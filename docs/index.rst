.. geomeppy documentation master file, created by
   sphinx-quickstart on Wed Dec  6 21:55:03 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to geomeppy's documentation!
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

geomeppy
========

GeomEppy is a scripting language for use with Eppy, which in turn is a scripting language for EnergyPlus IDF files and output files.

It primarily adds functions to do with IDF geometry, including zones, surfaces, constructions, etc.

Features
--------

- Auto-add blocks to your IDF
- Intersect and match block surfaces
- Move blocks
- Automatically set window-to-wall ratio
- View a simple model of the geometry

Installation
------------

GeomEppy requires Numpy, Shapely, and optionally Matplotlib.

Once these requirements are met, to install GeomEppy for Python 2.7, 3.5 or 3.6 call

    pip install geomeppy


Contribute
----------

- Issue Tracker: github.com/jamiebull1/geomeppy/issues
- Source Code: github.com/jamiebull1/geomeppy


License
-------

The project is licensed under the MIT license.