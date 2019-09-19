"""Tests for issue previously raised and fixed, so we can be alerted if they start failing again."""
import pytest

from geomeppy.geom.polygons import Polygon3D
from geomeppy.geom.surfaces import set_coords


@pytest.fixture
def shadow_matching():
    shadow_blocks = [
        {
            "name": "PN1001_Bld1000",
            "coordinates": [
                (-83637.73039999977, -100993.7087999992),
                (-83639.28569999989, -101015.82459999993),
                (-83653.77890000027, -101007.15670000017),
                (-83652.75889999978, -100992.65210000053),
                (-83637.73039999977, -100993.7087999992),
            ],
            "height": 21.0,
        },
        {
            "name": "PN1001_Bld1001",
            "coordinates": [
                (-83636.50970000029, -100976.35019999929),
                (-83637.73039999977, -100993.7087999992),
                (-83652.75889999978, -100992.65210000053),
                (-83651.5382000003, -100975.29350000061),
                (-83636.50970000029, -100976.35019999929),
            ],
            "height": 21.0,
        },
        {
            "name": "PN1001_Bld1004_EL23",
            "coordinates": [
                (-83635.2890999997, -100958.99369999953),
                (-83650.31759999972, -100957.93679999933),
                (-83648.50050000008, -100932.0979999993),
                (-83634.0064000003, -100940.75280000083),
                (-83635.2890999997, -100958.99369999953),
            ],
            "height": 21.0,
        },
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
        },
    ]
    zones = [
        {
            "name": "PN1001_Bld1003 Zone1",
            "coordinates": [
                (-83637.86197158082, -100995.57970000058),
                (-83623.76818996808, -100995.57970000058),
                (-83629.44400000013, -101021.71050000004),
                (-83639.28569999989, -101015.82459999993),
                (-83637.86197158082, -100995.57970000058),
            ],
            "height": 3.0,
            "num_stories": 1,
        },
        {
            "name": "PN1001_Bld1003 Zone2",
            "coordinates": [
                (-83623.76818996808, -100995.57970000058),
                (-83637.86197158082, -100995.57970000058),
                (-83637.73039999977, -100993.7087999992),
                (-83636.55229433342, -100976.95590000041),
                (-83619.72295787116, -100976.95590000041),
                (-83623.76818996808, -100995.57970000058),
            ],
            "height": 3.0,
            "num_stories": 1,
        },
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


def test_basic_shadow_matching(new_idf):
    """
    Test with all x-axis at 0

    This should avoid any issues with rounding/almost_equals.

    """
    try:
        ggr = new_idf.idfobjects["GLOBALGEOMETRYRULES"][0]
    except IndexError:
        ggr = None
    wall = new_idf.newidfobject(
        "BUILDINGSURFACE:DETAILED", Name="A Wall", Surface_Type="wall"
    )

    set_coords(wall, [(0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)], ggr)
    shadow = new_idf.newidfobject("SHADING:SITE:DETAILED", Name="A Shadow")
    set_coords(shadow, [(0, 0, 2), (0, 2, 2), (0, 2, 0), (0, 0, 0)], ggr)
    new_idf.intersect_match()
    # new_idf.view_model()
    walls = [
        Polygon3D(w.coords)
        for w in new_idf.getsurfaces("wall")
        if w.Outside_Boundary_Condition == "adiabatic"
    ]
    expected_adiabatic = 1
    assert len(walls) == expected_adiabatic


def test_simple_shadow_matching(new_idf):
    """Test in a single plane, but angled."""
    try:
        ggr = new_idf.idfobjects["GLOBALGEOMETRYRULES"][0]
    except IndexError:
        ggr = None
    wall1 = new_idf.newidfobject(
        "BUILDINGSURFACE:DETAILED", Name="Wall 1", Surface_Type="wall"
    )

    set_coords(
        wall1,
        [
            (1.5553000001236796, 28.001700000837445, 3.0),
            (1.5553000001236796, 28.001700000837445, -1.0),
            (2.7759999996051192, 45.36030000075698, -1.0),
            (2.7759999996051192, 45.36030000075698, 3.0),
        ],
        ggr,
    )
    shadow = new_idf.newidfobject("SHADING:SITE:DETAILED", Name="A Shadow")
    set_coords(
        shadow,
        [
            (2.7759999996051192, 45.36030000075698, 21.0),
            (2.7759999996051192, 45.36030000075698, 0.0),
            (1.5553000001236796, 28.001700000837445, 0.0),
            (1.5553000001236796, 28.001700000837445, 21.0),
        ],
        ggr,
    )
    new_idf.intersect_match()
    # new_idf.view_model()
    walls = [
        Polygon3D(w.coords)
        for w in new_idf.getsurfaces("wall")
        if w.Outside_Boundary_Condition == "adiabatic"
    ]
    expected_adiabatic = 1
    assert len(walls) == expected_adiabatic


def test_shadow_matching(new_idf, shadow_matching):
    """Test with a full model."""
    for block in shadow_matching["shadows"]:
        new_idf.add_shading_block(**block)
    for block in shadow_matching["zones"]:
        new_idf.add_block(**block)
    new_idf.translate_to_origin()
    new_idf.intersect_match()
    adiabatic = [
        Polygon3D(w.coords)
        for w in new_idf.getsurfaces("wall")
        if w.Outside_Boundary_Condition == "adiabatic"
    ]
    expected_adiabatic = 7
    assert len(adiabatic) == expected_adiabatic


def test_shadow_intersecting(new_idf, shadow_matching):
    """Test with a full model."""
    for block in shadow_matching["shadows"]:
        new_idf.add_shading_block(**block)
    for block in shadow_matching["zones"]:
        new_idf.add_block(**block)
    new_idf.translate_to_origin()
    new_idf.intersect()
    shadows = [Polygon3D(s.coords) for s in new_idf.getshadingsurfaces()]
    assert len(shadows) == 23
