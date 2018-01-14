"""Perform clipping operations on Polygons.

PyClipper is used for clipping.
"""
from typing import List  # noqa

import pyclipper as pc

if False: from .polygons import Polygon2D,  Polygon3D  # noqa
from ..utilities import almostequal


class Clipper(object):
    """Base class for 2D and 3D clippers."""

    def difference(self, poly):
        # type: (Polygon3D) -> List[Polygon3D]
        """Intersect with another 2D polygon.

        :param poly: The clip polygon.
        :returns: False if no intersection, otherwise a list of lists of Polygons representing each difference.
        """
        clipper = self._prepare_clipper(poly)
        if not clipper:
            return []
        differences = clipper.Execute(
            pc.CT_DIFFERENCE, pc.PFT_NONZERO, pc.PFT_NONZERO)

        return self._process(differences)

    def intersect(self, poly):
        # type: (Polygon3D) -> List[Polygon3D]
        """Intersect with another 3D polygon.

        :param poly: The clip polygon.
        :returns: False if no intersection, otherwise a list of Polygons representing each intersection.
        """
        clipper = self._prepare_clipper(poly)
        if not clipper:
            return []
        intersections = clipper.Execute(
            pc.CT_INTERSECTION, pc.PFT_NONZERO, pc.PFT_NONZERO)

        return self._process(intersections)

    def union(self, poly):
        # type: (Polygon3D) -> List[Polygon3D]
        """Union with another 3D polygon.

        :param poly: The clip polygon.
        :returns: A list of Polygon3Ds.
        """
        clipper = self._prepare_clipper(poly)
        if not clipper:
            return []
        unions = clipper.Execute(
            pc.CT_UNION, pc.PFT_NONZERO, pc.PFT_NONZERO)

        return self._process(unions)


class Clipper2D(Clipper):
    """This class is used to add clipping functionality to the Polygon2D class."""

    def _prepare_clipper(self, poly):
        # type: (Polygon2D) -> pc.Pyclipper
        """Prepare 2D polygons for clipping operations.

        :param poly: The clip polygon.
        :returns: A Pyclipper object.
        """
        s1 = pc.scale_to_clipper(self.vertices_list)
        s2 = pc.scale_to_clipper(poly.vertices_list)
        clipper = pc.Pyclipper()
        clipper.AddPath(s1, poly_type=pc.PT_SUBJECT, closed=True)
        clipper.AddPath(s2, poly_type=pc.PT_CLIP, closed=True)
        return clipper

    def _process(self, results):
        # type: (List[List[List[int]]]) -> List[Polygon2D]
        """Process and return the results of a clipping operation.

        :param results: A list of lists of coordinates .
        :returns: A list of Polygon2D results of the clipping operation.
        """
        if not results:
            return []
        scaled = [pc.scale_from_clipper(r) for r in results]
        polys = [self.as_2d(r) for r in scaled]
        processed = []
        for poly in polys:
            if almostequal(poly.normal_vector, self.normal_vector):
                processed.append(poly)
            else:
                processed.append(poly.invert_orientation())
        return processed


class Clipper3D(Clipper):
    """This class is used to add clipping functionality to the Polygon3D class."""

    def _prepare_clipper(self, poly):
        # type: (Polygon3D) -> pc.Pyclipper
        """Prepare 3D polygons for clipping operations.

        :param poly: The clip polygon.
        :returns: A Pyclipper object.
        """
        if not self.is_coplanar(poly):
            return False
        poly1 = self.project_to_2D()
        poly2 = poly.project_to_2D()

        s1 = pc.scale_to_clipper(poly1.vertices_list)
        s2 = pc.scale_to_clipper(poly2.vertices_list)
        clipper = pc.Pyclipper()
        clipper.AddPath(s1, poly_type=pc.PT_SUBJECT, closed=True)
        clipper.AddPath(s2, poly_type=pc.PT_CLIP, closed=True)

        return clipper

    def _process(self, results):
        # type: (List[List[List[int]]], Polygon3D) -> List[Polygon3D]
        """Process and return the results of a clipping operation.

        :param results: A list of lists of coordinates .
        :returns: A list of Polygon3D results of the clipping operation.
        """
        if not results:
            return []
        results = [pc.scale_from_clipper(r) for r in results]
        polys = [self.as_2d(v).project_to_3D(self) for v in results]
        processed = []
        for poly in polys:
            if almostequal(self.normal_vector, poly.normal_vector):
                processed.append(poly)
            else:
                processed.append(poly.invert_orientation())
        return processed
