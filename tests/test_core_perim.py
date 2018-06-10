import pytest
from geomeppy.geom.core_perim import core_perim_zone_coordinates

footprint_1 = [(-20, 20), (30, -30), (50, 0), (50, 65), (-25, 50)]
expected_footprint_1 = {'Perimeter_Zone_5':
                        [(-19.27212384434131, 46.04655571753895),
                         (-25.0, 50.0),
                         (-20.0, 20.0),
                         (-15.331451032074877, 22.402518843940353)],
                        'Perimeter_Zone_4':
                        [(45.0, 58.900980486407214),
                         (50.0, 65.0),
                         (-25.0, 50.0),
                         (-19.27212384434131, 46.04655571753895)],
                        'Perimeter_Zone_3':
                        [(45.0, 1.5138781886599777),
                         (50.0, 0.0),
                         (50.0, 65.0),
                         (45.0, 58.900980486407214)],
                        'Perimeter_Zone_2':
                        [(29.2228758492822, -22.15180803741673),
                         (30.0, -30.0),
                         (50.0, 0.0),
                         (45.0, 1.5138781886599777)],
                        'Perimeter_Zone_1':
                        [(-15.331451032074877, 22.402518843940353),
                         (-20.0, 20.0),
                         (30.0, -30.0),
                         (29.2228758492822, -22.15180803741673)],
                        'Core_Zone':
                        [(-15.331451032074877, 22.402518843940353),
                         (-19.27212384434131, 46.04655571753895),
                         (45.0, 58.900980486407214),
                         (45.0, 1.5138781886599777),
                         (29.2228758492822, -22.15180803741673),
                         (-15.331451032074877, 22.402518843940353)]}


footprint_2 = [(0, 0), (30, 0), (30, 20), (0, 20)]
expected_footprint_2 = {'Core_Zone': [(5.0, 5.0), (5.0, 15.0),
                                      (25.0, 15.0), (25.0, 5.0), (5.0, 5.0)],
                        'Perimeter_Zone_4': [(5.0, 15.0), (0.0, 20.0),
                                             (0.0, 0.0), (5.0, 5.0)],
                        'Perimeter_Zone_3': [(25.0, 15.0), (30.0, 20.0),
                                             (0.0, 20.0), (5.0, 15.0)],
                        'Perimeter_Zone_2': [(25.0, 5.0), (30.0, 0.0),
                                             (30.0, 20.0), (25.0, 15.0)],
                        'Perimeter_Zone_1': [(5.0, 5.0), (0.0, 0.0),
                                             (30.0, 0.0), (25.0, 5.0)]}


def test_core_perim():
    assert core_perim_zone_coordinates(footprint_1, 5)[0] \
        == expected_footprint_1
    assert core_perim_zone_coordinates(footprint_2, 5)[0] \
        == expected_footprint_2
    with pytest.raises(NotImplementedError) as excinfo:
        core_perim_zone_coordinates(footprint_2, 10)[0]
    assert str(excinfo.value) == 'Multi-part geometries do not provide a coordinate sequence'
