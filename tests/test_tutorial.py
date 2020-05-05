import os
import shutil

import esoreader
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
    idf.epw = "USA_CO_Golden-NREL.724666_TMY3.epw"
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
    idf.epw = "USA_CO_Golden-NREL.724666_TMY3.epw"
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
    # add a heating system
    stat = idf.newidfobject(
        "HVACTEMPLATE:THERMOSTAT",
        Name="Zone Stat",
        Constant_Heating_Setpoint=20,
        Constant_Cooling_Setpoint=25,
    )
    for zone in idf.idfobjects["ZONE"]:
        idf.newidfobject(
            "HVACTEMPLATE:ZONE:IDEALLOADSAIRSYSTEM",
            Zone_Name=zone.Name,
            Template_Thermostat_Name=stat.Name,
        )
    # add some output variables
    idf.newidfobject(
        "OUTPUT:VARIABLE",
        Variable_Name="Zone Ideal Loads Supply Air Total Heating Energy",
        Reporting_Frequency="Hourly",
    )
    idf.newidfobject(
        "OUTPUT:VARIABLE",
        Variable_Name="Zone Ideal Loads Supply Air Total Cooling Energy",
        Reporting_Frequency="Hourly",
    )
    # run a set of simulations, moving glazing from mostly on the South facade, to mostly on the North facade
    north_wwr = [i / 10 for i in range(1, 10)]
    south_wwr = [1 - wwr for wwr in north_wwr]
    for north, south in zip(north_wwr, south_wwr):
        idf.set_wwr(north, construction="Project External Window", orientation="north")
        idf.set_wwr(south, construction="Project External Window", orientation="south")
        idf.run(
            output_prefix=f"{north}_{south}_",
            output_directory="tests/tutorial",
            expandobjects=True,
            verbose="q",
        )
    results = []
    for north, south in zip(north_wwr, south_wwr):
        eso = ESO(f"tests/tutorial/{north}_{south}_out.eso")
        heat = eso.total_kwh("Zone Ideal Loads Supply Air Total Heating Energy")
        cool = eso.total_kwh("Zone Ideal Loads Supply Air Total Cooling Energy")
        results.append([north, south, heat, cool, heat + cool])
    # print out the results
    headers = ["WWR-N", "WWR-S", "Heat", "Cool", "Total"]
    header_format = "{:>10}" * (len(headers))
    print(header_format.format(*headers))
    row_format = "{:>10.1f}" * (len(headers))
    for row in results:
        print(row_format.format(*row))


class ESO:
    def __init__(self, path):
        self.dd, self.data = esoreader.read(path)

    def read_var(self, variable, frequency="Hourly"):
        return [
            {"key": k, "series": self.data[self.dd.index[frequency, k, variable]]}
            for _f, k, _v in self.dd.find_variable(variable)
        ]

    def total_kwh(self, variable, frequency="Hourly"):
        j_per_kwh = 3_600_000
        results = self.read_var(variable, frequency)
        return sum(sum(s["series"]) for s in results) / j_per_kwh


@pytest.mark.usefixtures("tmp_dir")
def test_tutorial_3():
    IDF.setiddname("C:/EnergyPlusV9-1-0/Energy+.idd", testing=True)
    idf = IDF("C:/EnergyPlusV9-1-0/ExampleFiles/Minimal.idf")
    idf.epw = "USA_CO_Golden-NREL.724666_TMY3.epw"
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
