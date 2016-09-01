# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""
Segment class, representing a line segment.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from geomeppy.vectors import Vector3D
from geomeppy.utilities import almostequal


class Segment(object):
    """Line segment in 3D."""
    
    def __init__(self, *vertices):
        self.vertices = vertices
        self.p1 = vertices[0]
        self.p2 = vertices[1]
    
    def __repr__(self):
        class_name = type(self).__name__
        return '{}({}, {})'.format(class_name, self.p1, self.p2)
    
    def __neg__(self):
        return Segment(self.p2, self.p1)
    
    def __iter__(self):
        return (i for i in self.vertices)
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def is_collinear(self, other):
        if almostequal(other, self) or almostequal(other, -self):
            return True
        a = self.p1 - other.p1
        b = self.p1 - other.p2
        angle_between = a.cross(b)
        if almostequal(angle_between, Vector3D(0,0,0)):
            return True
        a = self.p2 - other.p1
        b = self.p2 - other.p2
        angle_between = a.cross(b)
        if almostequal(angle_between, Vector3D(0,0,0)):
            return True
        return False
            
    def on_poly_edge(self, poly):
        """Test if segment lies on any edge of a polygon
        
        Parameters
        ----------
        poly : Polygon3D
            The polygon to test against.
        
        Returns
        -------
        bool
        
        """
        for edge in poly.edges:
            if self.is_collinear(edge):
                return True
        return False
