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
    adjacencies, adjacentShades = get_adjacencies(surfaces)
    for surface in adjacentShades:
        key, name = surface
        obj = idf.getobject(key.upper(), name)
        idf.removeidfobject(obj)

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
            # if matches :
            #     import matplotlib.pyplot as plt
            #     fig = plt.figure()
            #     ax = plt.axes(projection="3d")
            for s, m in product(surfaces, matches):
                # print(m.Name)
                #
                # x, y, z = zip(*m.coords)
                # plt.plot(x,y,z)
                # x, y, z = zip(*s.coords)
                # plt.plot(x, y, z)
                # plt.show()
                # if s.Name == 'Block Build0 Storey 0 Wall 0004':
                #     a=1
                for i in range(len(s.coords)):  # xavfa modification to make a vertex rotation (the almostequl makes vertex per vertex comparison only.
                    coord2test = s.coords[i:] + s.coords[:i]
                    if almostequal(coord2test, reversed(m.coords),3):
                        matched[sorted_tuple(m, s)] = (m, s)
                        break

    MatchedShades = []
    for key in matched:
        Shade2Reomove = set_matched_surfaces(*matched[key])
        if Shade2Reomove:
            obj = idf.getobject(Shade2Reomove[0].upper(), Shade2Reomove[1])
            idf.removeidfobject(obj)
            mainShadeName = Shade2Reomove[1][:Shade2Reomove[1].index('_1')]
            if mainShadeName not in MatchedShades:
                MatchedShades.append(mainShadeName)
    return MatchedShades



def sorted_tuple(m, s):
    """Used as a key for the matches."""
    return tuple(sorted(((s.key, s.Name), (m.key, m.Name))))
