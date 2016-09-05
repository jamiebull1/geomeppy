# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""Intersect and match all surfaces in an IDF.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
from itertools import combinations
from itertools import product

from geomeppy.polygons import Polygon3D
from geomeppy.polygons import break_polygons
from geomeppy.vectors import Vector3D
from geomeppy.utilities import almostequal

from six.moves import zip_longest


def match_idf_surfaces(idf):
    """Match all surfaces in an IDF.
    
    Parameters
    ----------
    idf : IDF object
        The IDF.
    
    """
    surfaces = getidfsurfaces(idf)
    for s1 in surfaces:
        poly1 = Polygon3D(s1.coords)
        s1.View_Factor_to_Ground = 'autocalculate'
        for s2 in surfaces:
            if s1 is s2:
                continue
            poly2 = Polygon3D(s2.coords)
            if poly1 == poly2.invert_orientation():
                # matched surfaces
                s1.Outside_Boundary_Condition = 'surface'
                s1.Outside_Boundary_Condition_Object = s2.Name
                s1.Sun_Exposure = 'NoSun'
                s1.Wind_Exposure = 'NoWind'
                break
            elif min(poly1.zs) < 0 or all(z == 0 for z in poly1.zs):
                # below ground or ground-adjacent surfaces
                s1.Outside_Boundary_Condition_Object = ''
                s1.Outside_Boundary_Condition = 'ground'
                s1.Sun_Exposure = 'NoSun'
                s1.Wind_Exposure = 'NoWind'
            else:
                # outside surfaces
                s1.Outside_Boundary_Condition = 'outdoors'
                s1.Outside_Boundary_Condition_Object = ''
                s1.Wind_Exposure = 'WindExposed'
                if almostequal(poly1.normal_vector, Vector3D(0.0, 0.0, -1.0)):
                    # downward facing surfaces
                    s1.Sun_Exposure = 'NoSun'
                else:
                    # other external surfaces
                    s1.Sun_Exposure = 'SunExposed'

            
def intersect_idf_surfaces(idf):
    """Intersect all surfaces in an IDF.
    
    Parameters
    ----------
    idf : IDF object
        The IDF.
    
    """
    surfaces = getidfsurfaces(idf)
    ggr = idf.idfobjects['GLOBALGEOMETRYRULES']
    # get all the intersected surfaces
    adjacencies = get_adjacencies(surfaces)
    for surface in adjacencies:
        key, name = surface
        new_surfaces = adjacencies[surface][0]
        old_obj = idf.getobject(key.upper(), name)
        for i, new_coords in enumerate(new_surfaces, 1):
            new = idf.copyidfobject(old_obj)
            new.Name = "%s_%i" % (name, i)
            set_coords(new, new_coords, ggr)
        idf.removeidfobject(old_obj)    


def get_adjacencies(surfaces):
    """Create a dictionary mapping surfaces to their adjacent surfaces.
    
    Parameters
    ----------
    surfaces : IdfMSequence
        A mutable list of surfaces.
    
    Returns
    -------
    dict
    
    """
    adjacencies = defaultdict(list)
    # find all adjacent surfaces
    for s1, s2 in combinations(surfaces, 2):
        adjacencies = populate_adjacencies(adjacencies, s1, s2)
    # make sure we have only unique surfaces
    for surface in adjacencies:
        adjacencies[surface] = unique(adjacencies[surface])

    return adjacencies

def populate_adjacencies(adjacencies, s1, s2):
    """Update the adjacencies dict with any intersections between two surfaces.
    
    Parameters
    ----------
    adjacencies : dict
        Dict to contain lists of adjacent surfaces.
    s1 : EPBunch
        Object representing an EnergyPlus surface.
    s2 : EPBunch
        Object representing an EnergyPlus surface.
    
    Returns
    -------
    dict
    
    """
    poly1 = Polygon3D(s1.coords)
    poly2 = Polygon3D(s2.coords)
    intersection = poly1.intersect(poly2)
    if intersection:
        new_surfaces = intersect(poly1, poly2)
        new_s1 = [s for s in new_surfaces 
                  if almostequal(s.normal_vector, poly1.normal_vector)]
        new_s2 = [s for s in new_surfaces 
                  if almostequal(s.normal_vector, poly2.normal_vector)]
        adjacencies[(s1.key, s1.Name)] += new_s1
        adjacencies[(s2.key, s2.Name)] += new_s2
    return adjacencies


def intersect(poly1, poly2):
    """Calculate the polygons to represent the intersection of two polygons.
    
    Parameters
    ----------
    poly1 : Polygon3D
        The first polygon.
    poly2 : Polygon3D
        The second polygon.
    
    Returns
    -------
    list
        A list of unique polygons.
        
    """
    polys = []
    polys.extend(poly1.intersect(poly2))
    polys.extend(poly2.intersect(poly1))
    if is_hole(poly1, poly2):
        polys.extend(break_polygons(poly1, poly2))
    elif is_hole(poly2, poly1):
        polys.extend(break_polygons(poly2, poly1))
    else:
        polys.extend(poly1.difference(poly2))
        polys.extend(poly2.difference(poly1))
    polys = unique(*polys)
    return polys


def unique(*polys):
    """Make a unique set of polygons.
    
    Parameters
    ----------
    *polys : 
    
    Returns
    -------
    list
    
    """
    result = []
    for poly in polys:
        if poly not in result:
            result.append(poly)
    return result


def is_hole(surface, possible_hole):
    """Identify if an intersection is a hole in the surface.
    
    Check the intersection touches an edge of the surface. If it doesn't then
    it represents a hole, and this needs further processing into valid
    EnergyPlus surfaces.
    
    Parameters
    ----------
    surface : Polygon3D
        The first surface.

    possible_hole : Polygon3D
        The intersection into the surface.
        
    Returns
    -------
    bool

    """
    if surface.area < possible_hole.area:
        return False
    collinear_edges = (edges[0].is_collinear(edges[1]) 
                       for edges in product(surface.edges, possible_hole.edges))
    return not any(collinear_edges)


def set_coords(surface, coords, ggr):
    """Update the coordinates of a surface.
      
    Parameters
    ----------
    surface : EPBunch
        The surface to modify.
    coords : list
        The new coordinates as lists of [x,y,z] lists.
    ggr : EpBunch
        Global geometry rules.

    """
    poly = Polygon3D(coords)
    poly = poly.normalize_coords(ggr)
    coords = [i for vertex in poly for i in vertex]
    # find the vertex fields
    n_vertices_index = surface.objls.index('Number_of_Vertices')
    first_x = n_vertices_index + 1 # X of first coordinate
    last_z = max(len(surface.obj), first_x + len(coords)) # Z of final coordinate
    vertex_fields = surface.objls[first_x:last_z]
    # set the vertex field values
    for field, x in zip_longest(vertex_fields, coords, fillvalue=""):
        try:
            surface[field] = x
        except:
            pass
            

def getidfsurfaces(idf, surface_type=None):
    """Return all surfaces in an IDF.
    
    Parameters
    ----------
    idf : IDF object
        The IDF to search.
    surface_type : str, optional
        A surface type to specify. Default is None, which returns all surfaces.
        
    """
    surfaces = idf.idfobjects['BUILDINGSURFACE:DETAILED']
    if surface_type:
        surfaces = [s for s in surfaces if s.Surface_type == surface_type]
    return surfaces
