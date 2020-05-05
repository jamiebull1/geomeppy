.. _next_steps:

Next steps
==========
.. toctree::
   :maxdepth: 2

Introduction
------------
This tutorial continues on from the :ref:`start_here` guide to `geomeppy`. In it you will learn how to add a simple heating system, simulate multiple runs, and view the results of your simulation.

In outline, you will:

1. create a test building with two blocks and three zones

2. add a heating system to service the zones

3. add output variables to measure the energy performance

4. run several simulations while varying the glazing orientation

5. extract and explore the simulation outputs

The building
------------
First we'll build a couple of blocks with default constructions and window-to-wall ratio of 25%.

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

Heating systems
---------------
This is all good, but we're really interested in the energy performance of our building. Lets add a heating system.

    >>> stat = idf.newidfobject(
          "HVACTEMPLATE:THERMOSTAT",
          Name="Zone Stat",
          Constant_Heating_Setpoint=20,
          Constant_Cooling_Setpoint=25,
        )
    >>> for zone in idf.idfobjects["ZONE"]:
          idf.newidfobject(
              "HVACTEMPLATE:ZONE:IDEALLOADSAIRSYSTEM",
              Zone_Name=zone.Name,
              Template_Thermostat_Name=stat.Name,
        )

We'll also add some output variables.

    >>> idf.newidfobject(
            "OUTPUT:VARIABLE",
            Variable_Name="Zone Ideal Loads Supply Air Total Heating Energy",
            Reporting_Frequency="Hourly",
        )
    >>> idf.newidfobject(
            "OUTPUT:VARIABLE",
            Variable_Name="Zone Ideal Loads Supply Air Total Cooling Energy",
            Reporting_Frequency="Hourly",
        )

A small experiment
------------------
To give us something to test out geomeppy, we'll design a test where we explore the effect of moving the glazing from mainly on the North facade, to mainly on the South facade.
    >>> north_wwr = [i / 10 for i in range(1, 10)]
    >>> print(north_wwr)
    [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    >>> south_wwr = [1-wwr for wwr in north_wwr]
    >>> print(south_wwr)
    [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]

These are our window-to-wall ratios for the North and South facades.

    >>> for north, south in zip(north_wwr, south_wwr):
            idf.set_wwr(north, construction="Project External Window", orientation="north")
            idf.set_wwr(south, construction="Project External Window", orientation="south")
            idf.run(
                output_prefix=f"{north}_{south}_",  # so we can tell which files belong to which simulation
                expandobjects=True,  # because we're using HVAC:Template objects
            )

Results
-------
Gathering EnergyPlus results can be a little bit tricky, so here's a little class that we can use to extract total energy use in kWh. It uses the `esoreader` package, and I highly recommend using the `pandas` interface for anything more involved than this little demo.

    >>> class ESO:
            def __init__(self, path):
                self.dd, self.data = esoreader.read(path)

    >>>     def read_var(self, variable, frequency="Hourly"):
                return [
                    {"key": k, "series": self.data[self.dd.index[frequency, k, variable]]}
                    for _f, k, _v in self.dd.find_variable(variable)
                ]

    >>>     def total_kwh(self, variable, frequency="Hourly"):
                j_per_kwh = 3_600_000
                results = self.read_var(variable, frequency)
                return sum(sum(s["series"]) for s in results) / j_per_kwh

Now we'll use the `ESO` class to read in the results of the simulations.

    >>> results = []
    >>> for north, south in zip(north_wwr, south_wwr):
            eso = ESO(f"tests/tutorial/{north}_{south}_out.eso")
            heat = eso.total_kwh("Zone Ideal Loads Supply Air Total Heating Energy")
            cool = eso.total_kwh("Zone Ideal Loads Supply Air Total Cooling Energy")
            results.append([north, south, heat, cool, heat + cool])
            idf.run(output_prefix=f"{north}_{south}_", expandobjects=True)

And print out a table of results.

    >>> headers = ["WWR-N", "WWR-S", "Heat", "Cool", "Total"]
    >>> header_format = "{:>10}" * (len(headers))
    >>> row_format = "{:>10.1f}" * (len(headers))
    >>> print(header_format.format(*headers))
    >>> for row in results:
            print(row_format.format(*row))

.. code::

    WWR-N     WWR-S      Heat      Cool     Total
      0.1       0.9     346.3      81.5     427.9
      0.2       0.8     347.4      79.3     426.7
      0.3       0.7     348.1      77.1     425.2
      0.4       0.6     348.5      75.1     423.5
      0.5       0.5     348.6      73.1     421.7
      0.6       0.4     348.5      71.1     419.6
      0.7       0.3     348.2      69.1     417.3
      0.8       0.2     347.5      67.3     414.8
      0.9       0.1     346.5      65.5     412.0

You can see the annual energy use is lower with more glazing on the North facade and less on the South facade. This is driven by the increase in energy required for cooling when there is more South-facing glazing.

Summary
-------
This tutorial has shown you how to add a heating system to your model, run a set of simulations while changing geometry between each run, and process the results.

So far you've used the default constructions. In the next tutorial you'll find out how to change these and run yet more interesting simulations.

:ref:`constructions`
