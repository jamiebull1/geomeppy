Start here
==========
.. toctree::
   :maxdepth: 2

This tutorial is intended as a walk-through for complete beginners to `geomeppy`.

At the end of the tutorial, you will have created and run an EnergyPlus model without once
having to manually edit an `.idf` file, without creating geometry in SketchUp, and without any other
such hassles.

In outline, you will:

1. create a virtual environment and install `geomeppy`

2. install EnergyPlus (if you haven't already)

3. create a simple test building

4. add some windows

5. set the constructions and boundary conditions

6. view the model in 3D

7. run a simulation in EnergyPlus

Installation
------------

First we need to set up a virtual environment to keep this Python environment separate from any
other installations on your machine. This tutorial assumes you're using Python 3 so make sure you have that installed.

.. code::

    $ mkdir tutorial
    $ cd tutorial
    $ python3 -m venv venv

Now we activate the virtual environment.

.. code::

    $ source venv/bin/activate

And install `geomeppy`.

.. code::

    (venv)$ pip3 install geomeppy

This will take a while to install the `geomeppy` package and its dependencies. While it's installing, we can move on to installing EnergyPlus if you don't already have it installed.

The EnergyPlus installers can be found on the `energyplus.net <https://energyplus.net/downloads>`_ site. Choose the correct package for your platform and install it.

Creating a model
----------------

Next we want to create our basic model, so we'll open a Python interpreter.

.. code::

    (venv)$ python3

From now on, we're working in the Python interpreter, indicated by the ``>>>`` prompt.

Be aware that this tutorial is written for the Mac and for EnergyPlus 9.1.0.

If you are on Windows or Linux machine or have a different version of EnergyPlus installed, you'll need to replace the path to the EnergyPlus installation folder with the appropriate path.

For example, on Windows, this is usually ``C:/EnergyPlusV9-1-0``, and on Linux, ``/usr/local/EnergyPlus-9-1-0``.

    >>> from geomeppy import IDF
    >>> IDF.setiddname('/Applications/EnergyPlus-9-1-0/Energy+.idd')
    >>> idf = IDF('/Applications/EnergyPlus-9-1-0/ExampleFiles/Minimal.idf')

Now we have imported an EnergyPlus IDF file which contains the bare minimum required to be able to run successfully. We need to add a weather file to our IDF object first though.

    >>> idf.epw = 'USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw'

Now we have assigned an EPW format weather file to the IDF. This will tell EnergyPlus about the weather conditions to simulate.

So far, this is the same as using `eppy`, but now we are getting to the `geomeppy` part where we can generate and manipulate the IDF geometry. First off, let's add a simple square block.

    >>> idf.add_block(
            name='Boring hut',
            coordinates=[(10,0),(10,10),(0,10),(0,0)],
            height=3.5)

Next we can set some default constructions for the IDF surfaces.

    >>> idf.set_default_constructions()

Now we need to tell `geomeppy` to match up our surfaces with the correct outside conditions. In this case, it will just set the outside boundary conditions for all the walls and roof to "outside", and that of the floor to "ground".

    >>> idf.intersect_match()

Last step, let's add some nice big windows. We'll set window to wall ratio (WWR) of 0.6 for all external walls.

    >>> idf.set_wwr(0.6)

So what have we built? We can export the IDF geometry as an OBJ file, a format that can be imported into a 3D geometry viewer.

    >>> idf.to_obj('boring_hut.obj')

Try dragging the 'boring_hut.obj' file and 'boring_hut.mtl' file to `3D Viewer <https://3dviewer.net/>`_ to see your "Boring hut" in glorious interactive 3D.

And now, the moment you've been working towards all this time...

    >>> idf.run()

You should see an output something like the following:

.. code::

    C:\EnergyPlusV9-1-0\energyplus.exe --idd C:/EnergyPlusV9-1-0/Energy+.idd --output-directory C:\Users\jamie\geomeppy --weather C:\EnergyPlusV9-1-0\WeatherData\USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw C:\Users\jamie\geomeppy\in.idf
    
    EnergyPlus Starting
    EnergyPlus, Version 9.1.0-08d2e308bb, YMD=2019.09.17 10:11
    Adjusting Air System Sizing
    Adjusting Standard 62.1 Ventilation Sizing
    Initializing Simulation
    Reporting Surfaces
    Beginning Primary Simulation
    Initializing New Environment Parameters
    Warming up {1}
    Warming up {2}
    Warming up {3}
    Warming up {4}
    Warming up {5}
    Warming up {6}
    Starting Simulation at 12/21 for DENVER_STAPLETON ANN HTG 99.6% CONDNS DB
    Initializing New Environment Parameters
    Warming up {1}
    Warming up {2}
    Warming up {3}
    Warming up {4}
    Warming up {5}
    Warming up {6}
    Starting Simulation at 07/21 for DENVER_STAPLETON ANN CLG .4% CONDNS DB=>MWB
    Writing tabular output file results using HTML format.
    Writing final SQL reports
    EnergyPlus Run Time=00hr 00min  0.53sec
    EnergyPlus Completed Successfully.

This indicates that EnergyPlus has run successfully.

It's not very exciting, since we haven't added any heating or cooling systems, or output variables. Geomeppy is a geometry package after all!

But in the next tutorial, we'll add a heating system, while also learning about some of the other features of `geomeppy`.

Coming soon...