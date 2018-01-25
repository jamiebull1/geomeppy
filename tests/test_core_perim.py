from itertools import product

from geomeppy.geom.polygons import Polygon2D


footprint = Polygon2D([(0, 0), (0, 10), (10, 10), (10, 0)])
expected_core = Polygon2D([(1, 1), (1, 9), (9, 9), (9, 1)])

expected_perims = {
    Polygon2D([(1, 9), (0, 10), (10,10), (10, 0)]),
    Polygon2D([(1, 1), (0, 0), (0, 10), (1, 9)]),
    Polygon2D([(9, 1), (10, 0), (0, 0), (1, 1)]),
    Polygon2D([(4, 4), (4, -4), (5, -5), (5, 5)]),
}


def get_core(footprint, perim_depth=None):
    poly = Polygon2D(footprint)
    core = poly.buffer(distance=-perim_depth)
    return core


def get_perims(footprint, core):
    perims = set()
    for edge in footprint.edges:
        c1 = sorted(
            product([edge.p1] * len(core), core),
            key=lambda x: x[0].relative_distance(x[1])
        )[0][1]
        c2 = sorted(
            product([edge.p2] * len(core), core),
            key=lambda x: x[0].relative_distance(x[1])
        )[0][1]
        perims.add(Polygon2D([c1, edge.p1, edge.p2, c2]))
    return perims


def test_core_perim():
    core = get_core(footprint, perim_depth=1)
    assert core == expected_core
    perims = get_perims(footprint, core)
    assert len(perims) == 4
    result = core
    for perim in perims:
        result = result.union(perim)[0]
    assert result == footprint
