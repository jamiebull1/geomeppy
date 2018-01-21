"""A collection of functions which act on surfaces or lists of surfaces."""
from collections import defaultdict
from itertools import combinations
from typing import Dict, List, Tuple, Union  # noqa
import warnings

from eppy.bunch_subclass import EpBunch  # noqa
from eppy.idf_msequence import Idf_MSequence  # noqa
from numpy import float64  # noqa

from .polygons import intersect, Polygon3D, unique
from .vectors import Vector2D, Vector3D  # noqa
from ..utilities import almostequal


def set_coords(surface,  # type: EpBunch
               coords,  # type: Union[List[Vector3D], List[Tuple[float, float, float]], Polygon3D]
               ggr  # type: Union[List, None, Idf_MSequence]
               ):
    # type: (...) -> None
    """Update the coordinates of a surface.

    :param surface: The surface to modify.
    :param coords: The new coordinates as lists of [x,y,z] lists.
    :param ggr: Global geometry rules.
    """
    poly = Polygon3D(coords)
    poly = poly.normalize_coords(ggr)
    coords = [i for vertex in poly for i in vertex]
    if len(coords) > 120:
        warnings.warn(
            'To create surfaces with >120 vertices, ensure you have customised your IDD before running EnergyPlus. '
            'https://unmethours.com/question/9343/energy-idf-parsing-error/?answer=9344#post-id-9344'
        )
    # find the vertex fields
    n_vertices_index = surface.objls.index('Number_of_Vertices')
    first_x = n_vertices_index + 1  # X of first coordinate
    surface.obj = surface.obj[:first_x]
    # set the vertex field values
    surface.fieldvalues.extend(coords)


def set_matched_surfaces(surface, matched):
    # type: (EpBunch, EpBunch) -> None
    """Set boundary conditions for two adjoining surfaces.

    :param surface: The first surface.
    :param matched: The second surface.
    """
    for s in [surface, matched]:
        s.Outside_Boundary_Condition = 'surface'
        s.Sun_Exposure = 'NoSun'
        s.Wind_Exposure = 'NoWind'
    surface.Outside_Boundary_Condition_Object = matched.Name
    matched.Outside_Boundary_Condition_Object = surface.Name


def set_unmatched_surface(surface, vector):
    # type: (EpBunch, Union[Vector2D, Vector3D]) -> None
    """Set boundary conditions for a surface which does not adjoin another one.

    :param surface: The surface.
    :param vector: The surface normal vector.
    """
    surface.View_Factor_to_Ground = 'autocalculate'
    poly = Polygon3D(surface.coords)
    if min(poly.zs) < 0 or all(z == 0 for z in poly.zs):
        # below ground or ground-adjacent surfaces
        surface.Outside_Boundary_Condition_Object = ''
        surface.Outside_Boundary_Condition = 'ground'
        surface.Sun_Exposure = 'NoSun'
        surface.Wind_Exposure = 'NoWind'
    else:
        surface.Outside_Boundary_Condition = 'outdoors'
        surface.Outside_Boundary_Condition_Object = ''
        surface.Wind_Exposure = 'WindExposed'
        if almostequal(vector, (0, 0, -1)):
            # downward facing surfaces
            surface.Sun_Exposure = 'NoSun'
        else:
            surface.Sun_Exposure = 'SunExposed'  # other external surfaces


def getidfplanes(surfaces):
    # type: (Idf_MSequence) -> Dict[float64, Dict[Union[Vector2D, Vector3D], List[EpBunch]]]
    """Fast access data structure for potentially matched surfaces.

    Get a data structure populated with all the surfaces in the IDF, keyed by their distance from the origin, and their
    normal vector.

    :param surfaces: List of all the surfaces.
    :returns: Mapping to look up IDF surfaces.
    """
    planes = {}  # type: Dict[float64, Dict[Union[Vector2D, Vector3D], List[EpBunch]]]
    for s in surfaces:
        poly = Polygon3D(s.coords)
        rounded_distance = round(poly.distance, 8)
        rounded_normal_vector = Vector3D(*[round(axis, 8)
                                           for axis in poly.normal_vector])
        planes.setdefault(rounded_distance,
                          {}).setdefault(rounded_normal_vector,
                                         []).append(s)
    return planes


def get_adjacencies(surfaces):
    # type: (Idf_MSequence) -> defaultdict
    """Create a dictionary mapping surfaces to their adjacent surfaces.

    :param surfaces: A mutable list of surfaces.
    :returns: Mapping of surfaces to adjacent surfaces.
    """
    adjacencies = defaultdict(list)  # type: defaultdict
    # find all adjacent surfaces
    for s1, s2 in combinations(surfaces, 2):
        adjacencies = populate_adjacencies(adjacencies, s1, s2)
    # make sure we have only unique surfaces
    for surface in adjacencies:
        adjacencies[surface] = unique(adjacencies[surface])

    return adjacencies


def populate_adjacencies(adjacencies, s1, s2):
    # type: (defaultdict, EpBunch, EpBunch) -> defaultdict
    """Update the adjacencies dict with any intersections between two surfaces.

    :param adjacencies: Dict to contain lists of adjacent surfaces.
    :param s1: Object representing an EnergyPlus surface.
    :param s2: Object representing an EnergyPlus surface.
    :returns: An updated dict of adjacencies.
    """
    poly1 = Polygon3D(s1.coords)
    poly2 = Polygon3D(s2.coords)
    if not almostequal(abs(poly1.distance), abs(poly2.distance), 4):
        return adjacencies
    if not almostequal(poly1.normal_vector, poly2.normal_vector, 4):
        if not almostequal(poly1.normal_vector, -poly2.normal_vector, 4):
            return adjacencies

    intersection = poly1.intersect(poly2)
    if intersection:
        new_surfaces = intersect(poly1, poly2)
        new_s1 = [s for s in new_surfaces
                  if almostequal(s.normal_vector, poly1.normal_vector, 4)]
        new_s2 = [s for s in new_surfaces
                  if almostequal(s.normal_vector, poly2.normal_vector, 4)]
        adjacencies[(s1.key, s1.Name)] += new_s1
        adjacencies[(s2.key, s2.Name)] += new_s2
    return adjacencies
