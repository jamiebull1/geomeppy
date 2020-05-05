Basics
======

The API for `geomeppy` depends on replacing an `eppy` IDF object with a
`geomeppy` IDF object. To use this, you will need to import IDF from
`geomeppy` rather than directly from `eppy`.

In your scripts, use ``from geomeppy import IDF`` instead of
``from eppy.modeleditor import IDF``. All other features of the current
release version of `eppy` will still be available.

`geomeppy` then provides a simple Python API for actions on the IDF
object:

Intersect and match surfaces
----------------------------

Intersect all surfaces:

::

    IDF.intersect()

Set boundary conditions of surfaces:

::

    IDF.match()

Intersect surfaces then set/update boundary conditions:

::

    IDF.intersect_match()

Move an IDF
-----------

Move the whole IDF close to 0,0 on the x, y axes:

::

    IDF.translate_to_origin()

Move the whole IDF to x + 50, y + 20:

::

    IDF.translate([50, 20])

Move the whole IDF to z + 10:

::

    IDF.translate([0, 0, 10])

Rotate
------

Rotate the IDF 90 degrees counterclockwise around the centre of its bounding box:

::

    IDF.rotate(90)

Scale
-----

Scale the IDF to double its size (default is on the xy axes):

::

    IDF.scale(2)

Scale the IDF to double its size (in the xy axes):

::

    IDF.scale(2, axes='xy')

Scale the IDF to double its size (in the z axis):

::

    IDF.scale(2, axes='z')


Add windows to external walls
-----------------------------

Set a WWR of 20% (the default) for all external walls:

::

    IDF.set_wwr()

Set a WWR of 25% for all external walls:

::

    IDF.set_wwr(wwr=0.25)

Set no windows on all external walls with azimuth of 90, and WWR of 20% on other walls:

::

    IDF.set_wwr(wwr_map={90: 0})

Set a WWR of 30% for all external walls with azimuth of 90, and no windows on other walls:

::

    IDF.set_wwr(wwr=0, wwr_map={90: 0.3})

If ``wwr_map`` is passed, it overrides any value passed to ``wwr``, including
the default of 0.2. However it only overrides it on walls which have an
azimuth in the ``wwr_map``. Any omitted walls' WWR will be set to the value in
``wwr``. If you want to specify no windows for walls which are not specified in
``wwr_map``, you must also set ``wwr=None``.

Set constructions
-----------------

Set a name for each construction in the model:

::

    IDF.set_default_constructions()

View a simple 3D model
----------------------

Show a zoomable, rotatable transparent model using `matplotlib`:

::

    IDF.view_model()

Export a 3D OBJ file
--------------------

Generate a model which can be viewed in external programs:

::

    IDF.to_obj('mymodel.obj')

You can view the exported model `here <https://3dviewer.net/>`_. Just drag the .obj file
and .mtl file into the browser window.

Get all surfaces
----------------

::

    IDF.getsurfaces()

Get all surfaces of a given type
--------------------------------

::

    IDF.getsurfaces('wall')

This only works if the surface type has been set in the IDF.

Get all subsurfaces
-------------------

::

    IDF.getsubsurfaces()

Get all subsurfaces of a given type
-----------------------------------

::

    IDF.getsubsurfaces('window')

This only works if the surface type has been set in the IDF.

Add a block automatically
-------------------------

Automatically add a building block to the IDF:

::

    IDF.add_block(...)

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
        The rules to use in creating zones. Currently two options are available:
        - `by_storey`: sets each storey in the block as a Zone.
        - `core/perim`: creates core and perimeter Zones for each storey (see perim_depth).
    perim_depth : float, optional
        Depth of the perimeter zones if the core/perim zoning pattern is requested. Default : 3.0.
	

The block generated will have boundary conditions set correctly and any
intersections with adjacent blocks will be handled automatically. The
surface type will be set to ``wall``, ``floor``, ``ceiling`` or ``roof``
for each surface. Constructions are not set automatically so these will
need to be added afterwards in the normal way for Eppy.

Set surface coordinates
-----------------------

::

    surface.setcoords(...)

For example:

::

    wall = idf.newidfobject(
        'BUILDINGSURFACE:DETAILED',
        Name='awall',
        Surface_Type = 'wall',
        )
    wall.setcoords([(0,0,1),(0,0,0),(1,0,0),(1,0,1)])