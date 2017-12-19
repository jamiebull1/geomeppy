# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""Tool for visualising geometry."""
from eppy.function_helpers import getcoords
from eppy.iddcurrent import iddcurrent
from eppy.modeleditor import IDF
from six import StringIO

try:
    from mpl_toolkits.mplot3d import Axes3D  # noqa
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    import matplotlib.pyplot as plt
except ImportError:
    # this isn't always needed so we can ignore if it's not present
    pass


def view_idf(fname=None, idf_txt=None):
    # type: (Optional[str], Optional[str]) -> None
    """Display an IDF for inspection.

    :param fname: Path to the IDF.
    :param idf_txt: The string representation of an IDF.
    """
    if fname and idf_txt:
        raise ValueError('Pass either fname or idf_txt, not both.')
    # set the IDD for the version of EnergyPlus
    iddfhandle = StringIO(iddcurrent.iddtxt)
    if IDF.getiddname() is None:
        IDF.setiddname(iddfhandle)

    if fname:
        # import the IDF
        idf = IDF(fname)
    elif idf_txt:
        idf = IDF()
        idf.initreadtxt(idf_txt)
    # create the figure and add the surfaces
    plt.figure()
    ax = plt.axes(projection='3d')
    collections = _get_collections(idf, opacity=0.5)
    for c in collections:
        ax.add_collection3d(c)

    # calculate and set the axis limits
    limits = _get_limits(idf=idf)
    ax.set_xlim(limits['x'])
    ax.set_ylim(limits['y'])
    ax.set_zlim(limits['z'])

    plt.show()


def view_polygons(polygons):
    """Display a collection of polygons for inspection.

    :param polygons: A dict keyed by colour, containing Polygon3D objects to show in that colour.
    """
    # create the figure and add the surfaces
    plt.figure()
    ax = plt.axes(projection='3d')

    collections = _make_collections(polygons, opacity=0.5)

    for c in collections:
        ax.add_collection3d(c)

    # calculate and set the axis limits
    limits = _get_limits(polygons=polygons)
    ax.set_xlim(limits['x'])
    ax.set_ylim(limits['y'])
    ax.set_zlim(limits['z'])

    plt.show()


def _get_surfaces(idf):
    """Get the surfaces from the IDF.
    """
    surface_types = ['BUILDINGSURFACE:DETAILED',
                     'FENESTRATIONSURFACE:DETAILED']
    surfaces = []
    for surface_type in surface_types:
        surfaces.extend(idf.idfobjects[surface_type])

    return surfaces


def _get_collections(idf, opacity=1):
    """Set up 3D collections for each surface type.
    """
    surfaces = _get_surfaces(idf)
    # set up the collections
    walls = Poly3DCollection([getcoords(s) for s in surfaces
                              if s.Surface_Type.lower() == 'wall'],
                             alpha=opacity,
                             facecolor='wheat',
                             edgecolors='black'
                             )
    floors = Poly3DCollection([getcoords(s) for s in surfaces
                               if s.Surface_Type.lower() == 'floor'],
                              alpha=opacity,
                              facecolor='dimgray',
                              edgecolors='black'
                              )
    roofs = Poly3DCollection([getcoords(s) for s in surfaces
                              if s.Surface_Type.lower() == 'roof'],
                             alpha=opacity,
                             facecolor='firebrick',
                             edgecolors='black'
                             )
    windows = Poly3DCollection([getcoords(s) for s in surfaces
                                if s.Surface_Type.lower() == 'window'],
                               alpha=opacity,
                               facecolor='cornflowerblue',
                               edgecolors='black'
                               )

    return walls, roofs, floors, windows


def _make_collections(polygons, opacity=1):
    """Make collections from a dict of polygons.
    """
    collection = []
    for color in polygons:
        collection.append(Poly3DCollection(
            [p.points_matrix for p in polygons[color]],
            alpha=opacity,
            facecolor=color,
            edgecolors='black'))
    return collection


def _get_limits(idf=None, polygons=None):
    """Get limits for the x, y and z axes so the plot is fitted to the axes."""
    if polygons:
        x = [pt[0] for color in polygons for p in polygons[color] for pt in p]
        y = [pt[1] for color in polygons for p in polygons[color] for pt in p]
        z = [pt[2] for color in polygons for p in polygons[color] for pt in p]

    elif idf:
        surfaces = _get_surfaces(idf)

        x = [pt[0] for s in surfaces for pt in getcoords(s)]
        y = [pt[1] for s in surfaces for pt in getcoords(s)]
        z = [pt[2] for s in surfaces for pt in getcoords(s)]

    max_delta = max((max(x) - min(x)),
                    (max(y) - min(y)),
                    (max(z) - min(z)))

    return {'x': (min(x), min(x) + max_delta),
            'y': (min(y), min(y) + max_delta),
            'z': (min(z), min(y) + max_delta)}


def main(fname=None, polygons=None):
    if fname:
        view_idf(fname)
    elif polygons:
        view_polygons(polygons)


if __name__ == "__main__":
    main()
