"""
Segment class, representing a line segment.

"""

from typing import Any, Iterator  # noqa

from .vectors import Vector3D
from ..utilities import almostequal

if False: from .polygons import Polygon3D  # noqa


class Segment(object):
    """Line segment in 3D."""

    def __init__(self, *vertices):
        # type: (*Vector3D) -> None
        self.vertices = vertices
        self.p1 = vertices[0]
        self.p2 = vertices[1]

    def __repr__(self):
        # type: () -> str
        class_name = type(self).__name__
        return '{}({}, {})'.format(class_name, self.p1, self.p2)

    def __neg__(self):
        # type: () -> Segment
        return Segment(self.p2, self.p1)

    def __iter__(self):
        # type: () -> Iterator
        return (i for i in self.vertices)

    def __eq__(self, other):
        # type: (Any) -> bool
        return self.__dict__ == other.__dict__

    def _is_collinear(self, other):
        # type: (Segment) -> bool
        """Test if a segment is collinear with another segment

        :param other: The other segment.
        :return: True if the segments are collinear else False.
        """
        if almostequal(other, self) or almostequal(other, -self):
            return True
        a = self.p1 - other.p1
        b = self.p1 - other.p2
        angle_between = a.cross(b)
        if almostequal(angle_between, Vector3D(0, 0, 0)):
            return True
        a = self.p2 - other.p1
        b = self.p2 - other.p2
        angle_between = a.cross(b)
        if almostequal(angle_between, Vector3D(0, 0, 0)):
            return True
        return False

    def _on_poly_edge(self, poly):
        # type: (Polygon3D) -> bool
        """Test if segment lies on any edge of a polygon

        :param poly: The polygon to test against.
        :returns: True if segment lies on any edge of the polygon, else False.
        """
        for edge in poly.edges:
            if self._is_collinear(edge):
                return True
        return False
