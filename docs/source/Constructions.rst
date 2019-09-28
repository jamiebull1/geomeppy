.. _constructions:

Constructions
=============
.. toctree::
   :maxdepth: 2

Introduction
------------
TODO: add an outline of the tutorial

The building
------------
We'll use the same building as in the previous tutorial.

    >>> from geomeppy import IDF
    >>> IDF.setiddname("C:/EnergyPlusV9-1-0/Energy+.idd")
    >>> idf = IDF("C:/EnergyPlusV9-1-0/ExampleFiles/Minimal.idf")
    >>> idf.epw = "USA_CO_Golden-NREL.724666_TMY3.epw"
    >>> idf.add_block(
          name='Two storey',
          coordinates=[(10,0),(10,5),(0,5),(0,0)],
          height=6,
          num_stories=2,
        )
    >>> idf.add_block(
          name='One storey',
          coordinates=[(10,5),(10,10),(0,10),(0,5)],
          height=3,
        )
    >>> idf.intersect_match()
    >>> idf.set_default_constructions()
    >>> idf.set_wwr(0.25, construction="Project External Window")

Viewing constructions
---------------------

Next we'll take a look at some of the constructions.

    >>> for c in idf.idfobjects["CONSTRUCTION"]:
            print(c)
    CONSTRUCTION,
        Project Wall,             !- Name
        DefaultMaterial;          !- Outside Layer
    CONSTRUCTION,
        Project Partition,        !- Name
        DefaultMaterial;          !- Outside Layer
    CONSTRUCTION,
        Project Floor,            !- Name
        DefaultMaterial;          !- Outside Layer
    CONSTRUCTION,
        Project Flat Roof,        !- Name
        DefaultMaterial;          !- Outside Layer
    CONSTRUCTION,
        Project Ceiling,          !- Name
        DefaultMaterial;          !- Outside Layer
    CONSTRUCTION,
        Project Door,             !- Name
        DefaultMaterial;          !- Outside Layer
    CONSTRUCTION,
        Project External Window,    !- Name
        DefaultGlazing;           !- Outside Layer

Ah. So what do these "DefaultMaterial" and "DefaultGlazing" look like?

    >>> idf.getobject("MATERIAL", "DefaultMaterial")
    MATERIAL,
        DefaultMaterial,          !- Name
        Rough,                    !- Roughness
        0.1,                      !- Thickness
        0.1,                      !- Conductivity
        1000,                     !- Density
        1000,                     !- Specific Heat
        0.9,                      !- Thermal Absorptance
        0.7,                      !- Solar Absorptance
        0.7;                      !- Visible Absorptance

    >>> idf.getobject("WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM", "DefaultGlazing")
    WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM,
    DefaultGlazing,           !- Name
    2.7,                      !- UFactor
    0.763,                    !- Solar Heat Gain Coefficient
    0.8;                      !- Visible Transmittance

Well the window looks OK, but those "DefaultMaterial"s should definitely be replaced with something better.

Importing constructions
-----------------------

We can import constructions from another IDF. For this tutorial, we'll fetch the ones from "WindowTestsSimple.idf".

    >>> src_idf = IDF("C:/EnergyPlusV9-1-0/ExampleFiles/WindowTestsSimple.idf")
    >>> copy_constructions(source_idf=src_idf, target_idf=idf)

Now we can assign some of those constructions to our IDF.

    >>> for wall in idf.getsubsurfaces("wall"):
            wall.Construction_Name = "EXTERIOR"
    >>> for roof in idf.getsubsurfaces("roof"):
            roof.Construction_Name = "ROOF31"
    >>> for floor in idf.getsubsurfaces("floor"):
            floor.Construction_Name = "FLOOR38"

And run the simulation.

    >>> idf.run(output_directory="tests/tutorial")


Summary
-------
TODO: add a summary of the contents
