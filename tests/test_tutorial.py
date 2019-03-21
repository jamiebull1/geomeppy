from geomeppy import IDF


def test_tutorial():
    IDF.setiddname("C:/EnergyPlusV8-8-0/Energy+.idd")
    idf = IDF("C:/EnergyPlusV8-8-0/ExampleFiles/Minimal.idf")
    idf.epw = "USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"
    idf.add_block(
        name="Boring hut", coordinates=[(10, 0), (10, 10), (0, 10), (0, 0)], height=3.5
    )
    idf.set_default_constructions()
    idf.intersect_match()
    idf.set_wwr(0.6, construction="Project External Window")
    idf.to_obj("boring_hut.obj")
    idf.run()
