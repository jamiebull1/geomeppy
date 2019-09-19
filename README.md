GeomEppy
========
[![Build Status](https://travis-ci.org/jamiebull1/geomeppy.svg?branch=master)](https://travis-ci.org/jamiebull1/geomeppy)
 for Python 2.7, 3.7 via Travis

[![CodeCov](https://img.shields.io/codecov/c/github/jamiebull1/geomeppy/master.svg)](https://codecov.io/github/jamiebull1/geomeppy)
 via CodeCov

[![Documentation Status](https://readthedocs.org/projects/geomeppy/badge/?version=latest)](http://geomeppy.readthedocs.io/en/latest/?badge=latest)
 on Read the Docs
 
GeomEppy is a scripting language for use with Eppy, which in turn is a scripting language for EnergyPlus IDF files and output files.

It primarily adds functions to do with IDF geometry, including zones, surfaces, constructions, etc.

## Installation

In most cases, all that is needed is:

`pip install geomeppy`

If you have problems installing, you may need to install `shapely` first. To ensure the required libraries are installed, we recommend installing `shapely` using a `conda` environment, particularly on Windows.

## Documentation

Complete documentation is hosted at [Read the Docs](http://geomeppy.readthedocs.io/en/latest/?). This covers the internals of geomeppy, 
and may be subject to change. 

Features documented in the [Basics](https://geomeppy.readthedocs.io/en/latest/How-to%20guides.html) section can be relied upon to remain stable.

## Referencing

If you rely on this package in academic work, and would like to include a citation (which we greatly appreciate), please refer to this project as:

- Bull J, et al. GeomEppy, 2016-, https://github.com/jamiebull1/geomeppy [Online; accessed 2019-09-21].
