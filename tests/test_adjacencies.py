import pytest

from geomeppy.geom.surfaces import get_adjacencies
from geomeppy.geom.surfaces import set_coords


@pytest.fixture
def shadow_intersecting():
    shadow_blocks = [
        {
            "name": "PN1001_Bld1004_EL24",
            "coordinates": [
                (-83635.2890999997, -100958.99369999953),
                (-83636.50970000029, -100976.35019999929),
                (-83651.5382000003, -100975.29350000061),
                (-83650.31759999972, -100957.93679999933),
                (-83635.2890999997, -100958.99369999953),
            ],
            "height": 21.0,
        }
    ]
    zones = [
        {
            "name": "PN1001_Bld1003 Zone3",
            "coordinates": [
                (-83614.40199999977, -100952.4587999992),
                (-83616.24896021019, -100960.96199999936),
                (-83635.42752116646, -100960.96199999936),
                (-83635.2890999997, -100958.99369999953),
                (-83634.0064000003, -100940.75280000083),
                (-83614.40199999977, -100952.4587999992),
            ],
            "height": 3.0,
            "num_stories": 1,
        },
        {
            "name": "PN1001_Bld1003 Zone4",
            "coordinates": [
                (-83616.24896021019, -100960.96199999936),
                (-83619.72295787116, -100976.95590000041),
                (-83636.55229433342, -100976.95590000041),
                (-83636.50970000029, -100976.35019999929),
                (-83635.42752116646, -100960.96199999936),
                (-83616.24896021019, -100960.96199999936),
            ],
            "height": 3.0,
            "num_stories": 1,
        },
    ]
    return {"zones": zones, "shadows": shadow_blocks}


def _test_adjacencies(new_idf, shadow_intersecting):
    """Test in a single plane, but angled."""
    try:
        ggr = new_idf.idfobjects["GLOBALGEOMETRYRULES"][0]
    except IndexError:
        ggr = None
    for block in shadow_intersecting["shadows"]:
        new_idf.add_shading_block(**block)
    for block in shadow_intersecting["zones"]:
        new_idf.add_block(**block)
    new_idf.translate_to_origin()
    # new_idf.view_model()
    adjacencies = get_adjacencies(new_idf.getsurfaces() + new_idf.getshadingsurfaces())
    done = []
    for surface in adjacencies:
        key, name = surface
        new_surfaces = adjacencies[surface]
        old_obj = new_idf.getobject(key.upper(), name)
        for i, new_coords in enumerate(new_surfaces, 1):
            if (key, name, new_coords) in done:
                continue
            done.append((key, name, new_coords))
            new = new_idf.copyidfobject(old_obj)
            new.Name = "%s_%i" % (name, i)
            set_coords(new, new_coords, ggr)
        new_idf.removeidfobject(old_obj)
    assert len(new_idf.getshadingsurfaces()) == 6
    assert len(new_idf.getsurfaces("wall")) == 10


def test_two_walls_one_shadow(new_idf):
    wall1 = [(0, 0.1, 0), (0, 1, 0), (0, 1, 1), (0, 0.1, 1)]
    wall2 = [(0, 1, 0), (0, 2.2, 0), (0, 2.2, 1), (0, 1, 1)]
    shadow = reversed([(0, 0, 0), (0, 2, 0), (0, 2, 2), (0, 0, 2)])
    w1 = new_idf.newidfobject(
        "BUILDINGSURFACE:DETAILED", Name="w1", Surface_Type="wall"
    )
    w1.setcoords(wall1)
    w2 = new_idf.newidfobject(
        "BUILDINGSURFACE:DETAILED", Name="w2", Surface_Type="wall"
    )
    w2.setcoords(wall2)
    sh = new_idf.newidfobject("SHADING:ZONE:DETAILED", Name="sh")
    sh.setcoords(shadow)
    new_idf.intersect()
    new_idf.match()
    adiabatic = [
        w
        for w in new_idf.getsurfaces("wall")
        if w.Outside_Boundary_Condition == "adiabatic"
    ]
    assert len(adiabatic) == 2
    assert len(new_idf.getsurfaces("wall")) == 3
    assert len(new_idf.getshadingsurfaces()) == 3
