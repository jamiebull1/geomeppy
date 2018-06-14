"""Core and perimeter zoning approach."""
from itertools import product
from geomeppy.geom.polygons import Polygon2D


def get_core(footprint, perim_depth=None):
    poly = Polygon2D(footprint)
    core = poly.buffer(distance=-perim_depth)
    return core


def get_perims(footprint, core):
    perims = []
    poly = Polygon2D(footprint)
    for edge in poly.edges:
        c1 = sorted(
            product([edge.p1] * len(core), core),
            key=lambda x: x[0].relative_distance(x[1]),
        )[0][1]
        c2 = sorted(
            product([edge.p2] * len(core), core),
            key=lambda x: x[0].relative_distance(x[1]),
        )[0][1]
        perims.append(Polygon2D([c1, edge.p1, edge.p2, c2]))
    return perims


def core_perim_zone_coordinates(footprint, perim_depth):
    """Returns a dictionary with the coordinates of the core/perimeter zones and
    a list of tuples containing the coordinates for the core zone."""
    zones_perim = get_perims(footprint, get_core(footprint, perim_depth))
    core = get_core(footprint, perim_depth)

    zones_dict = {}
    for idx, zone_perim in enumerate(zones_perim, 1):
        zone_name = "Perimeter_Zone_%i" % idx
        perim_zones_coords = []
        for pts in zone_perim:
            perim_zones_coords.append(pts.as_tuple(dims=2))
        zones_dict[zone_name] = perim_zones_coords
    core_zone_coords = []
    for pts in core:
        core_zone_coords.append(pts.as_tuple(dims=2))

    zones_dict["Core_Zone"] = core_zone_coords
    return zones_dict, core_zone_coords
