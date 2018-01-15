"""pytest for shading blocks"""
from eppy.iddcurrent import iddcurrent
from six import StringIO

from geomeppy.idf import IDF
from tests.test_builder import idf_txt


idf_txt = """
Version, 8.5;
"""


class TestAddShadingBlock():

    def setup(self):
        # type: () -> None
        iddfhandle = StringIO(iddcurrent.iddtxt)
        if IDF.getiddname() == None:
            IDF.setiddname(iddfhandle)
        
        self.idf = IDF(StringIO(idf_txt))

    def test_add_shading_block_smoke_test(self):
        # type: () -> None
        idf = self.idf
        name = "test"
        height = 7.5
        coordinates = [
            (87.25,24.0),(91.7,25.75),(90.05,30.25),
            (89.55,31.55),(89.15,31.35),(85.1,29.8),
            (86.1,27.2),(84.6,26.65),(85.8,23.5),
            (87.25,24.0)]
        idf.add_shading_block(name, coordinates, height)
        
        
