"""Intersect and match all surfaces in an IDF.
"""
from typing import List, Optional, Union  # noqa

from eppy.idf_msequence import Idf_MSequence  # noqa

from geomeppy.geom.polygons import Polygon3D
from geomeppy.geom.surfaces import (
    get_adjacencies, getidfplanes, set_coords, set_matched_surfaces, set_unmatched_surface,
)
from geomeppy.utilities import almostequal

if False: from ..idf import IDF  # noqa


def intersect_idf_surfaces(idf):
    # type: (IDF) -> None
    """Intersect all surfaces in an IDF.

    :param idf: The IDF.
    """
    surfaces = idf.getsurfaces()
    try:
        ggr = idf.idfobjects['GLOBALGEOMETRYRULES'][0]
    except IndexError:
        ggr = None
    # get all the intersected surfaces
    adjacencies = get_adjacencies(surfaces)
    for surface in adjacencies:
        key, name = surface
        new_surfaces = adjacencies[surface]
        old_obj = idf.getobject(key.upper(), name)
        for i, new_coords in enumerate(new_surfaces, 1):
            new = idf.copyidfobject(old_obj)
            new.Name = "%s_%i" % (name, i)
            set_coords(new, new_coords, ggr)
        idf.removeidfobject(old_obj)


def match_idf_surfaces(idf):
    # type: (IDF) -> None
    """Match all surfaces in an IDF.

    :param idf: The IDF.
    """
    surfaces = idf.getsurfaces()
    planes = getidfplanes(surfaces)
    for distance in planes:
        for vector in planes[distance]:
            surfaces = planes[distance][vector]
            matches = planes.get(-distance, {}).get(-vector, [])
            if not matches:
                # default set all the surfaces boundary conditions
                for s in surfaces:
                    set_unmatched_surface(s, vector)
            else:
                # check which are matches
                for s in surfaces:
                    for m in matches:
                        matched = False
                        poly1 = Polygon3D(s.coords)
                        poly2 = Polygon3D(m.coords)
                        if almostequal(poly1, poly2.invert_orientation()):
                            matched = True
                            set_matched_surfaces(s, m)
                            break
                    if not matched:
                        # unmatched surfaces
                        set_unmatched_surface(s, vector)
                        set_unmatched_surface(m, vector)
