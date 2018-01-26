from geomeppy.extractor import copy_constructions, copy_geometry


def test_copy_geometry(extracts_idf):
    idf = copy_geometry(extracts_idf)
    assert idf.getobject('ZONE', 'z1 Thermal Zone')
    assert not idf.getobject('MATERIAL', 'Spam')


def test_copy_constructions(extracts_idf):
    idf = copy_constructions(extracts_idf)
    assert not idf.getobject('ZONE', 'z1 Thermal Zone')
    assert idf.getobject('MATERIAL', 'Spam')
