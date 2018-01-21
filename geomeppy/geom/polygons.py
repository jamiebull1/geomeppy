"""Heavy lifting geometry for IDF surfaces."""
from collections import MutableSequence
from itertools import product
from math import atan2, pi
from typing import Any, List, Optional, Tuple, Union  # noqa

from eppy.geometry.surface import area
from eppy.idf_msequence import Idf_MSequence  # noqa
import numpy as np
from shapely import wkt
from six.moves import zip

from .clippers import Clipper2D, Clipper3D
from .segments import Segment
from .transformations import align_face, invert_align_face
from .vectors import Vector2D, Vector3D
from ..utilities import almostequal


class Polygon(Clipper2D, MutableSequence):
    """Base class for 2D and 3D polygons."""

    @property
    def n_dims(self):
        pass

    @property
    def vector_class(self):
        pass

    @property
    def normal_vector(self):
        pass

    def __init__(self, vertices):
        # type: (Any) -> None
        super(Polygon, self).__init__()
        self.vertices = [self.vector_class(*v) for v in vertices]
        self.as_2d = Polygon2D

    def __repr__(self):
        # type: () -> str
        class_name = type(self).__name__
        return '{}({!r})'.format(class_name, self.vertices)

    def __len__(self):
        # type: () -> int
        return len(self.vertices)

    def __delitem__(self, key):
        del self.vertices[key]

    def __getitem__(self, key):
        # type: (Union[int, slice]) -> Any
        return self.vertices[key]

    def __setitem__(self, key, value):
        self.vertices[key] = value

    def __add__(self,
                other  # type: Polygon
                ):
        # type: (...) -> Union[None, Polygon]
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
            # subtract two equal polygons
            vertices = [v1 - v2 for v1, v2 in zip(self, other)]
        elif len(self[0]) == len(other):
            # translate by a vector
            vertices = [v - other for v in self]
        else:
            raise ValueError("Incompatible objects: %s + %s" % (self, other))
        return self.__class__(vertices)

    def insert(self, key, value):
        self.vertices.insert(key, value)

    @property
    def area(self):
        # type: () -> np.float64
        return area(self)

    @property
    def bounding_box(self):
        # type: () -> Polygon
        aligned = align_face(self)
        top_left = Vector3D(min(aligned.xs), max(aligned.ys), max(aligned.zs))
        bottom_left = Vector3D(
            min(aligned.xs), min(aligned.ys), min(aligned.zs))
        bottom_right = Vector3D(
            max(aligned.xs), min(aligned.ys), min(aligned.zs))
        top_right = Vector3D(max(aligned.xs), max(aligned.ys), max(aligned.zs))

        bbox = Polygon3D([top_left, bottom_left, bottom_right, top_right])
        return invert_align_face(self, bbox)

    @property
    def centroid(self):
        # type: () -> Vector2D
        """The centroid of a polygon."""
        return self.vector_class(
            sum(self.xs) / len(self),
            sum(self.ys) / len(self),
            sum(self.zs) / len(self),
            )

    @property
    def edges(self):
        # type: () -> List[Segment]
        """A list of edges represented as Segment objects."""
        vertices = self.vertices
        edges = [Segment(vertices[i], vertices[(i + 1) % len(self)])
                 for i in range(len(self))]
        return edges

    def invert_orientation(self):
        # type: () -> Polygon
        """Reverse the order of the vertices.

        This can be used to create a matching surface, e.g. the other side of a wall.

        :returns: A polygon.

        """
        return self.__class__(reversed(self.vertices))

    @property
    def is_convex(self):
        return is_convex_polygon(self.vertices_list)
        return False

    @property
    def points_matrix(self):
        # type: () -> np.ndarray
        """Matrix representing the points in a polygon.

        Format::
            [[x1, x2,... xn]
            [y1, y2,... yn]
            [z1, z2,... zn]  # all 0 for 2D polygon

        """
        points = np.zeros((len(self.vertices), self.n_dims))
        for i, v in enumerate(self.vertices):
            points[i, :] = v.as_array(dims=self.n_dims)
        return points

    @property
    def vertices_list(self):
        # type: () -> List[Tuple[float, float, Optional[float]]]
        """A list of the vertices in the format required by pyclipper.

        :returns: A list of tuples like [(x1, y1), (x2, y2),... (xn, yn)].

        """
        return [pt.as_tuple(dims=self.n_dims) for pt in self.vertices]

    @property
    def xs(self):
        # type: () -> List[float]
        return [pt.x for pt in self.vertices]

    @property
    def ys(self):
        # type: () -> List[float]
        return [pt.y for pt in self.vertices]

    @property
    def zs(self):
        pass


class Polygon2D(Polygon):
    """Two-dimensional polygon."""
    n_dims = 2
    vector_class = Vector2D

    def __eq__(self, other):
        if self.__dict__ == other.__dict__:  # try the simple case first
            return True
        else:  # also cover same shape in different rotation
            if self.difference(other):
                return False
            if almostequal(self.normal_vector, other.normal_vector):
                return True
        return False

    @property
    def normal_vector(self):
        # type: () -> Vector3D
        as_3d = Polygon3D((v.x, v.y, 0) for v in self)
        return as_3d.normal_vector

    def project_to_3D(self, example3d):
        # type: (Polygon3D) -> Polygon3D
        """Project the 2D polygon rotated into 3D space.

        This is used to return a previously rotated 3D polygon back to its original orientation, or to to put polygons
        generated from pyclipper into the desired orientation.

        :param example3D: A 3D polygon in the desired plane.
        :returns: A 3D polygon.

        """
        points = self.points_matrix
        proj_axis = example3d.projection_axis
        a = example3d.distance
        v = example3d.normal_vector
        projected_points = project_to_3D(points, proj_axis, a, v)
        return Polygon3D(projected_points)

    @property
    def zs(self):
        # type: () -> List[float]
        return [0.0] * len(self.vertices)


class Polygon3D(Clipper3D, Polygon):
    """Three-dimensional polygon."""
    n_dims = 3
    vector_class = Vector3D

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
        # type: () -> List[float]
        return [pt.z for pt in self.vertices]

    @property
    def normal_vector(self):
        """Unit normal vector perpendicular to the polygon in the outward direction.

        We use Newell's Method since the cross-product of two edge vectors is not valid for concave polygons.
        https://www.opengl.org/wiki/Calculating_a_Surface_Normal#Newell.27s_Method

        """
        n = [0.0, 0.0, 0.0]

        for i, v_curr in enumerate(self.vertices):
            v_next = self.vertices[(i + 1) % len(self.vertices)]
            n[0] += (v_curr.y - v_next.y) * (v_curr.z + v_next.z)
            n[1] += (v_curr.z - v_next.z) * (v_curr.x + v_next.x)
            n[2] += (v_curr.x - v_next.x) * (v_curr.y + v_next.y)

        return Vector3D(*n).normalize()

    @property
    def distance(self):
        # type: () -> np.float64
        """Distance from the origin to the polygon.

        Where v[0] * x + v[1] * y + v[2] * z = a is the equation of the plane containing the polygon (and where v
        is the polygon normal vector).

        :returns: The distance from the origin to the polygon.

        """
        v = self.normal_vector
        pt = self.points_matrix[0]  # arbitrary point in the polygon
        d = np.dot(v, pt)
        return d

    @property
    def projection_axis(self):
        # type: () -> int
        """An axis which will not lead to a degenerate surface.

        :returns: The axis index.

        """
        proj_axis = max(range(3), key=lambda i: abs(self.normal_vector[i]))
        return proj_axis

    @property
    def is_horizontal(self):
        # type: () -> bool
        """Check if polygon is in the xy plane.

        :returns: True if the polygon is in the xy plane, else False.

        """
        return bool(np.array(self.zs).std() < 1e-8)

    def is_clockwise(self, viewpoint):
        # type: (Vector3D) -> np.bool_
        """Check if vertices are ordered clockwise

        This function checks the vertices as seen from the viewpoint.

        :param viewpoint: A point from which to view the polygon.
        :returns: True if vertices are ordered clockwise when observed from the given viewpoint.

        """
        arbitrary_pt = self.vertices[0]
        v = arbitrary_pt - viewpoint
        n = self.normal_vector
        sign = np.dot(v, n)
        return sign > 0

    def is_coplanar(self, other):
        # type: (Polygon3D) -> bool
        """Check if polygon is in the same plane as another polygon.

        This includes the same plane but opposite orientation.

        :param other: Another polygon.
        :returns: True if the two polygons are coplanar, else False.

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

    def outside_point(self, entry_direction='counterclockwise'):
        # type: (str) -> Vector3D
        """Return a point outside the zone to which the surface belongs.

        The point will be outside the zone, respecting the global geometry rules
        for vertex entry direction.

        :param entry_direction: Either "clockwise" or "counterclockwise", as seen from outside the space.
        :returns: A point vector.

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
        # type: (str) -> Polygon3D
        """Reorder the vertices based on a starting position rule.

        :param starting_position: The string that defines vertex starting position in EnergyPlus.
        :returns: The reordered polygon.

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
        # type: () -> Polygon2D
        """Project the 3D polygon into 2D space.

        This is so that we can perform operations on it using pyclipper library.

        Project onto either the xy, yz, or xz plane. (We choose the one that
        avoids degenerate configurations, which is the purpose of proj_axis.)

        :returns: A 2D polygon.

        """
        points = self.points_matrix
        projected_points = project_to_2D(points, self.projection_axis)

        return Polygon2D([pt[:2] for pt in projected_points])

    def normalize_coords(self, ggr):
        """Order points, respecting the global geometry rules

        :param ggr: EnergyPlus GlobalGeometryRules object.
        :returns: The normalized polygon.

        """
        try:
            entry_direction = ggr.Vertex_Entry_Direction
        except AttributeError:
            entry_direction = 'counterclockwise'
        outside_point = self.outside_point(entry_direction)
        return normalize_coords(self, outside_point, ggr)

    def from_wkt(self, wkt_poly):
        # type: (str) -> Polygon3D
        """Convert a wkt representation of a polygon to GeomEppy.

        This also accounts for the possible presence of inner rings by linking them to the outer ring.

        :param wkt_poly: A text representation of a polygon in well known text (wkt) format.
        :returns: A polygon.

        """
        poly = wkt.loads(wkt_poly)
        exterior = Polygon3D(poly.exterior.coords)
        if poly.interiors:
            # make the exterior into a geomeppy poly
            for inner_ring in poly.interiors:
                # make the interior into a geomeppy poly
                interior = Polygon3D(inner_ring.coords)
                # find the nearest points on the exterior and interior
                links = list(product(interior, exterior))
                links = sorted(
                    links, key=lambda x: x[0].relative_distance(x[1]))
                on_interior = links[0][0]
                on_exterior = links[0][1]
                # join them up
                exterior = Polygon3D(exterior[exterior.index(
                    on_exterior):] + exterior[:exterior.index(on_exterior) + 1])
                interior = Polygon3D(interior[interior.index(
                    on_interior):] + interior[:interior.index(on_interior) + 1])
                exterior = Polygon3D(exterior[:] + interior[:])

        return exterior


def break_polygons(poly, hole):
    # type: (Polygon, Polygon) -> List[Polygon]
    """Break up a surface with a hole in it.

    This produces two surfaces, neither of which have a hole in them.

    :param poly: The surface with a hole in.
    :param hole: The hole.
    :returns: Two Polygon3D objects.

    """
    # take the two closest points on the surface perimeter
    links = list(product(poly, hole))
    links = sorted(links, key=lambda x: x[0].relative_distance(x[1]))  # fast distance check

    first_on_poly = links[0][0]
    last_on_poly = links[1][0]

    first_on_hole = links[1][1]
    last_on_hole = links[0][1]

    new_poly = (
        section(first_on_poly, last_on_poly, poly[:] + poly[:]) +
        section(first_on_hole, last_on_hole, reversed(hole[:] + hole[:]))
    )

    new_poly = Polygon3D(new_poly)
    union = hole.union(new_poly)[0]
    new_poly2 = poly.difference(union)[0]
    if not almostequal(new_poly.normal_vector, poly.normal_vector):
        new_poly = new_poly.invert_orientation()
    if not almostequal(new_poly2.normal_vector, poly.normal_vector):
        new_poly2 = new_poly2.invert_orientation()

    return [new_poly, new_poly2]


def section(first, last, coords):
    section_on_hole = []
    for item in coords:
        if item == first:
            section_on_hole.append(item)
        elif section_on_hole:
            section_on_hole.append(item)
            if item == last:
                break
    return section_on_hole


def project(pt, proj_axis):
    # type: (np.ndarray, int) -> Any
    """Project point pt onto either the xy, yz, or xz plane

    We choose the one that avoids degenerate configurations, which is the
    purpose of proj_axis.
    See http://stackoverflow.com/a/39008641/1706564

    """
    return tuple(c for i, c in enumerate(pt) if i != proj_axis)


def project_inv(pt,  # type: np.ndarray
                proj_axis,  # type: int
                a,  # type: np.float64
                v  # type: Vector3D
                ):
    # type: (...) -> Any
    """Returns the vector w in the surface's plane such that project(w) equals x.

    See http://stackoverflow.com/a/39008641/1706564

    :param pt: A two-dimensional point.
    :param proj_axis: The axis to project into.
    :param a: Distance to the origin for the plane to project into.
    :param v: Normal vector of the plane to project into.
    :returns: The transformed point.

    """
    w = list(pt)
    w[proj_axis:proj_axis] = [0.0]
    c = a
    for i in range(3):
        c -= w[i] * v[i]
    c /= v[proj_axis]
    w[proj_axis] = c
    return tuple(w)


def project_to_2D(vertices, proj_axis):
    # type: (np.ndarray, int) -> List[Tuple[np.float64, np.float64]]
    """Project a 3D polygon into 2D space.

    :param vertices: The three-dimensional vertices of the polygon.
    :param proj_axis: The axis to project into.
    :returns: The transformed vertices.

    """
    points = [project(x, proj_axis) for x in vertices]
    return points


def project_to_3D(vertices,  # type: np.ndarray
                  proj_axis,  # type: int
                  a,  # type: np.float64
                  v  # type: Vector3D
                  ):
    # type: (...) -> List[Tuple[np.float64, np.float64, np.float64]]
    """Project a 2D polygon into 3D space.

    :param vertices: The two-dimensional vertices of the polygon.
    :param proj_axis: The axis to project into.
    :param a: Distance to the origin for the plane to project into.
    :param v: Normal vector of the plane to project into.
    :returns: The transformed vertices.

    """
    return [project_inv(pt, proj_axis, a, v) for pt in vertices]


def normalize_coords(poly,  # type: Polygon3D
                     outside_pt,  # type: Vector3D
                     ggr=None  # type: Union[List, None, Idf_MSequence]
                     ):
    # type: (...) -> Polygon3D
    """Put coordinates into the correct format for EnergyPlus dependent on Global Geometry Rules (GGR).

    :param poly: Polygon with new coordinates, but not yet checked for compliance with GGR.
    :param outside_pt: An outside point of the new polygon.
    :param ggr: EnergyPlus GlobalGeometryRules object.
    :returns: The normalized polygon.

    """
    # check and set entry direction
    poly = set_entry_direction(poly, outside_pt, ggr)
    # check and set starting position
    poly = set_starting_position(poly, ggr)

    return poly


def set_entry_direction(poly, outside_pt, ggr=None):
    """Check and set entry direction for a polygon.

    :param poly: A polygon.
    :param outside_pt: A point beyond the outside face of the polygon.
    :param ggr: EnergyPlus global geometry rules
    :return: A polygon with the vertices correctly oriented.

    """
    if not ggr:
        entry_direction = 'counterclockwise'  # EnergyPlus default
    else:
        entry_direction = ggr.Vertex_Entry_Direction.lower()
    if entry_direction == 'counterclockwise':
        if poly.is_clockwise(outside_pt):
            poly = poly.invert_orientation()
    elif entry_direction == 'clockwise':
        if not poly.is_clockwise(outside_pt):
            poly = poly.invert_orientation()
    return poly


def set_starting_position(poly, ggr=None):
    """Check and set starting position."""
    if not ggr:
        starting_position = 'upperleftcorner'  # EnergyPlus default
    else:
        starting_position = ggr.Starting_Vertex_Position.lower()
    poly = poly.order_points(starting_position)

    return poly


def intersect(poly1, poly2):
    # type: (Polygon, Polygon) -> List[Polygon]
    """Calculate the polygons to represent the intersection of two polygons.

    :param poly1: The first polygon.
    :param poly2: The second polygon.
    :returns: A list of unique polygons.

    """
    polys = []  # type: List[Polygon]
    polys.extend(poly1.intersect(poly2))
    polys.extend(poly2.intersect(poly1))
    if is_hole(poly1, poly2):
        polys.extend(break_polygons(poly1, poly2))
    elif is_hole(poly2, poly1):
        polys.extend(break_polygons(poly2, poly1))
    else:
        polys.extend(poly1.difference(poly2))
        polys.extend(poly2.difference(poly1))
    polys = unique(polys)
    return polys


def unique(polys):
    # type: (List[Polygon]) -> List[Polygon]
    """Make a unique set of polygons.

    :param polys: A list of polygons.
    :returns: A unique list of polygons.

    """
    flattened = []
    for item in polys:
        if isinstance(item, Polygon):
            flattened.append(item)
        elif isinstance(item, list):
            flattened.extend(item)

    results = []  # type: List[Polygon]
    for poly in flattened:
        if not any(poly == result for result in results):
            results.append(poly)

    return results


def is_hole(surface, possible_hole):
    # type: (Polygon, Polygon) -> bool
    """Identify if an intersection is a hole in the surface.

    Check the intersection touches an edge of the surface. If it doesn't then it represents a hole, and this needs
    further processing into valid EnergyPlus surfaces.

    :param surface: The first surface.
    :param possible_hole: The intersection into the surface.
    :returns: True if the possible hole is a hole in the surface.

    """
    if surface.area < possible_hole.area:
        return False
    collinear_edges = (
        edges[0]._is_collinear(
            edges[1]) for edges in product(
            surface.edges,
            possible_hole.edges))
    return not any(collinear_edges)


def bounding_box(polygons):
    """The bounding box which encompasses all of the polygons in the x,y plane.

    :param polygons: A list of polygons.
    :return: A 2D polygon.

    """
    top_left = (
        min(min(c[0] for c in f.coords) for f in polygons),
        max(max(c[1] for c in f.coords) for f in polygons)
    )
    bottom_left = (
        min(min(c[0] for c in f.coords) for f in polygons),
        min(min(c[1] for c in f.coords) for f in polygons)
    )
    bottom_right = (
        max(max(c[0] for c in f.coords) for f in polygons),
        min(min(c[1] for c in f.coords) for f in polygons)
    )
    top_right = (
        max(max(c[0] for c in f.coords) for f in polygons),
        max(max(c[1] for c in f.coords) for f in polygons)
    )
    return Polygon2D([top_left, bottom_left, bottom_right, top_right])


def is_convex_polygon(polygon):  # noqa
    """Return True if the polynomial defined by the sequence of 2D
    points is 'strictly convex': points are valid, side lengths non-
    zero, interior angles are strictly between zero and a straight
    angle, and the polygon does not intersect itself.

    See: https://stackoverflow.com/a/45372025/1706564

    :: NOTES:
            1.  Algorithm: the signed changes of the direction angles
                from one side to the next side must be all positive or
                all negative, and their sum must equal plus-or-minus
                one full turn (2 pi radians). Also check for too few,
                invalid, or repeated points.
            2.  No check is explicitly done for zero    internal angles
                (180 degree direction-change angle) as this is covered
                in other ways, including the `n < 3` check.

    """
    two_pi = 2 * pi
    try:  # needed for any bad points or direction changes
        # Check for too few points
        if len(polygon) < 3:
            return False
        # Get starting information
        old_x, old_y = polygon[-2]
        new_x, new_y = polygon[-1]
        new_direction = atan2(new_y - old_y, new_x - old_x)
        angle_sum = 0.0
        # Check each point (the side ending there, its angle) and accum. angles
        for ndx, newpoint in enumerate(polygon):
            # Update point coordinates and side directions, check side length
            old_x, old_y, old_direction = new_x, new_y, new_direction
            new_x, new_y = newpoint
            new_direction = atan2(new_y - old_y, new_x - old_x)
            if old_x == new_x and old_y == new_y:
                return False  # repeated consecutive points
            # Calculate & check the normalized direction-change angle
            angle = new_direction - old_direction
            if angle <= -pi:
                angle += two_pi  # make it in half-open interval (-Pi, Pi]
            elif angle > pi:
                angle -= two_pi
            if ndx == 0:  # if first time through loop, initialize orientation
                if angle == 0.0:
                    return False
                orientation = 1.0 if angle > 0.0 else -1.0
            else:  # if other time through loop, check orientation is stable
                if orientation * angle <= 0.0:  # not both pos. or both neg.
                    return False
            # Accumulate the direction-change angle
            angle_sum += angle
        # Check that the total number of full turns is plus-or-minus 1
        return abs(round(angle_sum / two_pi)) == 1
    except (ArithmeticError, TypeError, ValueError):
        return False  # any exception means not a proper convex polygon
