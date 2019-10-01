import os
from geomeppy.io.obj import export_to_obj

EXAMPLES_DIR = "C:/EnergyPlusV9-1-0/ExampleFiles"


def test_export_to_obj(base_idf):
    export_to_obj(base_idf, "test.obj")
    assert os.path.isfile("test.obj")
    assert os.path.isfile("test.mtl")
    os.remove("test.obj")
    os.remove("test.mtl")
