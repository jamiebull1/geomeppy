.. _next_steps:

Next steps
==========
.. toctree::
   :maxdepth: 2

Introduction
------------
This tutorial continues on from the :ref:`start_here` guide to `geomeppy`. In it you will learn how to add a simple heating system, and view the results of your simulation.

In outline, you will:

1. create a test building with two blocks and three zones

2. add a heating system to service the zones

3. add output variables to measure the energy performance

4. run the simulation

5. view the simulation outputs

The building
------------
First we'll build a couple of blocks with default constructions and window-to-wall ratio of 25%.

    >>> from geomeppy import IDF
    >>> IDF.setiddname("C:/EnergyPlusV9-1-0/Energy+.idd")
    >>> idf = IDF("C:/EnergyPlusV9-1-0/ExampleFiles/Minimal.idf")
    >>> idf.epw = "USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"
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

Heating systems
---------------
This is all good, but we're really interested in the energy performance of our building. Lets add a heating system.

TODO: add a heating system

Results
-------
TODO: add output variables
TODO: run the simulation
TODO: read the results

Summary
-------
This tutorial has shown you how to add a heating system to your model, and get some results.

So far you've used the default constructions. In the next tutorial you'll find out how to change these and run some more interesting simulations.

:ref:`constructions`
