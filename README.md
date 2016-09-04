GeomEppy
========
[![PyPI](https://img.shields.io/pypi/dm/geomeppy.svg)](https://pypi.python.org/pypi/geomeppy)
 from PyPI

[![Build Status](https://travis-ci.org/jamiebull1/geomeppy.svg?branch=master)](https://travis-ci.org/jamiebull1/geomeppy)
 for Python 2.7 on Linux via Travis

[![CodeCov](https://img.shields.io/codecov/c/github/jamiebull1/geomeppy/master.svg)](https://codecov.io/github/santoshphilip/eppy)
 via CodeCov

GeomEppy is a scripting language for use with Eppy, which in turn is a scripting language for EnergyPlus IDF files and output files.

##API

The API for GeomEppy depends on replacing an Eppy IDF object with a GeomEppy IDF object. To use this, you will need to import IDF from GeomEppy rather than directly from Eppy.

In your scripts, use `from geomeppy import IDF` instead of `from eppy.modeleditor import IDF`. All other features of the current release version of Eppy will still be available.

GeomEppy then provides a simple Python API for actions on an Eppy IDF object:

- Intersecting and matching surfaces

`IDF.intersect()  # intersects all surfaces`

`IDF.match()  # sets boundary conditions of surfaces`

`IDF.intersect_match()  # intersect surfaces then set/update boundary conditions

- Adding windows to external walls

`IDF.set_wwr(wwr=0.25)  # set a WWR of 25% for all external walls`

- Viewing a simple 3D representation of an IDF

`IDF.view_model()  # shows a zoomable, rotatable transparent model`

`IDF.add_block(...)  # automatically adds a building block to the IDF`

This method requires some explanation. The parameters required are:

    coordinates : list
        A list of (x, y) tuples representing the building outline.
    height : float
        The height of the block roof above ground level.
    num_stories : int, optional
        The total number of stories including basement stories. Default : 1.
    below_ground_stories : int, optional
        The number of stories below ground. Default : 0.
    below_ground_storey_height : float, optional
        The height of each basement storey. Default : 2.5.
	zoning : str, optional
		The rules to use in creating zones. Currently the only option is
		`by_storey` which sets each storey in the block as a Zone.

The block generated will have boundary conditions set correctly and any intersections with adjacent blocks will be handled automatically.
The surface type will be set to `wall`, `floor`, `ceiling` or `roof` for each surface.
Constructions are not set automatically so these will need to be added afterwards in the normal way for Eppy.

GeomEppy also provides some additional functions such as `surface.setcoords(...)`


##Forthcoming

- Scaling and rotating buildings and blocks
- Geometry validation and correction
- Geometry simplification
- Better geometry visualisation

##Installation

Installing GeomEppy for Python 2.7 is a simple as calling `pip install geomeppy`.

Python 3 is currently unsupported while we await a fully-compatible version of Eppy to be released to PyPI.
