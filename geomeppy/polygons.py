# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""
Heavy lifting geometry for IDF surfaces.

PyClipper is used for clipping.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import MutableSequence
from itertools import product

from eppy.geometry.surface import area
from geomeppy.segments import Segment
from geomeppy.transformations import align_face
from geomeppy.transformations import invert_align_face
from geomeppy.utilities import almostequal
from geomeppy.vectors import Vector2D
from geomeppy.vectors import Vector3D
from geomeppy.vectors import normalise_vector
from shapely import wkt

import numpy as np
import pyclipper as pc


class Polygon(MutableSequence):
    """Two-dimensional polygon."""
    n_dims = 2

    def __init__(self, vertices):
        super(Polygon, self).__init__()
        self.vertices = [Vector2D(*v) for v in vertices]
    
    def __repr__(self):
        class_name = type(self).__name__
        return '{}({!r})'.format(class_name, self.vertices)

    def __len__(self):
        return len(self.vertices)
            
    def __delitem__(self, key):
        del self.vertices[key]
    
    def __getitem__(self, key):
        return self.vertices[key]
    
    def __setitem__(self, key, value):
        self.vertices[key] = value

    def __eq__(self, other):
        if self.__dict__ == other.__dict__:  # try the simple case first
            return True
        else:  # also cover same shape in different rotation
            if self.difference(other):
                return False
            if self.normal_vector == other.normal_vector:
                return True
        return False
    
    def __add__(self, other):
        if len(self) == len(other) and hasattr(other[0], '__len__'):
            # add together two equal polygons
            vertices = [v1 + v2 for v1, v2 in zip(self, other)]
        elif len(self[0]) == len(other):
            # translate by a vector
            vertices = [v + other for v in self]
        else:
            raise ValueError("Incompatible objects: %s + %s" % (self, other))
        return self.__class__(vertices)
    
    def __sub__(self, other):
        if len(self) == len(other) and hasattr(other[0], '__len__'):
            # add together two equal polygons
            vertices = [v1 - v2 for v1, v2 in zip(self, other)]
        elif len(self[0]) == len(other):
            # translate by a vector
            vertices = [v - other for v in self]
        else:
            raise ValueError("Incompatible objects: %s + %s" % (self, other))
        return self.__class__(vertices)
    
    def from_wkt(self, wkt_poly):
        """Convert a wkt representation of a polygon to GeomEppy.
        
        This also accounts for the possible presence of inner rings by linking
        them to the outer ring.
        
        Parameters
        ----------
        wkt_poly : str
            A text representation of a polygon in well known text (wkt) format.
        
        Returns
        -------
        Polygon3D
        
        """
        poly = wkt.loads(wkt_poly)
        exterior = Polygon3D(poly.exterior.coords)
        if poly.interiors:
            # make the exterior into a geomeppy poly
            for inner_ring in poly.interiors:
                # make the interior into a geomeppy poly
                interior = Polygon3D(inner_ring.coords)
                # find the nearest points on the exterior and interior
                links = product(interior, exterior)
                links = sorted(links, key=lambda x: distance(x[0], x[1]))
                on_interior = links[0][0]
                on_exterior = links[0][1]
                # join them up
                exterior = Polygon3D(exterior[exterior.index(on_exterior):] + 
                                     exterior[:exterior.index(on_exterior) + 1])
                interior = Polygon3D(interior[interior.index(on_interior):] + 
                                     interior[:interior.index(on_interior) + 1])
                exterior = Polygon3D(exterior[:] + interior[:])
        
        return exterior
    
    @property
    def normal_vector(self):
        as_3d = Polygon3D((v.x, v.y, 0) for v in self)
        return as_3d.normal_vector
    
    @property
    def bounding_box(self):
        aligned = align_face(self)
        top_left = Vector3D(min(aligned.xs), max(aligned.ys), max(aligned.zs))
        bottom_left = Vector3D(min(aligned.xs), min(aligned.ys), min(aligned.zs))
        bottom_right = Vector3D(max(aligned.xs), min(aligned.ys), min(aligned.zs))
        top_right = Vector3D(max(aligned.xs), max(aligned.ys), max(aligned.zs))
        
        bbox = Polygon3D([top_left, bottom_left, bottom_right, top_right])
        return invert_align_face(self, bbox)
        
    def insert(self, key, value):
        self.vertices.insert(key, value)
                
    @property
    def points_matrix(self):
        """[[x1, x2,... xn]
            [y1, y2,... yn]
            [z1, z2,... zn]  # all 0 for 2D polygon
        """
        points = np.zeros((len(self.vertices), self.n_dims))
        for i, v in enumerate(self.vertices):
            points[i,:] = pt_to_array(v, dims=self.n_dims)
        return points
    
    @property
    def edges(self):
        """A list of edges represented as Segment objects.
        """
        vertices = self.vertices
        edges = [Segment(vertices[i], vertices[(i+1) % len(self)])
                for i in range(len(self))]
        return edges
    
    @property
    def xs(self):
        return [pt.x for pt in self.vertices]

    @property
    def ys(self):
        return [pt.y for pt in self.vertices]
   
    @property
    def zs(self):
        return [0.0] * len(self.vertices)
   
    @property
    def vertices_list(self):
        """A list of the vertices in the format required by pyclipper.
        
        Returns
        -------
        list of tuples
            Like [(x1, y1), (x2, y2),... (xn, yn)].
        
        """
        return [pt_to_tuple(pt, dims=self.n_dims) for pt in self.vertices]
    
    @property
    def area(self):
        return area(self)
    
    def invert_orientation(self):
        """Reverse the order of the vertices.
        
        This is to create a matching surface, e.g. the other side of a wall.
        
        Returns
        -------
        Polygon3D
        
        """
        return self.__class__(reversed(self.vertices))
        
    def project_to_3D(self, example3d):
        """Project the 2D polygon rotated into 3D space.
        
        This is used to return a previously rotated 3D polygon back to its
        original orientation, or to to put polygons generated from pyclipper
        into the desired orientation.
        
        Parameters
        ----------
        example3D : Polygon3D
            A 3D polygon in the desired plane.
                
        Returns
        -------
        Polygon3D
        
        """
        points = self.points_matrix
        proj_axis = example3d.projection_axis
        a = example3d.distance
        v = example3d.normal_vector
        projected_points = project_to_3D(points, proj_axis, a, v)
        return Polygon3D(projected_points)
    
    def union(self, poly):
        """Union with another 2D polygon.
        
        Parameters
        ----------
        poly : Polygon
            The clip polygon.

        Returns
        -------
        list
        
        """
        return union_2D_polys(self, poly)
        
    def intersect(self, poly):
        """Intersect with another 2D polygon.
        
        Parameters
        ----------
        poly : Polygon
            The clip polygon.

        Returns
        -------
        list or False
            False if no intersection, otherwise a list of lists of 2D
            coordinates representing each intersection.
        
        """
        return intersect_2D_polys(self, poly)
        
    def difference(self, poly):
        """Intersect with another 2D polygon.
        
        Parameters
        ----------
        poly : Polygon
            The clip polygon.

        Returns
        -------
        list or False
            False if no intersection, otherwise a list of lists of 2D
            coordinates representing each difference.
        
        """
        return difference_2D_polys(self, poly)

def distance(pt1, pt2):
    direction = pt1 - pt2
    return sum(x ** 2 for x in direction)
    
    
def break_polygons(poly, hole):
    """Break up a surface with a hole in it.
    
    This produces two surfaces, neither of which have a hole in them.
    
    Parameters
    ----------
    poly : Polygon3D
        The surface with a hole in.
    hole : Polygon3D
        The hole.
    
    Returns
    -------
    list
        Two Polygon3D objects.
        
    """
    # take the two closest points on the surface perimeter
    links = product(poly, hole)
    links = sorted(links, key=lambda x: distance(x[0], x[1]))

    first_on_poly = links[0][0]
    last_on_poly = links[1][0]

    first_on_hole = links[1][1]
    last_on_hole = links[0][1]

    coords = poly[:] + poly[:]  # a double loop
    section_on_poly = []
    for item in coords:
        if item == first_on_poly:
            section_on_poly.append(item)
        elif section_on_poly:
            section_on_poly.append(item)
            if item == last_on_poly:
                break

    coords = reversed(hole[:] + hole[:])  # a double loop
    section_on_hole = []
    for item in coords:
        if item == first_on_hole:
            section_on_hole.append(item)
        elif section_on_hole:
            section_on_hole.append(item)
            if item == last_on_hole:
                break    

    new_poly = section_on_poly + section_on_hole
        
    new_poly = Polygon3D(new_poly)
    union = hole.union(new_poly)
    union = union[0]
    new_poly2 = poly.difference(union)[0]
    if not almostequal(new_poly.normal_vector, poly.normal_vector):
        print("inverting 1")
        new_poly = new_poly.invert_orientation()
    if not almostequal(new_poly2.normal_vector, poly.normal_vector):
        print("inverting 2")
        new_poly2 = new_poly2.invert_orientation()
#    view_polygons({'blue': [new_poly], 'red': [hole]})
#    view_polygons({'blue': [new_poly, new_poly2], 'red': [hole]})
    
    return [new_poly, new_poly2]
    
    
def prep_2D_polys(poly1, poly2):
    """Prepare two 2D polygons for clipping operations.
    
    Parameters
    ----------
    poly1 : Polygon
        The subject polygon.
    poly2 : Polygon
        The clip polygon.
    
    Returns
    -------
    Pyclipper object
    
    """
    s1 = pc.scale_to_clipper(poly1.vertices_list)
    s2 = pc.scale_to_clipper(poly2.vertices_list)
    clipper = pc.Pyclipper()
    clipper.AddPath(s1, poly_type=pc.PT_SUBJECT, closed=True)
    clipper.AddPath(s2, poly_type=pc.PT_CLIP, closed=True)
    return clipper


def union_2D_polys(poly1, poly2):
    """Union of two 2D polygons.
    
    Find the combined shape of poly1 and poly2.
    
    Parameters
    ----------
    poly1 : Polygon
        The subject polygon.
    poly2 : Polygon
        The clip polygon.
    
    Returns
    -------
    list or False
        False if no intersection, otherwise a list of lists of 2D coordinates
        representing each intersection.
        
    """
    clipper = prep_2D_polys(poly1, poly2)        
    intersections = clipper.Execute(
        pc.CT_UNION, pc.PFT_NONZERO, pc.PFT_NONZERO)
    polys = process_clipped_2D_polys(intersections)
    results = []
    for poly in polys:
        if poly.normal_vector == poly1.normal_vector:
            results.append(poly)
        else:
            results.append(poly.invert_orientation())

    return results


def intersect_2D_polys(poly1, poly2):
    """Intersect two 2D polygons.
    
    Find the area/s that poly1 shares with poly2.
    
    Parameters
    ----------
    poly1 : Polygon
        The subject polygon.
    poly2 : Polygon
        The clip polygon.
    
    Returns
    -------
    list or False
        False if no intersection, otherwise a list of lists of 2D coordinates
        representing each intersection.
        
    """
    clipper = prep_2D_polys(poly1, poly2)        
    intersections = clipper.Execute(
        pc.CT_INTERSECTION, pc.PFT_NONZERO, pc.PFT_NONZERO)
    polys = process_clipped_2D_polys(intersections)
    results = []
    for poly in polys:
        if poly.normal_vector == poly1.normal_vector:
            results.append(poly)
        else:
            results.append(poly.invert_orientation())

    return results


def difference_2D_polys(poly1, poly2):
    """Difference from two 2D polygons.
    
    Equivalent to subtracting poly2 from poly1.
    
    Parameters
    ----------
    poly1 : Polygon
        The subject polygon.
    poly2 : Polygon
        The clip polygon.
    
    Returns
    -------
    list or False
        False if no difference, otherwise a list of lists of 2D coordinates
        representing each difference.
        
    """
    clipper = prep_2D_polys(poly1, poly2)        
    differences = clipper.Execute(
        pc.CT_DIFFERENCE, pc.PFT_NONZERO, pc.PFT_NONZERO)
    polys = process_clipped_2D_polys(differences)
    results = []
    for poly in polys:
        if poly.normal_vector == poly1.normal_vector:
            results.append(poly)
        else:
            results.append(poly.invert_orientation())

    return results


def process_clipped_2D_polys(results):
    """Process and return the results of a clipping operation.
    
    Parameters
    ----------
    results : list
        A list of results, potentially empty if the operation found no
        interactions between polygons.
        
    Returns
    -------
    list or False
        False if no intersection, otherwise a list of lists of 2D coordinates
        representing each intersection.
        
    """
    if results:
        results = [pc.scale_from_clipper(r) for r in results]
        return [Polygon(r) for r in results]
    else:
        return []
        

class Polygon3D(Polygon):
    """Three-dimensional polygon."""
    n_dims = 3

    def __init__(self, vertices):
        try:
            self.vertices = [Vector3D(*v) for v in vertices]
        except TypeError:
            self.vertices = vertices

    def __eq__(self, other):
        # check they're in the same plane
        if not almostequal(self.normal_vector, other.normal_vector):
            return False
        if not almostequal(self.distance, other.distance):
            return False
        # if they are in the same plane, check they completely overlap in 2D
        return (self.project_to_2D() == other.project_to_2D())
    
    @property
    def zs(self):
        return [pt.z for pt in self.vertices]

    @property
    def normal_vector(self):
        """Vector perpendicular to the polygon in the outward direction.
        
        Uses Newell's Method.
        
        Returns
        -------
        Vector3D

        """
        return Vector3D(*normal_vector(self.vertices))

    @property
    def distance(self):
        """
        A number where v[0] * x + v[1] * y + v[2] * z = a is the equation of
        the plane containing the polygon (where v is the polygon normal vector).
        
        Returns
        -------
        float
        
        """
        v = self.normal_vector
        pt = self.points_matrix[0]  # arbitrary point in the polygon
        d = np.dot(v, pt)
        return d
    
    @property
    def projection_axis(self):
        """Return an axis which will not lead to degenerate surface.
        
        Returns
        -------
        int
        
        """
        proj_axis = max(range(3), key=lambda i: abs(self.normal_vector[i]))
        return proj_axis
    
    @property
    def is_horizontal(self):
        """Check if polygon is in the xy plane.
        
        Returns
        -------
        bool
        
        """
        return np.array(self.zs).std() < 1e-8
    
    def is_clockwise(self, viewpoint):
        """Check if vertices are ordered clockwise
        
        This function checks the vertices as seen from the viewpoint.
        
        Parameters
        ----------
        viewpoint : Vector3D
        
        Returns
        -------
        bool
        
        """
        arbitrary_pt = self.vertices[0]
        v = arbitrary_pt - viewpoint
        n = self.normal_vector
        sign = np.dot(v, n)
        return sign > 0
    
    def is_coplanar(self, other):
        """Check if polygon is in the same plane as another polygon.
        
        This includes the same plane but opposite orientation.
        
        Parameters
        ----------
        other : Polygon3D
            Another polygon.
        
        Returns
        -------
        bool
        
        """
        n1 = self.normal_vector
        n2 = other.normal_vector
        d1 = self.distance
        d2 = other.distance
        
        if (almostequal(n1, n2) and almostequal(d1, d2)):
            return True
        elif (almostequal(n1, -n2) and almostequal(d1, -d2)):
            return True
        else:
            return False

    @property
    def centroid(self):
        """The centroid of a polygon.
        
        Returns
        -------
        Vector3D
        
        """
        return Vector3D(
            sum(self.xs) / len(self),
            sum(self.ys) / len(self),
            sum(self.zs) / len(self))
    
    def outside_point(self, entry_direction='counterclockwise'):
        """Return a point outside the zone to which the surface belongs.
        
        The point will be outside the zone, respecting the global geometry rules
        for vertex entry direction.
        
        Parameters
        ----------
        entry_direction : str
            Either "clockwise" or "counterclockwise", as seen from outside the
            space.
        
        Returns
        -------
        Vector3D
        
        """
        entry_direction = entry_direction.lower()
        if entry_direction == 'clockwise':
            inside = self.vertices[0] - self.normal_vector
        elif entry_direction == 'counterclockwise':
            inside = self.vertices[0] + self.normal_vector
        else:
            raise ValueError("invalid value for entry_direction '%s'" % 
                             entry_direction)
    
        return inside
    
    def order_points(self, starting_position):
        """Reorder the vertices based on a starting position rule.
        
        Parameters
        ----------
        starting_position : str
            The string that defines vertex starting position in EnergyPlus.
        
        Returns
        -------
        Polygon3D
        
        """
        if starting_position == 'upperleftcorner':
            bbox_corner = self.bounding_box[0]
        elif starting_position == 'lowerleftcorner':
            bbox_corner = self.bounding_box[1]
        elif starting_position == 'lowerrightcorner':
            bbox_corner = self.bounding_box[2]
        elif starting_position == 'upperrightcorner':
            bbox_corner = self.bounding_box[3]
        else:
            raise ValueError(
                '%s is not a valid starting position' % starting_position)
        start_index = self.index(bbox_corner.closest(self))
        new_vertices = [self[(start_index + i) % len(self)]
                        for i in range(len(self))]

        return Polygon3D(new_vertices)
    
    def project_to_2D(self):
        """Project the 3D polygon into 2D space.
        
        This is so that we can perform operations on it using pyclipper library.
        
        Project onto either the xy, yz, or xz plane. (We choose the one that
        avoids degenerate configurations, which is the purpose of proj_axis.)
        
        Returns
        -------
        Polygon3D
        
        """        
        points = self.points_matrix
        projected_points = project_to_2D(points, self.projection_axis)
        
        return Polygon([pt[:2] for pt in projected_points])
    
    def union(self, poly):
        """Union with another 3D polygon.
        
        Parameters
        ----------
        poly : Polygon3D
            The clip polygon.

        Returns
        -------
        list or False
            False if no union, otherwise a list of lists of Polygon3D
            objects representing each union.
        
        """
        return union_3D_polys(self, poly)
        
    def intersect(self, poly):
        """Intersect with another 3D polygon.
        
        Parameters
        ----------
        poly : Polygon3D
            The clip polygon.

        Returns
        -------
        list or False
            False if no intersection, otherwise a list of lists of Polygon3D
            objects representing each intersection.
        
        """
        return intersect_3D_polys(self, poly)
        
    def difference(self, poly):
        """Difference from another 3D polygon.
        
        Parameters
        ----------
        poly : Polygon3D
            The clip polygon.

        Returns
        -------
        list or False
            False if no difference, otherwise a list of lists of Polygon3D
            objects representing each intersection.
        
        """
        return difference_3D_polys(self, poly)
    
    def normalize_coords(self, ggr):
        """Order points, respecting the global geometry rules
        
        Parameters
        ----------
        ggr : EpPBunch
            GlobalGeometryRules object.
        
        Returns
        -------
        Polygon3D
        
        """
        try:
            entry_direction = ggr.Vertex_Entry_Direction
        except AttributeError:
            entry_direction = 'counterclockwise'            
        outside_point = self.outside_point(entry_direction)
        return normalize_coords(self, outside_point, ggr)

    
def normal_vector(poly):
    """Return the unit normal vector of a polygon.
    
    We use Newell's Method since the cross-product of two edge vectors is not
    valid for concave polygons.
    https://www.opengl.org/wiki/Calculating_a_Surface_Normal#Newell.27s_Method
    
    Parameters
    ----------
    
    """
    n = [0.0, 0.0, 0.0]

    for i, v_curr in enumerate(poly):
        v_next = poly[(i+1) % len(poly)]
        n[0] += (v_curr.y - v_next.y) * (v_curr.z + v_next.z)
        n[1] += (v_curr.z - v_next.z) * (v_curr.x + v_next.x)
        n[2] += (v_curr.x - v_next.x) * (v_curr.y + v_next.y)
    
    return normalise_vector(n)


def prep_3D_polys(poly1, poly2):
    """Prepare two 3D polygons for clipping operations.
    
    Parameters
    ----------
    poly1 : Polygon3D
        The subject polygon.
    poly2 : Polygon3D
        The clip polygon.
    
    Returns
    -------
    Pyclipper object
    
    """
    if not poly1.is_coplanar(poly2):
        return False
    poly1 = poly1.project_to_2D()
    poly2 = poly2.project_to_2D()

    s1 = pc.scale_to_clipper(poly1.vertices_list)
    s2 = pc.scale_to_clipper(poly2.vertices_list)
    clipper = pc.Pyclipper()
    clipper.AddPath(s1, poly_type=pc.PT_SUBJECT, closed=True)
    clipper.AddPath(s2, poly_type=pc.PT_CLIP, closed=True)
    
    return clipper


def union_3D_polys(poly1, poly2):
    """Union of two 3D polygons.
    
    Parameters
    ----------
    poly1 : Polygon3D
        The subject polygon.
    poly2 : Polygon3D
        The clip polygon.

    Returns
    -------
    list or False
        A list of lists of Polygon3D objects representing each union.
    
    """
    clipper = prep_3D_polys(poly1, poly2)
    if not clipper:
        return []
    unions = clipper.Execute(
        pc.CT_UNION, pc.PFT_NONZERO, pc.PFT_NONZERO)
    
    polys = process_clipped_3D_polys(unions, poly1)
    
    # orient to match poly1
    results = []
    for poly in polys:
        if almostequal(poly.normal_vector, poly1.normal_vector):
            results.append(poly)
        else:
            results.append(poly.invert_orientation())

    return results


def intersect_3D_polys(poly1, poly2):    
    """Intersection of two 3D polygons.
    
    Parameters
    ----------
    poly1 : Polygon3D
        The subject polygon.
    poly2 : Polygon3D
        The clip polygon.

    Returns
    -------
    list or False
        False if no intersection, otherwise a list of lists of Polygon3D
        objects representing each intersection.
    
    """
    clipper = prep_3D_polys(poly1, poly2)    
    if not clipper:
        return []
    intersections = clipper.Execute(
        pc.CT_INTERSECTION, pc.PFT_NONZERO, pc.PFT_NONZERO)
    
    polys = process_clipped_3D_polys(intersections, poly1)
    # orient to match poly1
    results = []
    for poly in polys:
        if almostequal(poly.normal_vector, poly1.normal_vector):
            results.append(poly)
        else:
            results.append(poly.invert_orientation())

    return results


def difference_3D_polys(poly1, poly2):
    """Difference between two 3D polygons.
    
    Parameters
    ----------
    poly1 : Polygon3D
        The subject polygon.
    poly2 : Polygon3D
        The clip polygon.

    Returns
    -------
    list or False
        False if no difference, otherwise a list of lists of Polygon3D
        objects representing each difference.
    
    """
    clipper = prep_3D_polys(poly1, poly2)
    if not clipper:
        return []
    differences = clipper.Execute(
        pc.CT_DIFFERENCE, pc.PFT_NONZERO, pc.PFT_NONZERO)
    
    polys = process_clipped_3D_polys(differences, poly1)

    # orient to match poly1
    results = []
    for poly in polys:
        if almostequal(poly.normal_vector, poly1.normal_vector):
            results.append(poly)
        else:
            results.append(poly.invert_orientation())

    return results


def process_clipped_3D_polys(results, example3d):
    """Convert 2D clipping results back to 3D.
    
    Parameters
    ----------
    example3d : Polygon3D
        Used to find the plane to project the 2D polygons into.
    
    Returns
    -------
    list or False
        List of Poygon3D if result found, otherwise False.
        
    """
    if results:
        res_vertices = [pc.scale_from_clipper(r) for r in results]
        return [Polygon(v).project_to_3D(example3d) for v in res_vertices]
    else:
        return []

        
def project_to_2D(vertices, proj_axis):
    """Project a 3D polygon into 2D space.
    
    Parameters
    ----------
    vertices : list 
        The three-dimensional vertices of the polygon.
    proj_axis : int
        The axis to project into.
    a : float
        Distance to the origin for the plane to project into.
    v : list
        Normal vector of the plane to project into.
    
    Returns
    -------
    list
        The transformed vertices.
    
    """
    points = [project(x, proj_axis) for x in vertices]
    return points


def project(pt, proj_axis):
    """Project point pt onto either the xy, yz, or xz plane
    
    We choose the one that avoids degenerate configurations, which is the
    purpose of proj_axis.
    See http://stackoverflow.com/a/39008641/1706564
    
    """
    return tuple(c for i, c in enumerate(pt) if i != proj_axis)


def project_to_3D(vertices, proj_axis, a, v):
    """Project a 2D polygon into 3D space.
    
    Parameters
    ----------
    vertices : list 
        The two-dimensional vertices of the polygon.
    proj_axis : int
        The axis to project into.
    a : float
        Distance to the origin for the plane to project into.
    v : list
        Normal vector of the plane to project into.
    
    Returns
    -------
    list
        The transformed vertices.
    
    """
    return [project_inv(pt, proj_axis, a, v) for pt in vertices]


def project_inv(pt, proj_axis, a, v):
    """Returns the vector w in the surface's plane such that project(w) equals
    x.
    
    See http://stackoverflow.com/a/39008641/1706564
    
    Parameters
    ----------
    pt : list 
        The two-dimensional point.
    proj_axis : int
        The axis to project into.
    a : float
        Distance to the origin for the plane to project into.
    v : list
        Normal vector of the plane to project into.
    
    Returns
    -------
    list
        The transformed point.
    
    """
    w = list(pt)
    w[proj_axis:proj_axis] = [0.0]
    c = a
    for i in range(3):
        c -= w[i] * v[i]
    c /= v[proj_axis]
    w[proj_axis] = c
    return tuple(w)


def pt_to_tuple(pt, dims=3):
    """Convert a point to a numpy array.
    
    Convert a Vector3D to an (x,y,z) tuple or a Vector2D to an (x,y) tuple.
    Ensures all values are floats since some other types cause problems in 
    pyclipper (notably where sympy.Zero is used to represent 0.0).

    Parameters
    ----------
    pt : sympy.Vector3D, sympy.Vector2D
        The point to convert.
    dims : int, optional
        Number of dimensions {default : 3}.
        
    Returns
    -------
    tuple

    """
    # handle Vector3D
    if dims == 3:
        return float(pt.x), float(pt.y), float(pt.z)
    # handle Vector2D
    elif dims == 2:
        return float(pt.x), float(pt.y)


def pt_to_array(pt, dims=3):
    """Convert a point to a numpy array.
    
    Converts a Vector3D to a numpy.array([x,y,z]) or a Vector2D to a 
    numpy.array([x,y]).
    Ensures all values are floats since some other types cause problems in 
    pyclipper (notably where sympy.Zero is used to represent 0.0).
    
    Parameters
    ----------
    pt : sympy.Vector3D
        The point to convert.
    dims : int, optional
        Number of dimensions {default : 3}.
    
    Returns
    -------
    numpy.ndarray

    """
    # handle Vector3D
    if dims == 3:
        return np.array([float(pt.x), float(pt.y), float(pt.z)])
    # handle Vector2D
    elif dims == 2:
        return np.array([float(pt.x), float(pt.y)])
    
    
def normalize_coords(poly, outside_pt, ggr=None):
    """Put coordinates into the correct format for EnergyPlus.
    
    poly : Polygon3D
        Polygon with the new coordinates.
    outside_pt : Vector3D
        An outside point of the new polygon.
    ggr : EPBunch, optional
        The section of the IDF that give rules for the order of vertices in a
        surface {default : None}.
    
    Returns
    -------
    list
    
    """
    # check and set entry direction
    poly = set_entry_direction(poly, outside_pt, ggr)
    # check and set starting position
    poly = set_starting_position(poly, outside_pt, ggr)

    return poly


def set_entry_direction(poly, outside_pt, ggr=None):
    """Check and set entry direction.
    """
    if not ggr:
        entry_direction = 'counterclockwise' # EnergyPlus default
    else:
        entry_direction = ggr.Vertex_Entry_Direction.lower()
    if entry_direction == 'counterclockwise':
        if poly.is_clockwise(outside_pt):
            poly = poly.invert_orientation()
    elif entry_direction == 'clockwise':
        if not poly.is_clockwise(outside_pt):
            poly = poly.invert_orientation()
    return poly


def set_starting_position(poly, outside_pt, ggr=None):
    """Check and set entry direction.
    """
    if not ggr:
        starting_position = 'upperleftcorner' # EnergyPlus default
    else:
        starting_position = ggr.Starting_Vertex_Position.lower()
    poly = poly.order_points(starting_position)

    return poly
