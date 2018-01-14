"""Tests for Segment class, representing a line segment."""
from geomeppy.geom.segments import Segment
from geomeppy.geom.vectors import Vector3D


def test_segment_repr():
    # type: () -> None
    edge = Segment(Vector3D(0,0,0), Vector3D(2,0,0))
    assert eval(repr(edge)) == edge

def test_collinear():
    # type: () -> None
    # same line
    edge1 = Segment(Vector3D(0,0,0), Vector3D(1,1,1))
    edge2 = Segment(Vector3D(0,0,0), Vector3D(1,1,1))
    assert edge1._is_collinear(edge2)

    # opposite direction line
    edge1 = Segment(Vector3D(1,1,1), Vector3D(0,0,0))
    edge2 = Segment(Vector3D(0,0,0), Vector3D(1,1,1))
    assert edge1._is_collinear(edge2)

    # edge1 is longer
    edge1 = Segment(Vector3D(0,0,0), Vector3D(4,4,4))
    edge2 = Segment(Vector3D(1,1,1), Vector3D(2,2,2))
    assert edge1._is_collinear(edge2)

    # same start point, different lengths
    edge1 = Segment(Vector3D(0,0,0), Vector3D(1,1,1))
    edge2 = Segment(Vector3D(0,0,0), Vector3D(2,2,2))
    assert edge1._is_collinear(edge2)
    
    # something being missed
    edge1 = Segment(Vector3D(1,4,0), Vector3D(1,0,0))
    edge2 = Segment(Vector3D(1,0,0), Vector3D(1,2,0))
    assert edge1._is_collinear(edge2)
    
    # parallel
    edge1 = Segment(Vector3D(0,0,0), Vector3D(1,1,1))
    edge2 = Segment(Vector3D(1,0,0), Vector3D(2,1,1))
    assert not edge1._is_collinear(edge2)

