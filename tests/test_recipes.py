"""Tests for recipes."""
from geomeppy.idf import IDF
from geomeppy.geom.intersect_match import intersect_idf_surfaces, match_idf_surfaces
from geomeppy.geom.polygons import Polygon3D
from geomeppy.geom.vectors import Vector2D, Vector3D
from geomeppy.recipes import rotate, set_wwr, translate, translate_to_origin
from geomeppy.utilities import almostequal
from geomeppy.view_geometry import _get_collections, _get_shading, _get_surfaces


class TestTranslate():
    
    def test_translate(self, base_idf):
        # type: () -> None
        idf = base_idf
        surfaces = idf.getsurfaces()
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

    def test_translate_to_origin(self, base_idf):
        # type: () -> None
        idf = base_idf
        surfaces = idf.getsurfaces()
        translate(surfaces, (50000, 10000))  # move to x + 50, y + 100
        result = Polygon3D(surfaces[0].coords).xs
        expected = [50002.0, 50002.0, 50001.0, 50001.0]
        assert result == expected

        translate_to_origin(idf)
        surfaces = idf.getsurfaces()
        min_x = min(min(Polygon3D(s.coords).xs) for s in surfaces)
        min_y = min(min(Polygon3D(s.coords).ys) for s in surfaces)
        assert min_x == 0
        assert min_y == 0

    def test_rotate_360(self, base_idf):
        # type: () -> None
        idf = base_idf
        surface = idf.getsurfaces()[0]
        coords = [Vector3D(*v) for v in [(0,0,0), (1,0,0), (1,1,0), (0,1,0)]]
        surface.setcoords(coords)
        expected = surface.coords
        rotate([surface], 360)
        result = surface.coords
        assert almostequal(result, expected)

    def test_rotate_idf_360(self, base_idf):
        # type: () -> None
        idf1 = base_idf
        idf2 = IDF()
        idf2.initreadtxt(idf1.idfstr())
        idf1.rotate(360)
        floor1 = Polygon3D(idf1.getsurfaces('floor')[0].coords).normalize_coords(None)
        floor2 = Polygon3D(idf2.getsurfaces('floor')[0].coords).normalize_coords(None)
        assert almostequal(floor1, floor2)
        shade1 = Polygon3D(idf1.getshadingsurfaces()[0].coords).normalize_coords(None)
        shade2 = Polygon3D(idf1.getshadingsurfaces()[0].coords).normalize_coords(None)
        assert almostequal(shade1, shade2)

    def test_centre(self, base_idf):
        # type: () -> None
        idf = base_idf
        result = idf.centroid
        expected = Vector2D(1.75, 2.025)
        assert result == expected

    def test_scale_idf(self, base_idf):
        # type: () -> None
        idf1 = base_idf
        idf2 = IDF()
        idf2.initreadtxt(idf1.idfstr())
        idf1.scale(10)
        idf1.scale(0.1)
        floor1 = Polygon3D(idf1.getsurfaces('floor')[0].coords).normalize_coords(None)
        floor2 = Polygon3D(idf2.getsurfaces('floor')[0].coords).normalize_coords(None)
        assert almostequal(floor1, floor2)


class TestMatchSurfaces():

    def test_set_wwr(self, base_idf):
        # type: () -> None
        idf = base_idf
        intersect_idf_surfaces(idf)
        match_idf_surfaces(idf)
        wwr = 0.25
        set_wwr(idf, wwr)
        windows = idf.idfobjects['FENESTRATIONSURFACE:DETAILED']
        assert len(windows) == 8
        for window in windows:
            wall = idf.getobject('BUILDINGSURFACE:DETAILED',
                                 window.Building_Surface_Name)
            assert almostequal(window.area, wall.area * wwr, 3)


class TestViewGeometry():

    def test_get_surfaces(self, base_idf):
        # type: () -> None
        idf = base_idf
        surfaces = _get_surfaces(idf)
        assert len(surfaces) == 12

    def test_get_shading(self, base_idf):
        # type: () -> None
        idf = base_idf
        shading = _get_shading(idf)
        assert len(shading) == 1

    def test_get_collections(self, base_idf):
        # type: () -> None
        idf = base_idf
        collections = _get_collections(idf)
        assert len(collections) == 5
        for c in collections:
            assert c

    def test_view_model(self, base_idf):
        # type: () -> None
        idf = base_idf
        idf.view_model(test=True)


class TestWWR:

    def is_expected_wwr(self, idf, wwr):
        windows_area = sum(w.area for w in idf.getsubsurfaces('window'))
        walls_area = sum(w.area for w in idf.getsurfaces('wall'))
        expected_area = walls_area * wwr
        return almostequal(windows_area, expected_area, 3)

    def test_wwr(self, wwr_idf):
        idf = wwr_idf
        wwr = 0.2
        idf.set_wwr(wwr)
        assert self.is_expected_wwr(idf, wwr), 'Not all walls have the expected WWR set'

    def test_wwr_map(self, wwr_idf):
        idf = wwr_idf
        expected_wwr = 0.2
        idf.set_wwr(wwr=0.99, wwr_map={90.0: 0.1, 180: 0.3})
        assert self.is_expected_wwr(idf, expected_wwr), 'Not all walls have the expected WWR set'

    def test_wwr_zero(self, wwr_idf):
        idf = wwr_idf
        idf.set_wwr(wwr=0, wwr_map={90.0: 0.1})
        expected_wwr = 0.05
        assert self.is_expected_wwr(idf, expected_wwr), 'Not all walls have the expected WWR set'

    def test_wwr_none(self, wwr_idf):
        idf = wwr_idf
        idf.set_wwr(wwr=None, wwr_map={90.0: 0.3})
        expected_wwr = 0.15
        assert self.is_expected_wwr(idf, expected_wwr), 'Not all walls have the expected WWR set'

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

    def test_wwr_by_orientation(self, wwr_idf):
        idf = wwr_idf
        idf.set_wwr(wwr=0.2, orientation='south')  # there is a south-facing wall
        idf.set_wwr(wwr=0.2, orientation='west')  # there is no west-facing wall
        expected_wwr = 0.1
        assert self.is_expected_wwr(idf, expected_wwr), 'WWR not set correctly by orientation'
