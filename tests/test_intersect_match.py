# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""pytest for intersect_match.py"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from devtools.view_geometry import view_idf
from devtools.view_geometry import view_polygons
from geomeppy.intersect_match import getidfsurfaces
from geomeppy.intersect_match import intersect_idf_surfaces
from geomeppy.intersect_match import is_hole
from geomeppy.polygons import Polygon3D

from eppy.iddcurrent import iddcurrent
from eppy.modeleditor import IDF as BaseIDF
from eppy.modeleditor import addthisbunch
import pytest
from six import StringIO


class IDF(BaseIDF):
    """Monkey-patched IDF to fix copyidfobject."""
    
    def __init__(self, *args, **kwargs):
        super(IDF, self).__init__(*args, **kwargs)
    
    def copyidfobject(self, idfobject):
        """Monkey-patched to add the return value.
        """
        return addthisbunch(self.idfobjects,
                            self.model,
                            self.idd_info,
                            idfobject)

idf_txt = """
Version, 8.5;
Building, Building 1, , , , , , , ;
Zone, z1 Thermal Zone, 0.0, 0.0, 0.0, 0.0, , 1, , , , , , Yes;
Zone, z2 Thermal Zone, 0.0, 0.0, 0.0, 0.0, , 1, , , , , , Yes;
BuildingSurface:Detailed, z1_FLOOR, Floor, , z1 Thermal Zone, ground, , NoSun, NoWind, , , 1.0, 2.1, 0.0, 2.0, 2.0, 0.0, 2.0, 1.0, 0.0, 1.0, 1.1, 0.0;
BuildingSurface:Detailed, z1_ROOF, Roof, , z1 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 2.0, 1.0, 0.5, 2.0, 2.0, 0.5, 1.0, 2.1, 0.5, 1.0, 1.1, 0.5;
BuildingSurface:Detailed, z1_WALL_0001, WALL, , z1 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 1.0, 1.1, 0.5, 1.0, 1.1, 0.0, 1.0, 2.1, 0.0, 1.0, 2.1, 0.5;
BuildingSurface:Detailed, z1_WALL_0002, Wall, , z1 Thermal Zone, Outdoors, , SunExposed, WindExposed, , , 1.0, 2.1, 0.5, 1.0, 2.1, 0.0, 2.0, 2.0, 0.0, 2.0, 2.0, 0.5;
BuildingSurface:Detailed, z1_WALL_0003, WALL, , z1 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 2.0, 2.0, 0.5, 2.0, 2.0, 0.0, 2.0, 1.0, 0.0, 2.0, 1.0, 0.5;
BuildingSurface:Detailed, z1_WALL_0004, WALL, , z1 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 2.0, 1.0, 0.5, 2.0, 1.0, 0.0, 1.0, 1.1, 0.0, 1.0, 1.1, 0.5;
BuildingSurface:Detailed, z2_FLOOR, Floor, , z2 Thermal Zone, ground, , NoSun, NoWind, , , 1.5, 3.05, 0.0, 2.5, 2.95, 0.0, 2.5, 1.95, 0.0, 1.5, 2.05, 0.0;
BuildingSurface:Detailed, z2_ROOF, Roof, , z2 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 2.5, 1.95, 0.5, 2.5, 2.95, 0.5, 1.5, 3.05, 0.5, 1.5, 2.05, 0.5;
BuildingSurface:Detailed, z2_WALL_0001, WALL, , z2 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 1.5, 2.05, 0.5, 1.5, 2.05, 0.0, 1.5, 3.05, 0.0, 1.5, 3.05, 0.5;
BuildingSurface:Detailed, z2_WALL_0002, WALL, , z2 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 1.5, 3.05, 0.5, 1.5, 3.05, 0.0, 2.5, 2.95, 0.0, 2.5, 2.95, 0.5;
BuildingSurface:Detailed, z2_WALL_0003, WALL, , z2 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 2.5, 2.95, 0.5, 2.5, 2.95, 0.0, 2.5, 1.95, 0.0, 2.5, 1.95, 0.5;
BuildingSurface:Detailed, z2_WALL_0004, Wall, , z2 Thermal Zone, Outdoors, , SunExposed, WindExposed, , , 2.5, 1.95, 0.5, 2.5, 1.95, 0.0, 1.5, 2.05, 0.0, 1.5, 2.05, 0.5;
"""

idf_txt_ring = """
Version, 8.5;
Building, Building 1, , , , , , , ;
Zone, Thermal Zone 1, 0.0, 0.0, 0.0, 0.0, , 1, , , , , , Yes;
Zone, Thermal Zone 2, 0.0, 0.0, 0.0, 0.0, , 1, , , , , , Yes;
BuildingSurface:Detailed, z1 Floor 0001, Floor, , Thermal Zone 1, Ground, , NoSun, NoWind, , , -0.259, 2.46, 0.0, -0.259, 0.4, 0.0, -1.68, 0.4, 0.0, -1.68, 2.46, 0.0;
BuildingSurface:Detailed, z1 Wall 0001, Wall, , Thermal Zone 1, Outdoors, , SunExposed, WindExposed, , , -0.259, 2.46, 0.7279, -0.259, 2.46, 0.0, -1.68, 2.46, 0.0, -1.68, 2.46, 0.7279;
BuildingSurface:Detailed, z1 Wall 0002, Wall, , Thermal Zone 1, Outdoors, , SunExposed, WindExposed, , , -0.259, 0.4, 0.7279, -0.259, 0.4, 0.0, -0.259, 2.46, 0.0, -0.259, 2.46, 0.7279;
BuildingSurface:Detailed, z1 Wall 0003, Wall, , Thermal Zone 1, Outdoors, , SunExposed, WindExposed, , , -1.68, 0.4, 0.7279, -1.68, 0.4, 0.0, -0.259, 0.4, 0.0, -0.259, 0.4, 0.7279;
BuildingSurface:Detailed, z1 Wall 0004, Wall, , Thermal Zone 1, Outdoors, , SunExposed, WindExposed, , , -1.68, 2.46, 0.7279, -1.68, 2.46, 0.0, -1.68, 0.4, 0.0, -1.68, 0.4, 0.7279;
BuildingSurface:Detailed, z1 Roof 0001, Roof, , Thermal Zone 1, Outdoors, , SunExposed, WindExposed, , , -0.259, 0.4, 0.7279, -0.259, 2.46, 0.7279, -1.68, 2.46, 0.7279, -1.68, 0.4, 0.7279;
BuildingSurface:Detailed, z2 Floor 0001, Floor, , Thermal Zone 2, Ground, , NoSun, NoWind, , , 0.0, 2.9, 0.7279, 0.0, 0.0, 0.7279, -2.14, 0.0, 0.7279, -2.14, 2.9, 0.7279;
BuildingSurface:Detailed, z2 Wall 0001, Wall, , Thermal Zone 2, Outdoors, , SunExposed, WindExposed, , , -2.14, 0.0, 1.458, -2.14, 0.0, 0.7279, 0.0, 0.0, 0.7279, 0.0, 0.0, 1.458;
BuildingSurface:Detailed, z2 Wall 0002, Wall, , Thermal Zone 2, Outdoors, , SunExposed, WindExposed, , , -2.14, 2.9, 1.458, -2.14, 2.9, 0.7279, -2.14, 0.0, 0.7279, -2.14, 0.0, 1.458;
BuildingSurface:Detailed, z2 Wall 0003, Wall, , Thermal Zone 2, Outdoors, , SunExposed, WindExposed, , , 0.0, 2.9, 1.458, 0.0, 2.9, 0.7279, -2.14, 2.9, 0.7279, -2.14, 2.9, 1.458;
BuildingSurface:Detailed, z2 Wall 0004, Wall, , Thermal Zone 2, Outdoors, , SunExposed, WindExposed, , , 0.0, 0.0, 1.458, 0.0, 0.0, 0.7279, 0.0, 2.9, 0.7279, 0.0, 2.9, 1.458;
BuildingSurface:Detailed, z2 Roof 0001, Roof, , Thermal Zone 2, Outdoors, , SunExposed, WindExposed, , , 0.0, 0.0, 1.458, 0.0, 2.9, 1.458, -2.14, 2.9, 1.458, -2.14, 0.0, 1.458;
"""


def test_intersect():
    poly1 = Polygon3D([(1.0, 2.1, 0.5), (1.0, 2.1, 0.0),
                       (2.0, 2.0, 0.0), (2.0, 2.0, 0.5)])
    poly2 = Polygon3D([(2.5, 1.95, 0.5), (2.5, 1.95, 0.0),
                       (1.5, 2.05, 0.0), (1.5, 2.05, 0.5)])
    intersect = poly1.intersect(poly2)[0]
#    view_polygons({'blue': [poly1, poly2], 'red': [intersect]})
    assert not is_hole(poly1, poly2, intersect)


def test_is_hole():
    """Test if a surface represents a hole in one of the surfaces.
    """
    # opposite faces (all touching edges)
    poly1 = Polygon3D([(0,4,0),(0,0,0),(4,0,0),(4,4,0)])
    poly2 = Polygon3D(reversed([(0,4,0),(0,0,0),(4,0,0),(4,4,0)]))
    intersection = poly1.intersect(poly2)[0]
    assert not is_hole(poly1, poly2, intersection)

    # poly2 is within poly1 and reversed (no touching edges)
    poly1 = Polygon3D([(0,4,0),(0,0,0),(4,0,0),(4,4,0)])
    poly2 = Polygon3D(reversed([(1,3,0),(1,1,0),(3,1,0),(3,3,0)]))
    intersection = poly1.intersect(poly2)[0]
    assert is_hole(poly1, poly2, intersection)

    # poly2 is within poly1 and reversed (touches at x=0)
    poly1 = Polygon3D([(0,4,0),(0,0,0),(4,0,0),(4,4,0)])
    poly2 = Polygon3D(reversed([(0,3,0),(0,1,0),(3,1,0),(3,3,0)]))
    intersection = poly1.intersect(poly2)[0]
    assert not is_hole(poly1, poly2, intersection)

    # poly2 overlaps poly1
    poly1 = Polygon3D([(1,4,0),(1,0,0),(5,0,0),(5,4,0)])
    poly2 = Polygon3D(reversed([(0,3,0),(0,1,0),(3,1,0),(3,3,0)]))
    intersection = poly1.intersect(poly2)[0]
    assert not is_hole(poly1, poly2, intersection)


class TestIntersectMatchRing():
    
    def setup(self):
        iddfhandle = StringIO(iddcurrent.iddtxt)
        if IDF.getiddname() == None:
            IDF.setiddname(iddfhandle)
        
        self.idf = IDF(StringIO(idf_txt_ring))
        
    @pytest.mark.xfail
    def test_intersect_idf_surfaces(self):       
        idf = self.idf        
        starting = len(idf.idfobjects['BUILDINGSURFACE:DETAILED'])
        intersect_idf_surfaces(idf)
#        view_idf(idf_txt=idf.idfstr())
        ending = len(idf.idfobjects['BUILDINGSURFACE:DETAILED'])
        assert starting == 12
        assert ending == 14
        result = [f for f in idf.idfobjects['BUILDINGSURFACE:DETAILED']
                     if f.Name == 'z2 Floor 0001_new_1']
        assert len(result) == 1
        result = [r for r in idf.idfobjects['BUILDINGSURFACE:DETAILED']
                     if r.Name == 'z1 Roof 0001_new_1']
        assert len(result) == 1


class TestIntersectMatch():
    
    def setup(self):
        iddfhandle = StringIO(iddcurrent.iddtxt)
        if IDF.getiddname() == None:
            IDF.setiddname(iddfhandle)
        
        self.idf = IDF(StringIO(idf_txt))
            
    def test_getidfsurfaces(self):    
        idf = self.idf
        surfaces = getidfsurfaces(idf)
        assert len(surfaces) == 12
    
    def test_intersect_idf_surfaces(self):       
        idf = self.idf        
        starting = len(idf.idfobjects['BUILDINGSURFACE:DETAILED'])
        intersect_idf_surfaces(idf)
        ending = len(idf.idfobjects['BUILDINGSURFACE:DETAILED'])
        assert starting == 12
        assert ending == 14

        result = [w for w in idf.idfobjects['BUILDINGSURFACE:DETAILED']
                     if w.Name == 'z1_WALL_0002_new_1']
        assert len(result) == 1
        result = [w for w in idf.idfobjects['BUILDINGSURFACE:DETAILED']
                     if w.Name == 'z2_WALL_0004_new_1']
        assert len(result) == 1

    def test_normalise_coords(self):
        idf = self.idf
        ggr = idf.idfobjects['GLOBALGEOMETRYRULES']
        poly = Polygon3D([(0,0,1), (0,0,0), (1,0,0), (1,0,1)])
        inv_poly = Polygon3D(reversed([(0,0,1), (0,0,0), (1,0,0), (1,0,1)]))
        
        offset_poly = Polygon3D([(1,0,1), (0,0,1), (0,0,0), (1,0,0)])
        inv_offset_poly = Polygon3D(
            reversed([(1,0,1), (0,0,1), (0,0,0), (1,0,0)]))

        entry_direction = 'counterclockwise'
        expected = Polygon3D([(0,0,1), (0,0,0), (1,0,0), (1,0,1)])
        
        # expect no change
        result = poly.normalize_coords(entry_direction, ggr)
        assert result == expected
        
        # expect direction to be reversed
        result = poly.normalize_coords(entry_direction, ggr)
        assert result == expected
        
        entry_direction = 'clockwise'
        result = poly.normalize_coords(entry_direction, ggr)
        expected = inv_poly
        
        # expect no change
        result = poly.normalize_coords(entry_direction, ggr)
        assert result == expected
        
        # expect direction to be reversed
        result = poly.normalize_coords(entry_direction, ggr)
        assert result == expected
        
        entry_direction = 'counterclockwise'
        expected = Polygon3D([(0,0,1), (0,0,0), (1,0,0), (1,0,1)])
        
        # expect to move entry point
        result = poly.normalize_coords(entry_direction, ggr)
        assert result == expected

        # expect direction to reverse and to move entry point
        result = poly.normalize_coords(entry_direction, ggr)
        assert result == expected
                
        entry_direction = 'clockwise'
        expected = inv_poly
        
        # expect to move entry point
        result = poly.normalize_coords(entry_direction, ggr)
        assert result == expected

        # expect direction to reverse and to move entry point
        result = poly.normalize_coords(entry_direction, ggr)
        assert result == expected
        
        
