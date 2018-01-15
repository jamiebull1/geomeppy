"""Tests for transformations"""
import numpy as np
from transforms3d._gohlketransforms import translation_matrix

from geomeppy.geom.polygons import Polygon3D
from geomeppy.geom.transformations import Transformation
from geomeppy.geom.vectors import Vector3D
from geomeppy.utilities import almostequal


class TestTransformations():
    
    def test_translation_transformations(self):
        # type: () -> None
        tol = 12 # places
        trans = Vector3D(1,1,1)
        point1 = Vector3D(1,0,0)
        t = Transformation()
        
        # identity transformation
        temp = t * point1
        assert almostequal(1.0, temp.x, tol)
        assert almostequal(0.0, temp.y, tol)
        assert almostequal(0.0, temp.z, tol)
        
        # move by 1, 1, 1
        t = Transformation(translation_matrix(trans))
        temp = t * point1
        assert almostequal(2.0, temp.x, tol)
        assert almostequal(1.0, temp.y, tol)
        assert almostequal(1.0, temp.z, tol)
        
        # move by -1, -1, -1
        temp = t._inverse() * point1
        assert almostequal(0.0, temp.x, tol)
        assert almostequal(-1.0, temp.y, tol)
        assert almostequal(-1.0, temp.z, tol)
        
        # identity transformation
        temp = t._inverse() * t * point1
        assert almostequal(1.0, temp.x, tol)
        assert almostequal(0.0, temp.y, tol)
        assert almostequal(0.0, temp.z, tol)
        
        # identity transformation
        temp = t * t._inverse() * point1
        assert almostequal(1.0, temp.x, tol)
        assert almostequal(0.0, temp.y, tol)
        assert almostequal(0.0, temp.z, tol)
    
    def test_align_z_prime_transformations(self):
        # type: () -> None
        x_axis = Vector3D(1,0,0)
        y_axis = Vector3D(0,1,0)
        z_axis = Vector3D(0,0,1)
        t = Transformation()
        
        outward_normal = Vector3D(0, -1, 0)
        t = t._align_z_prime(outward_normal)
        assert x_axis == t * x_axis
        assert z_axis == t * y_axis
        result = t * z_axis
        assert outward_normal == result
        
        outward_normal = Vector3D(1, 0, 0)
        t = t._align_z_prime(outward_normal)
        assert y_axis == t * x_axis
        assert z_axis == t * y_axis
        assert outward_normal == t * z_axis
        
        outward_normal = Vector3D(0, 1, 0)
        t = t._align_z_prime(outward_normal)
        assert -x_axis == t * x_axis
        assert z_axis == t * y_axis
        assert outward_normal == t * z_axis
        
        outward_normal = Vector3D(-1, 0, 0)
        t = t._align_z_prime(outward_normal)
        assert -y_axis == t * x_axis
        assert z_axis == t * y_axis
        assert outward_normal == t * z_axis
        
        outward_normal = Vector3D(0, 0, 1)
        t = t._align_z_prime(outward_normal)
        assert -x_axis == t * x_axis
        assert -y_axis == t * y_axis
        assert outward_normal == t * z_axis
        
        outward_normal = Vector3D(0, 0, -1)
        t = t._align_z_prime(outward_normal)
        assert -x_axis == t * x_axis
        assert y_axis == t * y_axis
        assert outward_normal == t * z_axis
    
    def test_align_face_transformations(self):
        # type: () -> None
        tol = 12  # places
        
        vertices = Polygon3D([(1, 0, 1), (1, 0, 0), (2, 0, 0), (2, 0, 1)])
        t = Transformation()
        
        # rotate 0 degrees about z
        testVertices = t._rotation(Vector3D(0, 0, 1), 0) * vertices
        t = Transformation()._align_face(testVertices)
        tempVertices = t._inverse() * testVertices
        expectedVertices = Polygon3D([(0,1,0),(0,0,0),(1,0,0),(1,1,0)])
        assert almostequal(tempVertices, expectedVertices, tol)
    
        # rotate 30 degrees about z
        testVertices = t._rotation(Vector3D(0, 0, 1), np.deg2rad(30)) * vertices
        t = Transformation()._align_face(testVertices)
        tempVertices = t._inverse() * testVertices
        expectedVertices = Polygon3D([(0,1,0),(0,0,0),(1,0,0),(1,1,0)])
        assert almostequal(tempVertices, expectedVertices, tol)
    
        # rotate -30 degrees about z
        testVertices = t._rotation(Vector3D(0, 0, 1), -np.deg2rad(30)) * vertices
        t = Transformation()._align_face(testVertices)
        tempVertices = t._inverse() * testVertices
        expectedVertices = Polygon3D([(0,1,0),(0,0,0),(1,0,0),(1,1,0)])
        assert almostequal(tempVertices, expectedVertices, tol)
    
        # rotate -30 degrees about x
        testVertices = t._rotation(Vector3D(1, 0, 0), -np.deg2rad(30)) * vertices
        t = Transformation()._align_face(testVertices)
        tempVertices = t._inverse() * testVertices
        expectedVertices = Polygon3D([(0,1,0),(0,0,0),(1,0,0),(1,1,0)])
        assert almostequal(tempVertices, expectedVertices, tol)
    
        # rotate -90 degrees about x
        testVertices = t._rotation(Vector3D(1, 0, 0), -np.deg2rad(90)) * vertices
        t = Transformation()._align_face(testVertices)
        tempVertices = t._inverse() * testVertices
        expectedVertices = Polygon3D([(1,0,0),(1,1,0),(0,1,0),(0,0,0)])
        assert almostequal(tempVertices, expectedVertices, tol)
    
        # rotate 30 degrees about x
        testVertices = t._rotation(Vector3D(1, 0, 0), np.deg2rad(30)) * vertices
        t = Transformation()._align_face(testVertices)
        tempVertices = t._inverse() * testVertices
        expectedVertices = Polygon3D([(0,1,0),(0,0,0),(1,0,0),(1,1,0)])
        assert almostequal(tempVertices, expectedVertices, tol)
    
        # rotate 90 degrees about x
        testVertices = t._rotation(Vector3D(1, 0, 0), np.deg2rad(90)) * vertices
        t = Transformation()._align_face(testVertices)
        tempVertices = t._inverse() * testVertices
        expectedVertices = Polygon3D([(1,0,0),(1,1,0),(0,1,0),(0,0,0)])
        assert almostequal(tempVertices, expectedVertices, tol)

    def test_align_face_transformations_trapezoid_floor(self):
        # type: () -> None
        tol = 12  # places
        
        testVertices = Polygon3D([(27.69,0,0),(0,0,0),
                                  (5,5,0),(22.69,5,0)])
        t = Transformation()._align_face(testVertices)
        tempVertices = t._inverse() * testVertices
        expectedVertices = Polygon3D([(0,0,0),(27.69,0,0),(22.69,5,0),(5,5,0)])
        assert almostequal(tempVertices, expectedVertices, tol)
