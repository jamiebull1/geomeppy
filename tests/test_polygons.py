"""Tests for polygons."""
from geomeppy.geom.polygons import break_polygons, Polygon2D, Polygon3D, Vector2D, Vector3D
from geomeppy.geom.segments import Segment
from geomeppy.utilities import almostequal


def test_polygon_repr():
    # type: () -> None
    s2D = Polygon2D([(0, 0), (2, 0), (2, 0), (0, 0)])  # vertical
    assert eval(repr(s2D)) == s2D
    
    s3D = Polygon3D([(0,0,0), (2,0,0), (2,2,0), (0,2,0)])  # vertical
    assert eval(repr(s3D)) == s3D


def test_equal_polygon():
    # type: () -> None
    poly1 = Polygon2D([(1, 0), (0, 0), (0, 1), (1, 1)])
    poly2 = Polygon2D([(1, 1), (1, 0), (0, 0), (0, 1)])
    assert poly1 == poly2
    
    poly1 = Polygon2D([(1, 0), (0, 0), (0, 1), (1, 1)])
    poly2 = Polygon2D(reversed([(1, 1), (1, 0), (0, 0), (0, 1)]))
    assert poly1 != poly2
    
    
def test_equal_polygon3D():
    # type: () -> None
    poly1 = Polygon2D([(1, 0, 0), (0, 0, 0), (0, 1, 0), (1, 1, 0)])
    poly2 = Polygon2D([(1, 1, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0)])
    assert poly1 == poly2
    
    poly1 = Polygon2D([(1, 0, 0), (0, 0, 0), (0, 1, 0), (1, 1, 0)])
    poly2 = Polygon2D(reversed([(1, 1, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0)]))
    assert poly1 != poly2
    
    
def test_polygon_index():
    # type: () -> None
    poly = Polygon3D([(0,4,0),(0,0,0),(4,0,0),(4,4,0)])
    assert poly[1] == Vector3D(0,0,0)
    assert poly.index(Vector3D(0,0,0)) == 1


def test_polygon_attributes():
    # type: () -> None
    poly2d = Polygon2D([(0, 0), (0, 1), (1, 1), (1, 0)])
    assert len(poly2d) == 4
    assert poly2d.xs == [0,0,1,1]
    assert poly2d.ys == [0,1,1,0] 
    assert poly2d.zs == [0,0,0,0]
    assert poly2d.vertices_list == [(0,0), (0,1), (1,1), (1,0)]
    assert poly2d.vertices == [Vector2D(*v) for v in poly2d]
    
    
def test_polygon3d_attributes():
    # type: () -> None
    poly3d = Polygon3D([(0,0,0), (0,1,1), (1,1,1), (1,0,0)])
    assert len(poly3d) == 4
    assert poly3d.xs == [0,0,1,1]
    assert poly3d.ys == [0,1,1,0] 
    assert poly3d.zs == [0,1,1,0]
    assert poly3d.vertices_list == [(0,0,0), (0,1,1), (1,1,1), (1,0,0)]
    assert poly3d.vertices == [Vector3D(*v) for v in poly3d]
    assert poly3d.distance == 0
    assert poly3d.is_horizontal is False
    assert almostequal(poly3d.normal_vector, [0.0, 0.70710678, -0.70710678])
    poly3d_2 = Polygon3D([(0,1,1), (0,2,2), (1,2,2), (1,1,1)])
    assert almostequal(poly3d_2.normal_vector, [0.0, 0.70710678, -0.70710678])
    assert poly3d_2.projection_axis == 1
    result = poly3d.is_coplanar(poly3d_2)
    assert result
    
    
def test_add_polygon_to_polygon():
    # type: () -> None
    # 2D
    poly1 = Polygon2D([(1, 0), (0, 0), (0, 1)])
    poly2 = Polygon2D([(1, 0), (1, 0), (1, 0)])
    expected = Polygon2D([(2, 0), (1, 0), (1, 1)])
    result = poly1 + poly2
    assert almostequal(result, expected)

    vector = Vector2D(1,0)    
    result = poly1 + vector
    assert almostequal(result, expected)
    
    vector = Vector3D(1,0,0)
    try:
        result = poly1 + vector  # should fail
        assert False
    except ValueError:
        pass
    # 3D
    poly1 = Polygon2D([(1, 0, 1), (0, 0, 1), (0, 1, 1)])
    poly2 = Polygon2D([(1, 0, 1), (1, 0, 1), (1, 0, 1)])
    expected = Polygon2D([(2, 0, 2), (1, 0, 2), (1, 1, 2)])
    result = poly1 + poly2
    assert almostequal(result, expected)

    vector = Vector3D(1,0,1)    
    result = poly1 + vector
    assert almostequal(result, expected)
    
    vector = Vector2D(1,0)
    try:
        result = poly1 + vector  # should fail
        assert False
    except ValueError:
        pass


def test_polygons_not_equal():
    # type: () -> None
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
    

def test_order_points():
    # type: () -> None
    polygon = Polygon3D([(0,0,0), (0,1,1), (1,1,1), (1,0,0)])
    starting_position = 'upperleftcorner'
    expected = Polygon3D([(1,1,1), (1,0,0), (0,0,0), (0,1,1)])
    result = polygon.order_points(starting_position)
    assert result == expected
    assert result[0] == expected[0]
    
    starting_position = 'lowerleftcorner'
    expected = Polygon3D([(1,0,0), (0,0,0), (0,1,1), (1,1,1)])
    result = polygon.order_points(starting_position)
    assert result == expected
    assert result[0] == expected[0]
    
    starting_position = 'lowerrightcorner'
    expected = Polygon3D([(0,0,0), (0,1,1), (1,1,1), (1,0,0)])
    result = polygon.order_points(starting_position)
    assert result == expected
    assert result[0] == expected[0]
    
    starting_position = 'upperrightcorner'
    expected = Polygon3D([(0,1,1), (1,1,1), (1,0,0), (0,0,0)])
    result = polygon.order_points(starting_position)
    assert result == expected
    assert result[0] == expected[0]


def test_bounding_box():
    # type: () -> None
    poly = Polygon2D([(0, 0), (0, 1), (1, 1), (1, 0)])
    poly3d = Polygon3D([(0,0,0), (0,1,1), (1,1,1), (1,0,0)])
    
    expected = Polygon2D([(1, 1, 1), (1, 0, 0), (0, 0, 0), (0, 1, 1)])

    result = poly3d.bounding_box
    assert almostequal(result, expected)


def test_reflect():
    # type: () -> None
    """
    Test that a polygon with inverted orientation is seen as coplanar with the
    original polygon, but not seen as equal.
    
    """
    poly3d = Polygon3D([(0,0,0), (0,1,1), (1,1,1), (1,0,0)])
    poly3d_inv = poly3d.invert_orientation()
    assert poly3d != poly3d_inv
    assert poly3d.is_coplanar(poly3d_inv)
    

def test_rotate():
    # type: () -> None
    """Test for rotating 3D polygons into 2D and back again."""
    # At the origin
    s1 = Polygon3D([(0,0,2), (2,0,2), (0,0,0)])  # vertical
    expected = Polygon2D([(0, 2), (2, 2), (0, 0)])
    # convert to 2D    
    result = s1.project_to_2D()
    assert result == expected
    
    # revert to 3D
    result = result.project_to_3D(s1)
    assert result == s1
    
    # Away from the origin
    s1 = Polygon3D([(1,0,2), (3,0,2), (1,0,0)])  # vertical
    expected = Polygon2D([(1, 2), (3, 2), (1, 0)])
    # convert to 2D    
    result = s1.project_to_2D()

    assert result == expected

    # revert to 3D
    result = result.project_to_3D(s1)
    assert result == s1

    # Away from the origin
    s1 = Polygon3D([(0,1,1), (2,2,0), (2,2,2), (0,1,2)])  # vertical
    expected = Polygon2D([(0.0, 1.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)])

    # convert to 2D    
    result = s1.project_to_2D()
    assert result == expected

    # revert to 3D
    result = result.project_to_3D(s1)
    assert result == s1


def test_union_2D_polys_single():
    # type: () -> None
    """Simplest test for union_2D_polys
    
    This has two squares in the horizontal plane which overlap in one place.
    Fails if the expected union shape is not returned.
    
    """
    # surface is already a flat plane with z == 0
    s1 = Polygon2D([(0, 2), (2, 2), (2, 0), (0, 0)])  # clockwise
    s2 = Polygon2D([(1, 3), (3, 3), (3, 1), (1, 1)])  # clockwise
    expected = [Polygon2D([(0, 0), (0, 2), (1, 2), (1, 3),
                           (3,3), (3,1), (2,1), (2,0)])]  # clockwise
    
    result = s1.union(s2)
    for res, exp in zip(result, expected):
        assert res == exp

    result = s2.union(s1)
    for res, exp in zip(result, expected):
        assert res == exp


def test_intersect_2D_polys_single():
    # type: () -> None
    """Simplest test for intersect_2D_polys
    
    This has two squares in the horizontal plane which overlap in one place.
    Fails if the expected overlapping shape is not returned.
    
    """
    # surface is already a flat plane with z == 0
    s1 = Polygon2D([(0, 2), (2, 2), (2, 0), (0, 0)])  # clockwise
    s2 = Polygon2D([(1, 3), (3, 3), (3, 1), (1, 1)])  # clockwise
    expected = [Polygon2D([(1, 2), (2, 2), (2, 1), (1, 1)])]  #clockwise
    
    result = s1.intersect(s2)
    for res, exp in zip(result, expected):
        assert res == exp

    result = s2.intersect(s1)
    for res, exp in zip(result, expected):
        assert res == exp


def test_difference_2D_polys_single():
    # type: () -> None
    """Simplest test for difference_2D_polys
    
    This has two squares in the horizontal plane which overlap in one place.
    Fails if the two original polygons do not have the intersection removed.
    
    """
    s1 = Polygon2D([(0, 2), (2, 2), (2, 0), (0, 0)])  # clockwise
    s2 = Polygon2D([(1, 3), (3, 3), (3, 1), (1, 1)])  # clockwise
    
    # clockwise
    ex_s1 = [Polygon2D([(0, 2), (1, 2), (1, 1), (2, 1), (2, 0), (0, 0)])]
    ex_s2 = [Polygon2D([(1, 3), (3, 3), (3, 1), (2, 1), (2, 2), (1, 2)])]
    expected = [ex_s1, ex_s2]

    result = [s1.difference(s2), s2.difference(s1)]
    assert result[0] == expected[0]
    assert result[1] == expected[1]


def test_union_3D_polys_single():
    # type: () -> None
    """Simplest test for union_3D_polys
    
    This has two squares in the horizontal plane which overlap in one place.
    Fails if the expected union shape is not returned.
    
    """
    # surface is already a flat plane with z == 0
    s1 = Polygon3D([(0,2,0), (2,2,0), (2,0,0), (0,0,0)])  # clockwise
    s2 = Polygon3D([(1,3,0), (3,3,0), (3,1,0), (1,1,0)])  # clockwise
    expected = [Polygon3D([(0,0,0), (0,2,0), (1,2,0), (1,3,0),
                           (3,3,0), (3,1,0), (2,1,0), (2,0,0)])]  # clockwise
    
    result = s1.union(s2)
    for res, exp in zip(result, expected):
        assert res == exp

    result = s2.union(s1)
    for res, exp in zip(result, expected):
        assert res == exp


def test_intersect_3D_polys_single():
    # type: () -> None
    """Simplest test for intersect_3D_polys
    
    This has two squares in the horizontal plane which overlap in one place.
    Fails if the expected overlapping shape is not returned.
    
    """
    # surface is already a flat plane with z == 0
    s1 = Polygon3D([(0,2,0), (2,2,0), (2,0,0), (0,0,0)])  # clockwise
    s2 = Polygon3D([(1,3,0), (3,3,0), (3,1,0), (1,1,0)])  # clockwise
    expected = [Polygon3D([(1,2,0), (2,2,0), (2,1,0), (1,1,0)])]  #clockwise
    result = s1.intersect(s2)
    for res, exp in zip(result, expected):
        assert res == exp


def test_difference_3D_polys_single():
    # type: () -> None
    """Simplest test for difference_3D_polys
    
    This has two squares in the horizontal plane which overlap in one place.
    Fails if the two original polygons do not have the intersection removed.
    
    """
    # surface is already a flat plane with z == 0
    s1 = Polygon3D([(0,2,0), (2,2,0), (2,0,0), (0,0,0)])  # clockwise
    s2 = Polygon3D([(1,3,0), (3,3,0), (3,1,0), (1,1,0)])  # clockwise
    
    # clockwise
    ex_s1 = [Polygon3D([(0,2,0), (1,2,0), (1,1,0), (2,1,0), (2,0,0), (0,0,0)])]
    ex_s2 = [Polygon3D([(1,3,0), (3,3,0), (3,1,0), (2,1,0), (2,2,0), (1,2,0)])]
    expected = [ex_s1, ex_s2]

    result = [s1.difference(s2), s2.difference(s1)]
    assert result[0] == expected[0]
    assert result[1] == expected[1]
    
    
def test_intersect_3D_polys_angled():
    # type: () -> None
    s1 = Polygon3D([(2.5,1.95,0.5), (2.5,1.95,0), (1.5,2.05,0), (1.5,2.05,0.5)])  # clockwise
    s2 = Polygon3D([(1,2.1,0.5), (1,2.1,0), (2,2,0), (2,2,0.5)])  # clockwise
    expected = [Polygon3D([(2.0, 2.0, 0.0), (1.5, 2.05, 0.0),
                           (1.5, 2.05, 0.5),(2.0, 2.0, 0.5)])]

    result = s1.intersect(s2)

    assert result == expected


def test_intersect_no_overlap():
    # type: () -> None
    # surfaces don't overlap
    s1 = Polygon3D([(0,2,0), (2,2,0), (2,0,0), (0,0,0)])  # clockwise
    s2 = Polygon3D([(2,3,0), (3,3,0), (3,1,0), (2,1,0)])  # clockwise
    expected = []  #clockwise
    result = s1.intersect(s2)
    assert result == expected


def test_difference_no_difference():
    # type: () -> None
    # surfaces don't overlap
    s1 = Polygon3D([(0,2,0), (2,2,0), (2,0,0), (0,0,0)])  # clockwise
    s2 = s1
    expected = []  #clockwise
    result = s1.difference(s2)
    assert result == expected


def test_intersect_3D_polys_multi():
    # type: () -> None
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
    result = s1.intersect(s2)
    
    for res, exp in zip(result, overlap):
        assert res == exp

    result = s1.intersect(s2)
    for res, exp in zip(result, overlap):
        assert res == exp

    result = s2.intersect(s1)
    for res, exp in zip(result, overlap):
        assert res == exp


def test_difference_3D_polys_multi():
    # type: () -> None
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
    result = [s1.difference(s2), s2.difference(s1)]
    
    for res, exp in zip(result, expected):
        assert len(res) == len(exp)
        for r, e  in zip(res, exp):
            assert r == e
            
    assert s1.difference(s2) == ex_s1
    assert s2.difference(s1) == ex_s2


def test_surface_normal():
    # type: () -> None
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
    # type: () -> None
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
    

def test_break_polygons():
    # type: () -> None
    poly = Polygon3D([(0,4,0),(0,0,0),(4,0,0),(4,4,0)])
    hole = Polygon3D([(1,3,0),(1.5,2,0),(1,1,0),(3,1,0),(3,3,0)])
    expected = [
        Polygon3D([(0,4,0),(0,0,0),(1,1,0),(1.5,2,0),(1,3,0)]),
        Polygon3D([(4,4,0),(0,4,0),(1,3,0),(3,3,0),(3,1,0),(1,1,0),(0,0,0),(4,0,0)])
        ]

    result = break_polygons(poly, hole)
    
    assert result[0] == expected[0]
    assert result[1] == expected[1]


def test_identify_inner_ring_polygons():
    # type: () -> None
    geom = [
        (u'POLYGON((528318.562 186087.89,528307.65 186095.1,528303.1 186088.15,528305.59 186086.5,528299.67 186077.17,'
         u'528300.85 186075.56,528295.35 186071.9,528294.401 186072.514,528292.8 186073.55,528285.8 186069.2,'
         u'528286 186066.5,528286.45 186065.85,528285.854 186065.438,528277.752 186059.839,528275.54 186058.31,'
         u'528273.93 186066.89,528273.76 186067.81,528273.45 186069.42,528269.73 186068.72,528267.91 186078.41,'
         u'528242.51 186073.65,528242.78 186072.209,528243.49 186068.42,528252.68 186058.13,528255.36 186043.87,'
         u'528261.22 186044.97,528266.75 186016.45,528269.25 186016.95,528271 186017.3,528271.2 186016.25,'
         u'528277.85 186017.5,528277.25 186020.4,528300.75 186024.85,528301 186023.65,528307.8 186024.95,'
         u'528307.7 186025.6,528311.5 186028.5,528310.85 186029.4,528316.7 186033.3,528320.15 186035.55,'
         u'528320.7 186034.95,528324.15 186037.25,528325 186036.95,528328.75 186042.7,528327.85 186043.3,'
         u'528340.6 186063.2,528342.65 186061.8,528347.25 186068.8,528347.3 186068.9,528318.562 186087.89),'
         u'(528306.281 186071.421,528312.36 186075.46,528314.06 186078.02,528314.7 186077.6,528315.98 186076.78,'
         u'528311.35 186069.56,528320.79 186063.52,528317.54 186058.45,528318.74 186057.68,528315.04 186051.9,'
         u'528318.42 186049.74,528317.5 186048.31,528319.21 186047.21,528317.9 186045.2,528316.6 186043.15,'
         u'528302.35 186063.6,528304.4 186065.05,528301.99 186068.57,528306.281 186071.421),'
         u'(528294.9 186046.92,528296.47 186044.6,528299.04 186040.78,528298.55 186040.45,528290.62 186038.77,'
         u'528289.3 186038.48,528288.33 186043.03,528289.65 186043.28,528287.66 186052.57,528285.16 186052.04,'
         u'528284.85 186053.5,528284.1 186054.8,528286.79 186056.63,528287.12 186056.86,528286.6 186057.65,'
         u'528287.3 186058.14,528289.45 186055,528291.3 186056.25,528296.85 186048.23,528294.9 186046.92),'
         u'(528274.89 186044.69,528277.99 186045.28,528276.9 186051.08,528276.98 186051.1,528278.3 186052,'
         u'528280.4 186053.44,528280.72 186052.98,528281.04 186051.33,528278.53 186050.86,528280.42 186041.51,'
         u'528282.23 186041.86,528283.17 186037.18,528276.65 186035.8,528274.89 186044.69))',
         7.7)]
    
    for item in geom:
        poly = Polygon3D([]).from_wkt(item[0])
#    view_polygons({'blue': [poly]})#, 'red': [interior]})
    

def test_point():
    # type: () -> None
    pt1 = Vector3D(0.0, 0.0, 0.0)
    pt2 = Vector3D(1.0, 1.0, 1.0)
    
    assert pt2 - pt1 == pt2
    assert pt1 - pt2 == Vector3D(-1,-1,-1)
    
    assert pt2 + pt2 == Vector3D(2,2,2)
           
           
def test_invert():
    # type: () -> None
    v = Vector3D(1, 2, 3)
    assert v.invert() == Vector3D(-1, -2, -3)
    

def test_set_length():
    # type: () -> None
    v = Vector3D(1, 1, 1)
    v.set_length(1)
    for i in v:
        assert almostequal(i, 0.57735026)


def test_normalize():
    # type: () -> None
    v = Vector3D(1, 1, 1)
    v.normalize()
    for i in v:
        assert almostequal(i, 0.57735026)


def test_on_poly_edge():
    # type: () -> None
    poly = Polygon3D([(0,4,0),(0,0,0),(4,0,0),(4,4,0)])
    edge1 = Segment(Vector3D(0,1,0), Vector3D(0,2,0))
    edge2 = Segment(Vector3D(1,1,0), Vector3D(1,2,0))
    assert edge1._on_poly_edge(poly)
    assert not edge2._on_poly_edge(poly)


def test_closest():
    # type: () -> None
    pt = Vector3D(0,0,0)
    poly = Polygon3D([(1,1,1), (2,2,3), (3,4,5)])
    assert pt.closest(poly) == Vector3D(1,1,1)
