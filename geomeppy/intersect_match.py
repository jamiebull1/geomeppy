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

from geomeppy.polygons import Polygon3D
from geomeppy.polygons import normalize_coords
from itertools import combinations
import itertools

from six.moves import zip_longest


def intersect_idf_surfaces(idf):
    """Intersect all surfaces in an IDF.
    
    Parameters
    ----------
    idf : IDF object
        The IDF.
    
    Returns
    -------
    IDF object
    
    """
    surfaces = getidfsurfaces(idf)
    """
    @TODO: Add the Polygon3D as a field for all EPlus building surfaces so we
    can call surface1.poly.intersect(surface2.poly) and avoid all the indexing
    in the code below.
    """ 
    surfaces = [[s, Polygon3D(s.coords)] for s in surfaces]
    ggr = idf.idfobjects['GLOBALGEOMETRYRULES']
    if ggr:
        clockwise = ggr[0].Vertex_Entry_Direction
    else:
        clockwise = 'counterclockwise'
    for s1, s2 in itertools.combinations(surfaces, 2):
        # get a point outside the zone, assuming surface is oriented correctly
        outside_s1 = s1[1].outside_point(clockwise)
        outside_s2 = s2[1].outside_point(clockwise)

        if not s1[1].is_coplanar(s2[1]):
            continue
        intersects = s1[1].intersect(s2[1])
        if not intersects:
            continue
        # create new surfaces for the intersects, and their reflections
        for i, intersect in enumerate(intersects, 1):
            """
            @TODO: Check the intersection touches an edge of both surfaces.
            If it doesn't touch an edge then we need to make subsurfaces as 
            doors in each surface, or split the subsurface.
            """
            if is_hole(s1[1], s2[1], intersect):
                # split surface with a hole in it, or make it a subsurface
                print("subsurface - continuing")
                continue
            else:
                # regular intersection
                new_name = "%s_%s_%i" % (s1[0].Name, 'new', i)
                new_inv_name = "%s_%s_%i" % (s2[0].Name, 'new', i)
                # intersection
                new = idf.copyidfobject(s1[0])
                new.Name = new_name
                set_coords(new, intersect, outside_s2, ggr)
                new.Outside_Boundary_Condition = "Surface"
                new.Outside_Boundary_Condition_Object = new_inv_name
                # inverted intersection
                new_inv = idf.copyidfobject(s2[0])
                new_inv.Name = new_inv_name
                new_inv.Outside_Boundary_Condition = "Surface"
                new_inv.Outside_Boundary_Condition_Object = new_name
                set_coords(new_inv,
                           intersect.invert_orientation(),
                           outside_s2, ggr)
        # edit the original two surfaces
        s1_new = s1[1].difference(s2[1])
        s2_new = s2[1].difference(s1[1])
        if s1_new:
            # modify the original s1[0]
            set_coords(s1[0], s1_new[0], outside_s1, ggr)
        if s2_new:
            # modify the original s2[0]
            set_coords(s2[0], s2_new[0], outside_s2, ggr)
    
    
def is_hole(s1, s2, intersect):
    """Identify if intersect is a hole in either of the surfaces.
    
    Check the intersection touches an edge of both surfaces. If it doesn't then
    it represents a hole in one of the surfaces, and this needs further
    processing into valid EnergyPlus surfaces.
    
    Parameters
    ----------
    s1 : Polygon3D
        The first surface.

    s2 : Polygon3D
        The second surface.

    intersect : Polygon3D
        The intersection between the two surfaces.
        
    Returns
    -------
    bool

    """
    s1_touches = any([c[0].is_collinear(c[1]) 
                      for c in itertools.product(s1.edges, intersect.edges)])
    s2_touches = any([c[0].is_collinear(c[1]) 
                      for c in itertools.product(s2.edges, intersect.edges)])

    return not all([s1_touches, s2_touches])

def test_is_hole():
    """Test if a surface represents a hole in one of the surfaces.
    """
    poly1 = Polygon3D([(0,4,0),(0,0,0),(4,0,0),(4,4,0)])
    poly2 = Polygon3D([(3,3,0),(3,1,0),(1,1,0),(1,3,0)])
    intersect = Polygon3D([(3,3,0),(1,3,0),(1,1,0),(3,1,0)])
    assert is_hole(poly1, poly2, intersect)

    poly1 = Polygon3D([(0,4,0),(0,0,0),(4,0,0),(4,4,0)])
    poly2 = Polygon3D([(3,3,0),(3,1,0),(0,1,0),(0,3,0)])
    intersect = Polygon3D([(3,3,0),(0,3,0),(0,1,0),(3,1,0)])
    assert not is_hole(poly1, poly2, intersect)


def set_coords(surface, poly, outside_pt, ggr=None):
    """Update the coordinates of a surface.
    
    This functions follows the GlobalGeometryRules of the IDF where available.
    
    Parameters
    ----------
    surface : EPBunch
        The surface to modify.
    coords : list
        The new coordinates.
    outside_pt : Point3D
        A point outside the zone the surface belongs to.
    ggr : EPBunch
        The section of the IDF that give rules for the order of vertices in a
        surface.
    
    """
    # make new_coords follow the GlobalGeometryRules
    poly = normalize_coords(poly, outside_pt, ggr)
    coords = [i for vertex in poly for i in vertex]
    # find the vertex fields
    n_vertices_index = surface.fieldnames.index('Number_of_Vertices')
    last_z = len(surface.obj)
    first_x = n_vertices_index + 1 # X of first coordinate
    vertex_fields = surface.fieldnames[first_x:last_z] # Z of final coordinate
    
    # set the vertex field values
    for field, x in zip_longest(vertex_fields, coords, fillvalue=""):
        surface[field] = x
    

def getidfsurfaces(idf):
    """Return all surfaces in an IDF.
    
    """
    surfaces = idf.idfobjects['BUILDINGSURFACE:DETAILED']
    return surfaces
