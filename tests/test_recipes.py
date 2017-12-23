# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""pytest for recipes.py"""

from eppy.iddcurrent import iddcurrent
import pytest
from six import StringIO

from geomeppy.eppy_patches import IDF
from geomeppy.geom.intersect_match import getidfsurfaces, intersect_idf_surfaces, match_idf_surfaces
from geomeppy.geom.polygons import Polygon3D
from geomeppy.geom.vectors import Vector2D, Vector3D
from geomeppy.recipes import rotate, set_wwr, translate, translate_to_origin
from geomeppy.utilities import almostequal

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


class TestTranslate():
    
    def setup(self):
        # type: () -> None
        iddfhandle = StringIO(iddcurrent.iddtxt)
        if IDF.getiddname() == None:
            IDF.setiddname(iddfhandle)
        
        self.idf = IDF(StringIO(idf_txt))
            
    def test_translate(self):
        # type: () -> None
        idf = self.idf
        surfaces = getidfsurfaces(idf)
        translate(surfaces, (50, 100))  # move to x + 50, y + 100
        result = Polygon3D(surfaces[0].coords).xs
        expected = [52.0, 52.0, 51.0, 51.0]
        assert result == expected
        translate(surfaces, (-50, -100))  # move back
        
        translate(surfaces, Vector2D(50, 100))  # move to x + 50, y + 100
        result = Polygon3D(surfaces[0].coords).xs
        expected = [52.0, 52.0, 51.0, 51.0]
        assert result == expected
        translate(surfaces, (-50, -100))  # move back
        
        translate(surfaces, Vector3D(50, 100, 0))  # move to x + 50, y + 100
        result = Polygon3D(surfaces[0].coords).xs
        expected = [52.0, 52.0, 51.0, 51.0]
        assert result == expected

    def test_translate_to_origin(self):
        # type: () -> None
        idf = self.idf
        surfaces = getidfsurfaces(idf)
        translate(surfaces, (50000, 10000))  # move to x + 50, y + 100
        result = Polygon3D(surfaces[0].coords).xs
        expected = [50002.0, 50002.0, 50001.0, 50001.0]
        assert result == expected

        translate_to_origin(idf)
        surfaces = getidfsurfaces(idf)
        min_x = min(min(Polygon3D(s.coords).xs) for s in surfaces)
        min_y = min(min(Polygon3D(s.coords).ys) for s in surfaces)
        assert min_x == 0
        assert min_y == 0

    def test_rotate_360(self):
        # type: () -> None
        idf = self.idf
        surface = getidfsurfaces(idf)[0]
        coords = [Vector3D(*v) for v in [(0,0,0), (1,0,0), (1,1,0), (0,1,0)]]
        surface.setcoords(coords)
        expected = surface.coords
        rotate([surface], 360)
        result = surface.coords
        assert almostequal(result, expected)

    def test_rotate_idf_360(self):
        # type: () -> None
        idf1 = self.idf
        idf2 = IDF()
        idf2.initreadtxt(idf1.idfstr())
        idf1.rotate(360)
        floor1 = Polygon3D(idf1.getsurfaces('floor')[0].coords).normalize_coords(None)
        floor2 = Polygon3D(idf2.getsurfaces('floor')[0].coords).normalize_coords(None)
        assert almostequal(floor1, floor2)

    def test_centre(self):
        # type: () -> None
        idf = self.idf
        result = idf.centroid
        expected = Vector2D(1.75, 2.025)
        assert result == expected

    def test_scale_idf(self):
        # type: () -> None
        idf1 = self.idf
        idf2 = IDF()
        idf2.initreadtxt(idf1.idfstr())
        idf1.scale(10)
        idf1.scale(0.1)
        floor1 = Polygon3D(idf1.getsurfaces('floor')[0].coords).normalize_coords(None)
        floor2 = Polygon3D(idf2.getsurfaces('floor')[0].coords).normalize_coords(None)
        assert almostequal(floor1, floor2)


class TestMatchSurfaces():

    def setup(self):
        # type: () -> None
        IDF.iddname == None
        iddfhandle = StringIO(iddcurrent.iddtxt)
        IDF.setiddname(iddfhandle, testing=True)
        self.idf = IDF(StringIO(idf_txt))
        intersect_idf_surfaces(self.idf)
        match_idf_surfaces(self.idf)
            
    def test_set_wwr(self):
        # type: () -> None
        """Check that the correct WWR is set for all walls.
        """
        idf = self.idf
        wwr = 0.25
        set_wwr(idf, wwr)
        windows = idf.idfobjects['FENESTRATIONSURFACE:DETAILED']
        assert len(windows) == 8
        for window in windows:
            wall = idf.getobject('BUILDINGSURFACE:DETAILED',
                                 window.Building_Surface_Name)
            assert almostequal(window.area, wall.area * wwr, 3)


@pytest.fixture()
def new_idf():
    IDF.iddname == None
    iddfhandle = StringIO(iddcurrent.iddtxt)
    IDF.setiddname(iddfhandle, testing=True)
    idf = IDF()
    idf.new()
    return idf

@pytest.fixture()
def wwr_idf(new_idf):
    new_idf.newidfobject(
        'FENESTRATIONSURFACE:DETAILED',
        Name='window1',
        Surface_Type='window',
        Construction_Name='ExtWindow',
        Building_Surface_Name='wall1',
    )
    wall = new_idf.newidfobject(
        'BUILDINGSURFACE:DETAILED',
        Name='wall1',
        Surface_Type='wall',
        Outside_Boundary_Condition='Outdoors',

    )
    wall.setcoords([[0,0,0], [0,1,0], [0,1,1], [0,0,1]])

    return new_idf


class TestWWR:

    def is_expected_wwr(self, idf, wwr):
        windows_area = sum(w.area for w in idf.getsubsurfaces('window'))
        walls_area = sum(w.area for w in idf.getsurfaces('wall'))
        return almostequal(windows_area, walls_area * wwr, 3)

    def test_wwr(self, wwr_idf):
        idf = wwr_idf
        wwr = 0.2
        idf.set_wwr(wwr)
        assert self.is_expected_wwr(idf, wwr)

    def test_wwr_two_window_constructions(self, wwr_idf):
        idf = wwr_idf
        idf.newidfobject(
            'FENESTRATIONSURFACE:DETAILED',
            Name='window2',
            Surface_Type='window',
            Construction_Name='ExtWindow2',
            Building_Surface_Name='wall1',
        )
        wwr = 0.2
        try:
            idf.set_wwr(wwr)
            assert False, 'Should have raised an error since windows with more than one construction are present'
        except ValueError:
            pass
        idf.set_wwr(wwr, construction='ExtWindow')
        assert self.is_expected_wwr(idf, wwr)

    def test_wwr_mixed_subsurfaces(self, wwr_idf):
        idf = wwr_idf
        idf.newidfobject(
            'DOOR',
            Name='door1',
            Construction_Name='ExtDoor',
            Building_Surface_Name='wall1',
        )
        wwr = 0.2
        try:
            idf.set_wwr(wwr)
            assert False, 'Should have raised an error since not all subsurfaces are windows'
        except ValueError:
            pass
        idf.set_wwr(wwr, force=True)
        assert self.is_expected_wwr(idf, wwr)
