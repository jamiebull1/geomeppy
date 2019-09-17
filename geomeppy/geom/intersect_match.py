"""Intersect and match all surfaces in an IDF.
"""
from itertools import product

from geomeppy.geom.surfaces import (
    get_adjacencies,
    getidfplanes,
    set_coords,
    set_matched_surfaces,
    set_unmatched_surface,
)
from geomeppy.utilities import almostequal

if False:
    from ..idf import IDF  # noqa


def intersect_idf_surfaces(idf):
    # type: (IDF) -> None
    """Intersect all surfaces in an IDF.

    :param idf: The IDF.
    """
    surfaces = idf.getsurfaces() + idf.getshadingsurfaces()
    try:
        ggr = idf.idfobjects["GLOBALGEOMETRYRULES"][0]
    except IndexError:
        ggr = None
    # get all the intersected surfaces
    adjacencies = get_adjacencies(surfaces)
    for surface in adjacencies:
        key, name = surface
        new_surfaces = adjacencies[surface]
        old_obj = idf.getobject(key.upper(), name)
        for i, new_coords in enumerate(new_surfaces, 1):
            new = idf.copyidfobject(old_obj)
            new.Name = "%s_%i" % (name, i)
            set_coords(new, new_coords, ggr)
        idf.removeidfobject(old_obj)


def match_idf_surfaces(idf):
    # type: (IDF) -> None
    """Match all surfaces in an IDF.

    :param idf: The IDF.
    """
    surfaces = idf.getsurfaces() + idf.getshadingsurfaces()
    planes = getidfplanes(surfaces)
    matched = {}
    for distance in planes:
        for vector in planes[distance]:
            surfaces = planes[distance][vector]
            for surface in surfaces:
                set_unmatched_surface(surface, vector)
            matches = planes.get(-distance, {}).get(-vector, [])
            for s, m in product(surfaces, matches):
                if almostequal(s.coords, reversed(m.coords)):
                    matched[sorted_tuple(m, s)] = (m, s)

    for key in matched:
        set_matched_surfaces(*matched[key])


def sorted_tuple(m, s):
    """Used as a key for the matches."""
    return tuple(sorted(((s.key, s.Name), (m.key, m.Name))))
