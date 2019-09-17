import os
import shutil

import pytest

from geomeppy import IDF


@pytest.fixture
def tmp_dir():
    os.mkdir("tests/tutorial")
    yield
    shutil.rmtree("tests/tutorial")


@pytest.mark.usefixtures("tmp_dir")
def test_tutorial():
    IDF.setiddname("C:/EnergyPlusV9-1-0/Energy+.idd", testing=True)
    idf = IDF("C:/EnergyPlusV9-1-0/ExampleFiles/Minimal.idf")
    idf.epw = "USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"
    idf.add_block(
        name="Boring hut", coordinates=[(10, 0), (10, 10), (0, 10), (0, 0)], height=3.5
    )
    idf.set_default_constructions()
    idf.intersect_match()
    idf.set_wwr(0.6, construction="Project External Window")
    idf.to_obj("tests/tutorial/boring_hut.obj")
    idf.run(output_directory="tests/tutorial")
