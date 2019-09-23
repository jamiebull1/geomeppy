import os
import shutil

import pytest

from geomeppy import IDF
from geomeppy.extractor import copy_constructions


@pytest.fixture
def tmp_dir():
    shutil.rmtree("tests/tutorial", ignore_errors=True)
    os.mkdir("tests/tutorial")
    yield
    shutil.rmtree("tests/tutorial")


@pytest.mark.usefixtures("tmp_dir")
def test_tutorial_1():
    IDF.setiddname("C:/EnergyPlusV9-1-0/Energy+.idd", testing=True)
    idf = IDF("C:/EnergyPlusV9-1-0/ExampleFiles/Minimal.idf")
    idf.epw = "USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"
    idf.add_block(
        name="Boring hut", coordinates=[(10, 0), (10, 10), (0, 10), (0, 0)], height=3.5
    )
    idf.intersect_match()
    idf.set_wwr(0.6, construction="Project External Window")
    idf.set_default_constructions()
    idf.to_obj("tests/tutorial/boring_hut.obj")
    idf.run(output_directory="tests/tutorial")


@pytest.mark.usefixtures("tmp_dir")
def test_tutorial_2():
    IDF.setiddname("C:/EnergyPlusV9-1-0/Energy+.idd", testing=True)
    idf = IDF("C:/EnergyPlusV9-1-0/ExampleFiles/Minimal.idf")
    idf.epw = "USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"
    idf.add_block(
        name="Two storey",
        coordinates=[(10, 0), (10, 5), (0, 5), (0, 0)],
        height=6,
        num_stories=2,
    )
    idf.add_block(
        name="One storey", coordinates=[(10, 5), (10, 10), (0, 10), (0, 5)], height=3
    )
    idf.intersect_match()
    idf.set_default_constructions()
    idf.set_wwr(0.25, construction="Project External Window")
    # TODO: add a heating system and some output variables

    idf.run(output_directory="tests/tutorial")
    # TODO: do something with the results


@pytest.mark.usefixtures("tmp_dir")
def test_tutorial_3():
    IDF.setiddname("C:/EnergyPlusV9-1-0/Energy+.idd", testing=True)
    idf = IDF("C:/EnergyPlusV9-1-0/ExampleFiles/Minimal.idf")
    idf.epw = "USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"
    idf.add_block(
        name="Two storey",
        coordinates=[(10, 0), (10, 5), (0, 5), (0, 0)],
        height=6,
        num_stories=2,
    )
    idf.add_block(
        name="One storey", coordinates=[(10, 5), (10, 10), (0, 10), (0, 5)], height=3
    )
    idf.intersect_match()
    idf.set_wwr(0.25, construction="Project External Window")
    idf.set_default_constructions()
    for c in idf.idfobjects["CONSTRUCTION"]:
        print(c)
    print(idf.getobject("MATERIAL", "DefaultMaterial"))
    print(idf.getobject("WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM", "DefaultGlazing"))

    src_idf = IDF("C:/EnergyPlusV9-1-0/ExampleFiles/WindowTestsSimple.idf")
    copy_constructions(source_idf=src_idf, target_idf=idf)
    for c in idf.idfobjects["CONSTRUCTION"]:
        print(c)
    for wall in idf.getsubsurfaces("wall"):
        wall.Construction_Name = "EXTERIOR"
    for roof in idf.getsubsurfaces("roof"):
        roof.Construction_Name = "ROOF31"
    for floor in idf.getsubsurfaces("floor"):
        floor.Construction_Name = "FLOOR38"
    idf.run(output_directory="tests/tutorial")
