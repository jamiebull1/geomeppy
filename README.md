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

GeomEppy provides a simple Python API for actions on an Eppy IDF object:

- Intersecting surfaces

`geomeppy.intersect_idf_surfaces(idf)  # intersects all surfaces`

- Matching surfaces

`geomeppy.match_idf_surfaces(idf)  # sets boundary conditions of surfaces`

- Adding windows to external walls

`geomeppy.set_wwr(idf, wwr=0.25)  # set a WWR of 25%`

- Viewing a simple 3D representation of an IDF

`geomeppy.view_idf(idf)  # shows a zoomable, rotatable transparent model`

GeomEppy also provides some additional functions such as `surface.setcoords(...)`

To use this, you will need to import IDF from GeomEppy rather than directly from Eppy.

In your scripts, use `from geomeppy import IDF` instead of `from eppy.modeleditor import IDF`. All other features of the current release
version of Eppy will still be available.

##Forthcoming

- Automated creation of IDF geometry
- Scaling and rotating buildings and blocks
- Geometry validation and correction
- Geometry simplification
- Better geometry visualisation

##Installation

Installing GeomEppy for Python 2.7 is a simple as calling `pip install geomeppy`.

Python 3 is currently unsupported while we await an updated version of Eppy to be released to PyPI.
