import os

from geomeppy import IDF
from geomeppy.io.obj import export_to_obj
EXAMPLES_DIR = "C:/EnergyPlusV9-1-0/ExampleFiles"

def _test_export_to_obj(base_idf):
    export_to_obj(base_idf, "test.obj")
    assert os.path.isfile("test.obj")
    assert os.path.isfile("test.mtl")
    os.remove("test.obj")
    os.remove("test.mtl")


def test_example_file():
    # src_idf = "1ZoneDataCenterCRAC_wApproachTemp.idf"
    # src_idf = "SurfaceTest.idf"
    src_idf = "BaseBoardElectric.idf"
    IDF.setiddname("C:/EnergyPlusV9-0-1/Energy+.idd", testing=True)
    idf = IDF(os.path.join(EXAMPLES_DIR, src_idf))
    idf.intersect_match()
    # idf.printidf()
    assert not idf.idfobjects["PARAMETRIC:LOGIC"]
    # idf.save_view(fname=f"test_images/{name}.png")
    idf.to_obj(fname=f"C:/Users/jamie/VSCodeProjects/geomeppy-viewer/src/assets/{src_idf}.obj")
