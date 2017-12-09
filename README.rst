GeomEppy
========

|Build Status| for Python 2.7, 3.5, 3.6 via Travis

|CodeCov| via CodeCov

GeomEppy is a scripting language for use with Eppy, which in turn is a
scripting language for EnergyPlus IDF files and output files.

It primarily adds functions to do with IDF geometry, including zones,
surfaces, constructions, etc.

Installation
------------

GeomEppy requires Numpy, Shapely, and optionally Matplotlib.

Once these requirements are met, to install GeomEppy for Python 2.7 or
3.6 call ``pip install geomeppy``.

API
---

The API for GeomEppy depends on replacing an Eppy IDF object with a
GeomEppy IDF object. To use this, you will need to import IDF from
GeomEppy rather than directly from Eppy.

In your scripts, use ``from geomeppy import IDF`` instead of
``from eppy.modeleditor import IDF``. All other features of the current
release version of Eppy will still be available.

GeomEppy then provides a simple Python API for actions on the IDF
object:

-  Intersecting and matching surfaces

``IDF.intersect()  # intersects all surfaces``

``IDF.match()  # sets boundary conditions of surfaces``

``IDF.intersect_match()  # intersect surfaces then set/update boundary conditions``

-  Moving an IDF

``IDF.translate_to_origin()  # move the whole IDF close to 0,0 on the x, y axes``

``IDF.translate([50, 20])  # move the whole IDF to x + 50, y + 20``

``IDF.translate([0, 0, 10])  # move the whole IDF to z + 10``

-  Rotating an IDF

``IDF.rotate(90)  # rotate the IDF 90 degrees counterclockwise around the centre of its bounding box``
``IDF.scale(2)  # scale the IDF to double its size (default is on the xy axes)``
``IDF.scale(2, axes='xy')  # scale the IDF to double its size (in the xy axes)``
``IDF.scale(2, axes='z')  # scale the IDF to double its size (in the z axis)``

-  Adding windows to external walls

``IDF.set_wwr(wwr=0.25)  # set a WWR of 25% for all external walls``

-  Setting constructions

``IDF.set_default_constructions()  # set a name for each construction in the model``

-  Viewing a simple 3D representation of an IDF

``IDF.view_model()  # shows a zoomable, rotatable transparent model``

-  Get all surfaces in a model

``IDF.getsurfaces()``

-  Get all surfaces in a model of a given type

``IDF.getsurfaces('wall')  # only works if the surface type has been set in the IDF``

-  Get all subsurfaces in a model

``IDF.getsubsurfaces()``

-  Get all subsurfaces in a model of a given type

``IDF.getsubsurfaces('window')  # only works if the surface type has been set in the IDF``

-  Automatic geometry building

``IDF.add_block(...)  # automatically adds a building block to the IDF``

This method requires some explanation. The parameters required are:

::

    name : str
        A name for the block.
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
        The rules to use in creating zones. Currently the only option is `by_storey` which sets each storey in the block as a Zone.

The block generated will have boundary conditions set correctly and any
intersections with adjacent blocks will be handled automatically. The
surface type will be set to ``wall``, ``floor``, ``ceiling`` or ``roof``
for each surface. Constructions are not set automatically so these will
need to be added afterwards in the normal way for Eppy.

Other functions
---------------

GeomEppy also provides some additional functions such as
``surface.setcoords(...)``

::

    wall = idf.newidfobject(
        'BUILDINGSURFACE:DETAILED', 'awall',
        Surface_Type = 'wall')
    wall.setcoords([(0,0,1),(0,0,0),(1,0,0),(1,0,1)])

Forthcoming
-----------

-  Scaling blocks
-  Geometry validation and correction
-  Geometry simplification
-  Better geometry visualisation

.. |Build Status| image:: https://travis-ci.org/jamiebull1/geomeppy.svg?branch=master
   :target: https://travis-ci.org/jamiebull1/geomeppy
.. |CodeCov| image:: https://img.shields.io/codecov/c/github/jamiebull1/geomeppy/master.svg
   :target: https://codecov.io/github/jamiebull1/geomeppy
