"""Tests for fetching surfaces."""
from geomeppy.idf import EpBunch


class TestSurfaces():

    def test_surfaces(self, wwr_idf):
        # type: () -> None
        idf = wwr_idf
        surfaces = idf.getsurfaces()
        assert surfaces
        assert all(isinstance(s, EpBunch) for s in surfaces)

    def test_subsurfaces(self, wwr_idf):
        # type: () -> None
        idf = wwr_idf
        surfaces = idf.getsubsurfaces()
        assert surfaces
        assert all(isinstance(s, EpBunch) for s in surfaces)

    def test_shadingsurfaces(self, base_idf):
        # type: () -> None
        idf = base_idf
        surfaces = idf.getshadingsurfaces()
        assert surfaces
        assert all(isinstance(s, EpBunch) for s in surfaces)
