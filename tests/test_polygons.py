# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""pytest for polygons.py"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from geomeppy.polygons import Polygon
from geomeppy.polygons import Polygon3D
from geomeppy.polygons import Vector2D
from geomeppy.polygons import Vector3D
from geomeppy.polygons import difference_3D_polys
from geomeppy.polygons import intersect_3D_polys
from geomeppy.polygons import union_2D_polys
from geomeppy.polygons import union_3D_polys
from geomeppy.segments import Segment
from tests.pytest_helpers import almostequal


def test_polygon_repr():
    s2D = Polygon([(0,0), (2,0), (2,0), (0,0)])  # vertical
    assert eval(repr(s2D)) == s2D
    
    s3D = Polygon3D([(0,0,0), (2,0,0), (2,2,0), (0,2,0)])  # vertical
    assert eval(repr(s3D)) == s3D

def test_polygon_attributes():
    poly2d = Polygon([(0,0), (0,1), (1,1), (1,0)])
    assert len(poly2d) == 4
    assert poly2d.xs == [0,0,1,1]
    assert poly2d.ys == [0,1,1,0] 
    assert poly2d.zs == [0,0,0,0]
    assert poly2d.vertices_list == [(0,0), (0,1), (1,1), (1,0)]
    assert poly2d.vertices == [Vector2D(*v) for v in poly2d]
    
def test_polygon3d_attributes():
    poly3d = Polygon3D([(0,0,0), (0,1,1), (1,1,1), (1,0,0)])
    assert len(poly3d) == 4
    assert poly3d.xs == [0,0,1,1]
    assert poly3d.ys == [0,1,1,0] 
    assert poly3d.zs == [0,1,1,0]
    assert poly3d.vertices_list == [(0,0,0), (0,1,1), (1,1,1), (1,0,0)]
    assert poly3d.vertices == [Vector3D(*v) for v in poly3d]
    assert poly3d.distance == 0
    assert poly3d.is_horizontal == False
    assert poly3d.normal_vector == [0.0, 0.5, -0.5]
    poly3d_2 = Polygon3D([(0,1,1), (0,2,2), (1,2,2), (1,1,1)])
    assert poly3d_2.normal_vector == [0.0, 0.5, -0.5]
    assert poly3d_2.projection_axis == 1
    result = poly3d.is_coplanar(poly3d_2)
    assert result
    
def test_polygons_not_equal():
    """Test the check for equality between polygons.
    """
    # different normal vector
    poly3d = Polygon3D([(0,0,0), (0,1,1), (1,1,1), (1,0,0)])
    poly3d_2 = Polygon3D([(0,0,2), (0,1,2), (1,1,2), (1,0,2)])
    assert poly3d.normal_vector != poly3d_2.normal_vector
    assert poly3d != poly3d_2
    # different distance
    poly3d = Polygon3D([(0,0,0), (0,1,1), (1,1,1), (1,0,0)])
    poly3d_2 = Polygon3D([(0,1,2), (0,2,3), (1,2,3), (1,1,2)])
    assert poly3d.normal_vector == poly3d_2.normal_vector
    assert poly3d.distance != poly3d_2.distance
    assert poly3d != poly3d_2
    
def test_reflect():
    """
    Test that a polygon with inverted orientation is seen as coplanar with the
    original polygon, but not seen as equal.
    
    """
    poly3d = Polygon3D([(0,0,0), (0,1,1), (1,1,1), (1,0,0)])
    poly3d_inv = poly3d.invert_orientation()
    assert poly3d != poly3d_inv
    assert poly3d.is_coplanar(poly3d_inv)
    
def test_rotate():
    """Test for rotating 3D polygons into 2D and back again
    """
    # At the origin
    s1 = Polygon3D([(0,0,2), (2,0,2), (0,0,0)])  # vertical
    expected = Polygon([(0,2), (2,2), (0,0)])
    # convert to 2D    
    result = s1.project_to_2D()
    assert result == expected
    
    # revert to 3D
    result = result.project_to_3D(s1)
    assert result == s1
    
    # Away from the origin
    s1 = Polygon3D([(1,0,2), (3,0,2), (1,0,0)])  # vertical
    expected = Polygon([(1,2), (3,2), (1,0)])
    # convert to 2D    
    result = s1.project_to_2D()

    assert result == expected

    # revert to 3D
    result = result.project_to_3D(s1)
    assert result == s1

    # Away from the origin
    s1 = Polygon3D([(0,1,1), (2,2,0), (2,2,2), (0,1,2)])  # vertical
    expected = Polygon([(0.0, 1.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)])

    # convert to 2D    
    result = s1.project_to_2D()
    assert result == expected

    # revert to 3D
    result = result.project_to_3D(s1)
    assert result == s1


def test_union_2D_polys_single():
    """Simplest test for union_2D_polys
    
    This has two squares in the horizontal plane which overlap in one place.
    Fails if the expected union shape is not returned.
    
    """
    # surface is already a flat plane with z == 0
    s1 = Polygon([(0,2), (2,2), (2,0), (0,0)])  # clockwise
    s2 = Polygon([(1,3), (3,3), (3,1), (1,1)])  # clockwise
    expected = [Polygon(reversed([(0,0), (0,2), (1,2), (1,3),
                                  (3,3), (3,1), (2,1), (2,0)]))]  #counterclockwise
    
    result = union_2D_polys(s1, s2)
    for res, exp in zip(result, expected):
        assert res == exp

    result = s1.union(s2)
    assert res == exp

    result = s2.union(s1)
    assert res == exp


def test_intersect_2D_polys_single():
    """Simplest test for intersect_2D_polys
    
    This has two squares in the horizontal plane which overlap in one place.
    Fails if the expected overlapping shape is not returned.
    
    """
    # surface is already a flat plane with z == 0
    s1 = Polygon([(0,2), (2,2), (2,0), (0,0)])  # clockwise
    s2 = Polygon([(1,3), (3,3), (3,1), (1,1)])  # clockwise
    expected = [Polygon([(1,1), (2,1), (2,2), (1,2)])]  #clockwise
    
    result = s1.intersect(s2)
    for res, exp in zip(result, expected):
        assert res == exp

    result = s2.intersect(s1)
    for res, exp in zip(result, expected):
        assert res == exp


def test_difference_2D_polys_single():
    """Simplest test for difference_2D_polys
    
    This has two squares in the horizontal plane which overlap in one place.
    Fails if the two original polygons do not have the intersection removed.
    
    """
    s1 = Polygon([(0,2), (2,2), (2,0), (0,0)])  # clockwise
    s2 = Polygon([(1,3), (3,3), (3,1), (1,1)])  # clockwise
    
    # clockwise
    ex_s1 = [Polygon(reversed([(0,2), (1,2), (1,1), (2,1), (2,0), (0,0)]))]
    ex_s2 = [Polygon(reversed([(1,3), (3,3), (3,1), (2,1), (2,2), (1,2)]))]
    expected = [ex_s1, ex_s2]

    result = [s1.difference(s2), s2.difference(s1)]
    assert result[0] == expected[0]
    assert result[1] == expected[1]


def test_union_3D_polys_single():
    """Simplest test for union_3D_polys
    
    This has two squares in the horizontal plane which overlap in one place.
    Fails if the expected union shape is not returned.
    
    """
    # surface is already a flat plane with z == 0
    s1 = Polygon3D([(0,2,0), (2,2,0), (2,0,0), (0,0,0)])  # clockwise
    s2 = Polygon3D([(1,3,0), (3,3,0), (3,1,0), (1,1,0)])  # clockwise
    expected = [Polygon3D(reversed([(0,0,0), (0,2,0), (1,2,0), (1,3,0),
                           (3,3,0), (3,1,0), (2,1,0), (2,0,0)]))]  #counterclockwise
    
    result = union_3D_polys(s1, s2)
    for res, exp in zip(result, expected):
        assert res == exp

    result = s1.union(s2)
    assert res == exp

    result = s2.union(s1)
    assert res == exp


def test_intersect_3D_polys_single():
    """Simplest test for intersect_3D_polys
    
    This has two squares in the horizontal plane which overlap in one place.
    Fails if the expected overlapping shape is not returned.
    
    """
    # surface is already a flat plane with z == 0
    s1 = Polygon3D([(0,2,0), (2,2,0), (2,0,0), (0,0,0)])  # clockwise
    s2 = Polygon3D([(1,3,0), (3,3,0), (3,1,0), (1,1,0)])  # clockwise
    expected = [Polygon3D([(1,1,0), (2,1,0), (2,2,0), (1,2,0)])]  #clockwise
    
    result = intersect_3D_polys(s1, s2)
    for res, exp in zip(result, expected):
        assert res == exp


def test_difference_3D_polys_single():
    """Simplest test for difference_3D_polys
    
    This has two squares in the horizontal plane which overlap in one place.
    Fails if the two original polygons do not have the intersection removed.
    
    """
    # surface is already a flat plane with z == 0
    s1 = Polygon3D([(0,2,0), (2,2,0), (2,0,0), (0,0,0)])  # clockwise
    s2 = Polygon3D([(1,3,0), (3,3,0), (3,1,0), (1,1,0)])  # clockwise
    
    # clockwise
    ex_s1 = [Polygon3D(reversed([(0,2,0), (1,2,0), (1,1,0), (2,1,0), (2,0,0), (0,0,0)]))]
    ex_s2 = [Polygon3D(reversed([(1,3,0), (3,3,0), (3,1,0), (2,1,0), (2,2,0), (1,2,0)]))]
    expected = [ex_s1, ex_s2]

    result = [difference_3D_polys(s1, s2), difference_3D_polys(s2, s1)]
    assert result[0] == expected[0]
    assert result[1] == expected[1]
    
def test_intersect_3D_polys_angled():
    s1 = Polygon3D([(2.5,1.95,0.5), (2.5,1.95,0), (1.5,2.05,0), (1.5,2.05,0.5)])  # clockwise
    s2 = Polygon3D([(1,2.1,0.5), (1,2.1,0), (2,2,0), (2,2,0.5)])  # clockwise
    expected = [Polygon3D([(2.0, 2.0, 0.5), (1.5, 2.05, 0.5),
                           (1.5, 2.05, 0.0), (2.0, 2.0, 0.0)])]

    result = intersect_3D_polys(s1, s2)

    assert result == expected


def test_intersect_no_overlap():
    # surfaces don't overlap
    s1 = Polygon3D([(0,2,0), (2,2,0), (2,0,0), (0,0,0)])  # clockwise
    s2 = Polygon3D([(2,3,0), (3,3,0), (3,1,0), (2,1,0)])  # clockwise
    expected = False  #clockwise
    result = intersect_3D_polys(s1, s2)
    assert result == expected


def test_difference_no_difference():
    # surfaces don't overlap
    s1 = Polygon3D([(0,2,0), (2,2,0), (2,0,0), (0,0,0)])  # clockwise
    s2 = s1
    expected = False  #clockwise
    result = difference_3D_polys(s1, s2)
    assert result == expected


def test_intersect_3D_polys_multi():
    """Test for intersect_3D_polys with two overlapping regions
    
    This has two shapes in the horizontal plane which overlap in two places.
    Fails if the overlapping shapes are not returned as a new polygons.

    """    
    # surface is already a flat plane with z == 0
    s1 = Polygon3D([(0,0,0), (5,0,0), (5,2,0), (0,2,0)])  # counterclockwise
    s2 = Polygon3D([(1,1,0), (2,1,0), (2,2,0), (3,2,0),
                     (3,1,0), (4,1,0), (4,3,0), (1,3,0)])  # counterclockwise
    overlap = [Polygon3D([(1,1,0), (2,1,0), (2,2,0), (1,2,0)]),
               Polygon3D([(3,1,0), (4,1,0), (4,2,0), (3,2,0)])]
    
    ex_s1 = Polygon3D([(0,0,0), (5,0,0), (5,2,0), (4,2,0), (4,1,0), (3,1,0), 
                        (3,2,0), (2,2,0), (2,1,0), (1,1,0), (1,2,0), (0,2,0)])
    ex_s2 = Polygon3D([(1,2,0), (4,2,0), (4,3,0), (1,3,0)])

    expected = [ex_s1, ex_s2]
    expected.extend(overlap)
    result = intersect_3D_polys(s1, s2)
    
    for res, exp in zip(result, overlap):
        assert res == exp

    result = s1.intersect(s2)
    for res, exp in zip(result, overlap):
        assert res == exp

    result = s2.intersect(s1)
    for res, exp in zip(result, overlap):
        assert res == exp


def test_difference_3D_polys_multi():
    """Test for difference_3D_polys with two overlapping regions
    
    This has two shapes in the horizontal plane which overlap in two places.
    Fails if the overlapping shapes are not returned as a new polygons.

    """    
    # surface is already a flat plane with z == 0
    s1 = Polygon3D([(0,0,0), (5,0,0), (5,2,0), (0,2,0)])  # counterclockwise
    s2 = Polygon3D([(1,1,0), (2,1,0), (2,2,0), (3,2,0),
                     (3,1,0), (4,1,0), (4,3,0), (1,3,0)])  # counterclockwise
    
    ex_s1 = [Polygon3D([(0,0,0), (5,0,0), (5,2,0), (4,2,0), (4,1,0), (3,1,0), 
                        (3,2,0), (2,2,0), (2,1,0), (1,1,0), (1,2,0), (0,2,0)])]
    ex_s2 = [Polygon3D([(1,2,0), (4,2,0), (4,3,0), (1,3,0)])]

    expected = [ex_s1, ex_s2]
    result = [difference_3D_polys(s1, s2), difference_3D_polys(s2, s1)]
    
    for res, exp in zip(result, expected):
        assert len(res) == len(exp)
        for r, e  in zip(res, exp):
            assert r == e
            
    assert s1.difference(s2) == ex_s1
    assert s2.difference(s1) == ex_s2


def test_surface_normal():
    poly = Polygon3D([Vector3D(0.0, 0.0, 0.0),
                      Vector3D(1.0, 0.0, 0.0),
                      Vector3D(1.0, 1.0, 0.0),
                      Vector3D(0.0, 1.0, 0.0)])
    assert list(poly.normal_vector) == [0.0, 0.0, 1.0]  # for a horizontal surface

    poly = Polygon3D(reversed([Vector3D(0.0, 0.0, 0.0),
                      Vector3D(1.0, 0.0, 0.0),
                      Vector3D(1.0, 1.0, 0.0),
                      Vector3D(0.0, 1.0, 0.0)]))
    assert list(poly.normal_vector) == [0.0, 0.0, -1.0]  # for a horizontal surface

    poly = Polygon3D([Vector3D(0.0, 0.0, 0.0),
                      Vector3D(2.0, 1.0, 0.0),
                      Vector3D(4.0, 0.0, 0.0),
                      Vector3D(4.0, 3.0, 0.0),
                      Vector3D(2.0, 2.0, 0.0),
                      Vector3D(0.0, 3.0, 0.0)])
    assert list(poly.normal_vector) == [0.0, 0.0, 1.0]  # for a horizontal surface

    poly = Polygon3D(reversed([Vector3D(0.0, 0.0, 0.0),
                      Vector3D(2.0, 1.0, 0.0),
                      Vector3D(4.0, 0.0, 0.0),
                      Vector3D(4.0, 3.0, 0.0),
                      Vector3D(2.0, 2.0, 0.0),
                      Vector3D(0.0, 3.0, 0.0)]))
    assert list(poly.normal_vector) == [0.0, 0.0, -1.0]  # for a horizontal surface
    
    poly = Polygon3D([[ 1.,  1.1,  0.5],
                      [ 1.,  1.1,  0.],
                      [ 1.,  2.1,  0.],
                      [ 1.,  2.1,  0.5]])
    assert list(poly.normal_vector) == [1.0, 0.0, 0.0]  # for a horizontal surface

    
def test_surface_is_clockwise():
    """Test if a surface is clockwise as seen from a given point.
    """
    poly = Polygon3D(reversed([
        Vector3D(0.0, 0.0, 0.0),
        Vector3D(1.0, 0.0, 0.0),
        Vector3D(1.0, 1.0, 0.0),
        Vector3D(0.0, 1.0, 0.0)]))
    poly_inv = Polygon3D([
        Vector3D(0.0, 0.0, 0.0),
        Vector3D(1.0, 0.0, 0.0),
        Vector3D(1.0, 1.0, 0.0),
        Vector3D(0.0, 1.0, 0.0)])

    pt = Vector3D(0.5, 0.5, 1.0)  # point above the plane

    assert poly.is_clockwise(pt)
    assert not poly_inv.is_clockwise(pt)
    

def test_point():
    pt1 = Vector3D(0.0, 0.0, 0.0)
    pt2 = Vector3D(1.0, 1.0, 1.0)
    
    assert pt2 - pt1 == pt2
    assert pt1 - pt2 == Vector3D(-1,-1,-1)
    
    assert pt2 + pt2 == Vector3D(2,2,2)
           
           
def test_invert():
    v = Vector3D(1, 2, 3)
    assert v.invert() == Vector3D(-1, -2, -3)
    

def test_set_length():
    v = Vector3D(1, 1, 1)
    v.set_length(1)
    for i in v:
        assert almostequal(i, 0.57735026)


def test_normalize():
    v = Vector3D(1, 1, 1)
    v.normalize()
    for i in v:
        assert almostequal(i, 0.57735026)


def test_on_poly_edge():
    poly = Polygon3D([(0,4,0),(0,0,0),(4,0,0),(4,4,0)])
    edge1 = Segment(Vector3D(0,1,0), Vector3D(0,2,0))
    edge2 = Segment(Vector3D(1,1,0), Vector3D(1,2,0))
    assert edge1.on_poly_edge(poly)
    assert not edge2.on_poly_edge(poly)


