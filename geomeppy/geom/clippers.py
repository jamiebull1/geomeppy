# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""Perform clipping operations on Polygons.

PyClipper is used for clipping.
"""
import pyclipper as pc

if False: from .polygons import Polygon2D,  Polygon3D  # noqa
from ..utilities import almostequal


class Clipper2D(object):
    """This class is used to add clipping functionality to the Polygon2D class."""

    def _prep(self, poly):
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

    def difference(self, poly):
        # type: (Polygon2D) -> Union[bool, List[Polygon2D]]
        """Intersect with another 2D polygon.

        :param poly: The clip polygon.
        :returns: False if no intersection, otherwise a list of lists of Polygons representing each difference.
        """
        clipper = self._prep(poly)
        differences = clipper.Execute(
            pc.CT_DIFFERENCE, pc.PFT_NONZERO, pc.PFT_NONZERO)
        polys = self._process(differences)
        results = []
        for poly in polys:
            if almostequal(poly.normal_vector, self.normal_vector):
                results.append(poly)
            else:
                results.append(poly.invert_orientation())
        return results

    def intersect(self, poly):
        """Intersect with another 2D polygon.

        :param poly: The clip polygon.
        :returns: False if no intersection, otherwise a list of Polygons representing each intersection.
        """
        # type: (Polygon2D) -> Union[bool, List[Polygon2D]]
        clipper = self._prep(poly)
        intersections = clipper.Execute(
            pc.CT_INTERSECTION, pc.PFT_NONZERO, pc.PFT_NONZERO)
        polys = self._process(intersections)
        results = []
        for poly in polys:
            if almostequal(poly.normal_vector, self.normal_vector):
                results.append(poly)
            else:
                results.append(poly.invert_orientation())

        return results

    def union(self, poly):
        # type: (Polygon2D) -> List[Polygon2D]
        """Union with another 2D polygon.

        :param poly: The clip polygon.
        :returns: A list of Polygon2Ds.
        """
        clipper = self._prep(poly)
        intersections = clipper.Execute(
            pc.CT_UNION, pc.PFT_NONZERO, pc.PFT_NONZERO)
        polys = self._process(intersections)
        results = []
        for poly in polys:
            if almostequal(poly.normal_vector, self.normal_vector):
                results.append(poly)
            else:
                results.append(poly.invert_orientation())
        return results

    def _process(self, results):
        # type: (List[List[List[int]]]) -> List[Polygon2D]
        """Process and return the results of a clipping operation.

        :param results: A list of lists of coordinates .
        :returns: A list of Polygon2D results of the clipping operation.
        """
        if results:
            results = [pc.scale_from_clipper(r) for r in results]
            return [self.as_2d(r) for r in results]
        else:
            return []


class Clipper3D(object):
    """This class is used to add clipping functionality to the Polygon3D class."""

    def _prep(self, poly):
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

    def difference(self, poly):
        # type: (Polygon3D) -> List[Polygon3D]
        """Intersect with another 2D polygon.

        :param poly: The clip polygon.
        :returns: False if no intersection, otherwise a list of lists of Polygons representing each difference.
        """
        clipper = self._prep(poly)
        if not clipper:
            return []
        differences = clipper.Execute(
            pc.CT_DIFFERENCE, pc.PFT_NONZERO, pc.PFT_NONZERO)

        polys = self._process(differences, self)

        # orient to match poly1
        results = []
        for poly in polys:
            if almostequal(self.normal_vector, poly.normal_vector):
                results.append(poly)
            else:
                results.append(poly.invert_orientation())

        return results

    def intersect(self, poly):
        # type: (Polygon3D) -> List[Polygon3D]
        """Intersect with another 3D polygon.

        :param poly: The clip polygon.
        :returns: False if no intersection, otherwise a list of Polygons representing each intersection.
        """
        clipper = self._prep(poly)
        if not clipper:
            return []
        intersections = clipper.Execute(
            pc.CT_INTERSECTION, pc.PFT_NONZERO, pc.PFT_NONZERO)

        polys = self._process(intersections, self)
        # orient to match poly1
        results = []
        for poly in polys:
            if almostequal(self.normal_vector, poly.normal_vector):
                results.append(poly)
            else:
                results.append(poly.invert_orientation())

        return results

    def union(self, poly):
        # type: (Polygon3D) -> List[Polygon3D]
        """Union with another 3D polygon.

        :param poly: The clip polygon.
        :returns: A list of Polygon3Ds.
        """
        clipper = self._prep(poly)
        if not clipper:
            return []
        unions = clipper.Execute(
            pc.CT_UNION, pc.PFT_NONZERO, pc.PFT_NONZERO)

        polys = self._process(unions, self)

        # orient to match self
        results = []
        for poly in polys:
            if almostequal(self.normal_vector, poly.normal_vector):
                results.append(poly)
            else:
                results.append(poly.invert_orientation())

        return results

    def _process(self, results, example3d):
        # type: (List[List[List[int]]], Polygon3D) -> List[Polygon3D]
        """Process and return the results of a clipping operation.

        :param results: A list of lists of coordinates .
        :returns: A list of Polygon3D results of the clipping operation.
        """

        if results:
            results = [pc.scale_from_clipper(r) for r in results]
            return [self.as_2d(v).project_to_3D(example3d) for v in results]
        else:
            return []
        return results
