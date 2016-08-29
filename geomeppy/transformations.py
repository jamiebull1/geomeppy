# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""
A module to handle translations, using Christopher Gohlke's transforms3d as far
as possible, but also trying to respect the intent of the algorithms used in 
OpenStudio for the sake of consistency between tools based on EnergyPlus.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from transforms3d._gohlketransforms import concatenate_matrices
from transforms3d._gohlketransforms import identity_matrix
from transforms3d._gohlketransforms import inverse_matrix
from transforms3d._gohlketransforms import rotation_matrix
from transforms3d._gohlketransforms import translation_matrix

from geomeppy.vectors import Vector3D

import numpy as np


class Transformation(object):
        
    def __init__(self, mat=None):
        if mat is None:
            # initialise with a 4D identity matrix
            self.matrix = identity_matrix()
        else:
            # initialise with the matrix passed in
            self.matrix = mat
        assert self.matrix.shape == (4, 4)
        
    def __mul__(self, other):
        if hasattr(other, 'matrix'):
            # matrix by a matrix
            mat = concatenate_matrices(self.matrix, other.matrix)
            return Transformation(mat)
        elif hasattr(other, 'x'):
            # matrix by a vector
            vector = other
            temp = [vector.x, vector.y, vector.z, 1]
            result = np.dot(self.matrix, temp)[:3]
            return Vector3D(*result)
        else:
            # matrix by each point in a polygon
            result = [self * point for point in other]
            return other.__class__(result)
    
    def align_z_prime(self, zp):
        """Transform system with z' to regular system. Will try to align y' 
        with z, but if that fails will align y' with y
        
        """
        zp = zp.normalize()
        
        x_axis = Vector3D(1,0,0)
        y_axis = Vector3D(0,1,0)
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
        
        self.matrix[:3,0] = xp
        self.matrix[:3,1] = yp
        self.matrix[:3,2] = zp
        
        return self
        
    def align_face(self, polygon):
        """A transformation to align a polygon with the origin.
        
        Parameters
        ----------
        polygon : Polygon3D
        
        Returns
        -------
        Transformation
        
        """
        zp = polygon.normal_vector
        align = self.align_z_prime(zp)
        
        aligned_vertices = align.inverse() * polygon
        min_x = min(aligned_vertices.xs)
        min_y = min(aligned_vertices.ys)
        min_z = min(aligned_vertices.zs)
        assert aligned_vertices.is_horizontal
        
        direction = Vector3D(min_x, min_y, min_z)
        translate = self.translation(direction)
        
        self.matrix = concatenate_matrices(align.matrix, translate.matrix)

        return self
    
    def inverse(self):
        """The inverse of a given transformation.
        
        Returns
        -------
        Transformation
        
        """
        return Transformation(inverse_matrix(self.matrix))
    
    def translation(self, direction):
        return Transformation(translation_matrix(direction))

    def rotation(self, direction, angle):
        return Transformation(rotation_matrix(angle, direction))


def reorder_ULC(polygon):
    """Reorder points to upper-left-corner convention.
    """
    N = len(polygon)
    assert N >= 3
    # transformation to align face
    t = Transformation()
    t.align_face(polygon)
    aligned_polygon = t.inverse() * polygon
    
    # find ulc index in face coordinates
    min_x = float('inf')
    max_y = max(aligned_polygon.ys)  # prioritise upper vertices
    ulc_index = 0
    for i, vertex in enumerate(aligned_polygon):
        assert vertex.z < 0.001
        if vertex.y == max_y:
            if vertex.x <= min_x:
                min_x = vertex.x
                ulc_index = i
    
    # create output
    if ulc_index == 0:
        result = polygon
    else:
        vertices = [polygon.vertices[(i + ulc_index) % len(polygon)] 
                    for i in range(len(polygon))]
        result = polygon.__class__(vertices)
        assert len(result) == N

    return result       


