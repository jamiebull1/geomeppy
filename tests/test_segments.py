# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""
Tests for Segment class, representing a line segment.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from geomeppy.segments import Segment
from geomeppy.vectors import Vector3D


def test_segment_repr():
    edge = Segment(Vector3D(0,0,0), Vector3D(2,0,0))
    assert eval(repr(edge)) == edge

def test_collinear():
    # same line
    edge1 = Segment(Vector3D(0,0,0), Vector3D(1,1,1))
    edge2 = Segment(Vector3D(0,0,0), Vector3D(1,1,1))
    assert edge1.is_collinear(edge2)

    # opposite direction line
    edge1 = Segment(Vector3D(1,1,1), Vector3D(0,0,0))
    edge2 = Segment(Vector3D(0,0,0), Vector3D(1,1,1))
    assert edge1.is_collinear(edge2)

    # edge1 is longer
    edge1 = Segment(Vector3D(0,0,0), Vector3D(4,4,4))
    edge2 = Segment(Vector3D(1,1,1), Vector3D(2,2,2))
    assert edge1.is_collinear(edge2)

    # same start point, different lengths
    edge1 = Segment(Vector3D(0,0,0), Vector3D(1,1,1))
    edge2 = Segment(Vector3D(0,0,0), Vector3D(2,2,2))
    assert edge1.is_collinear(edge2)
    
    # something being missed
    edge1 = Segment(Vector3D(1,4,0), Vector3D(1,0,0))
    edge2 = Segment(Vector3D(1,0,0), Vector3D(1,2,0))
    assert edge1.is_collinear(edge2)
    
    # parallel
    edge1 = Segment(Vector3D(0,0,0), Vector3D(1,1,1))
    edge2 = Segment(Vector3D(1,0,0), Vector3D(2,1,1))
    assert not edge1.is_collinear(edge2)

