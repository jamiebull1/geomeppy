import pytest
from six import StringIO
from geomeppy.geom.core_perim import core_perim_zone_coordinates, get_core, get_perims
from geomeppy.geom.polygons import Polygon2D
from geomeppy import IDF

footprint = [(0, 0), (30, 0), (30, 20), (0, 20)]
expected_footprint = {
    "Core_Zone": [(5.0, 5.0), (5.0, 15.0), (25.0, 15.0), (25.0, 5.0), (5.0, 5.0)],
    "Perimeter_Zone_4": [(5.0, 15.0), (0.0, 20.0), (0.0, 0.0), (5.0, 5.0)],
    "Perimeter_Zone_3": [(25.0, 15.0), (30.0, 20.0), (0.0, 20.0), (5.0, 15.0)],
    "Perimeter_Zone_2": [(25.0, 5.0), (30.0, 0.0), (30.0, 20.0), (25.0, 15.0)],
    "Perimeter_Zone_1": [(5.0, 5.0), (0.0, 0.0), (30.0, 0.0), (25.0, 5.0)],
}


def test_core_perim():
    perim_depth = 5
    assert core_perim_zone_coordinates(footprint, perim_depth)[0] == expected_footprint
    assert get_core(footprint, perim_depth) == Polygon2D(
        expected_footprint["Core_Zone"]
    )
    for idx, zone in enumerate(
        get_perims(footprint, get_core(footprint, perim_depth)), 1
    ):
        assert zone == Polygon2D(expected_footprint["Perimeter_Zone_%i" % idx])


def test_perim_depth():
    idf_file = IDF(StringIO(""))

    with pytest.raises(ValueError) as excinfo:
        idf_file.add_block(
            name="footprint",
            coordinates=footprint,
            height=3,
            zoning="core/perim",
            num_stories=1,
            perim_depth=10,
        )
    assert str(excinfo.value) == "Perimeter depth is too great"
