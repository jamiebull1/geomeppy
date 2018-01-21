"""
A module to handle translations, using Christopher Gohlke's transforms3d as far
as possible, but also trying to respect the intent of the algorithms used in
OpenStudio for the sake of consistency between tools based on EnergyPlus.

"""

from typing import Any, Optional, Union  # noqa

import numpy as np
from transforms3d._gohlketransforms import (
    concatenate_matrices,
    identity_matrix,
    inverse_matrix,
    rotation_matrix,
    translation_matrix,
)

if False: from .polygons import Polygon3D  # noqa
from .vectors import Vector2D, Vector3D  # noqa


class Transformation(object):
    def __init__(self, mat=None):
        # type: (Optional[np.ndarray]) -> None
        if mat is None:
            # initialise with a 4D identity matrix
            self.matrix = identity_matrix()
        else:
            # initialise with the matrix passed in
            self.matrix = mat
        assert self.matrix.shape == (4, 4)

    def __mul__(self, other):
        # type: (Any) -> Union[Transformation, Vector3D]
        if hasattr(other, 'matrix'):
            # matrix by a matrix
            mat = concatenate_matrices(self.matrix, other.matrix)  # type: ignore
            return Transformation(mat)
        elif hasattr(other, 'x'):
            # matrix by a vector
            vector = other
            temp = [vector.x, vector.y, vector.z, 1]  # type: ignore
            result = np.dot(self.matrix, temp)[:3]
            return Vector3D(*result)
        else:
            # matrix by each point in a polygon
            result = [self * point for point in other]
            return other.__class__(result)

    def _align_z_prime(self, zp):
        # type: (Union[Vector2D, Vector3D]) -> Transformation
        """Transform system with z' to regular system. Will try to align y'
        with z, but if that fails will align y' with y

        """
        zp = zp.normalize()

        z_axis = Vector3D(0, 0, 1)
        neg_x_axis = Vector3D(-1, 0, 0)

        # check if face normal is up or down
        if abs(zp.dot(z_axis)) < 0.99:
            # not facing up or down, set yPrime along z_axis
            yp = z_axis - zp.dot(z_axis) * zp
            yp = yp.normalize()
            xp = yp.cross(zp)
        else:
            # facing up or down, set xPrime along -x_axis
            xp = neg_x_axis - zp.dot(neg_x_axis) * zp
            xp = xp.normalize()
            yp = zp.cross(xp)

        self.matrix[:3, 0] = xp
        self.matrix[:3, 1] = yp
        self.matrix[:3, 2] = zp

        return self

    def _align_face(self, polygon):
        """A transformation to align a polygon with the origin.

        Parameters
        ----------
        polygon : Polygon3D

        Returns
        -------
        Transformation

        """
        zp = polygon.normal_vector
        align = self._align_z_prime(zp)

        aligned_vertices = align._inverse() * polygon
        min_x = min(aligned_vertices.xs)
        min_y = min(aligned_vertices.ys)
        min_z = min(aligned_vertices.zs)
        assert aligned_vertices.is_horizontal

        direction = Vector3D(min_x, min_y, min_z)
        translate = self._translation(direction)

        self.matrix = concatenate_matrices(align.matrix, translate.matrix)

        return self

    def _inverse(self):
        # type: () -> Transformation
        """The inverse of a given transformation.

        Returns
        -------
        Transformation

        """
        return Transformation(inverse_matrix(self.matrix))

    def _translation(self, direction):
        # type: (Vector3D) -> Transformation
        return Transformation(translation_matrix(direction))

    def _rotation(self, direction, angle):
        # type: (Vector3D, Union[int, np.float]) -> Transformation
        return Transformation(rotation_matrix(angle, direction))


def align_face(polygon):
    """Transformation to align face with z-axis.

    :param polygon: Polygon to be aligned.
    :returns: Polygon3D aligned with the z-axis.
    """
    t = Transformation()
    t._align_face(polygon)

    return t._inverse() * polygon


def invert_align_face(original, poly2):
    """Transformation to align face with original position.

    :param original: Polygon in the desired orientation.
    :param poly2: Polygon previously aligned with `align_face`.
    :returns: Polygon returned to the original orientation.
    """
    t = Transformation()
    t._align_face(original)

    return t * poly2
