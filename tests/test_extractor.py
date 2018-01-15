from eppy.iddcurrent import iddcurrent
import pytest
from six import StringIO

from geomeppy.idf import IDF
from geomeppy.extractor import copy_constructions, copy_geometry

idf_txt = """
Version, 8.8;
Zone, z1 Thermal Zone, 0.0, 0.0, 0.0, 0.0, , 1, , , , , , Yes;
Material, Spam, Rough, 0.1, 1, 1000, 1000, 0.9, 0.9, 0.9;
"""

@pytest.fixture()
def base_idf():
    # type: () -> None
    iddfhandle = StringIO(iddcurrent.iddtxt)
    if IDF.getiddname() == None:
        IDF.setiddname(iddfhandle)

    return IDF(StringIO(idf_txt))


def test_copy_geometry(base_idf):
    idf = copy_geometry(base_idf)
    assert idf.getobject('ZONE', 'z1 Thermal Zone')
    assert not idf.getobject('MATERIAL', 'Spam')


def test_copy_constructions(base_idf):
    idf = copy_constructions(base_idf)
    assert not idf.getobject('ZONE', 'z1 Thermal Zone')
    assert idf.getobject('MATERIAL', 'Spam')
