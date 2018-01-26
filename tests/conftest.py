"""A module containing pytest fixtures that are used in multiple places in the test suite."""
from eppy.iddcurrent import iddcurrent
import pytest
from six import StringIO

from geomeppy.idf import IDF

base_idf_txt = """
    Version, 8.5;
    Building, Building 1, , , , , , , ;
    Zone, z1 Thermal Zone, 0.0, 0.0, 0.0, 0.0, , 1, , , , , , Yes;
    Zone, z2 Thermal Zone, 0.0, 0.0, 0.0, 0.0, , 1, , , , , , Yes;
    BuildingSurface:Detailed, z1_FLOOR, Floor, , z1 Thermal Zone, ground, , NoSun, NoWind, , , 1.0, 2.1, 0.0, 2.0, 2.0, 0.0, 2.0, 1.0, 0.0, 1.0, 1.1, 0.0;
    BuildingSurface:Detailed, z1_ROOF, Roof, , z1 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 2.0, 1.0, 0.5, 2.0, 2.0, 0.5, 1.0, 2.1, 0.5, 1.0, 1.1, 0.5;
    BuildingSurface:Detailed, z1_WALL_0001, WALL, , z1 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 1.0, 1.1, 0.5, 1.0, 1.1, 0.0, 1.0, 2.1, 0.0, 1.0, 2.1, 0.5;
    BuildingSurface:Detailed, z1_WALL_0002, Wall, , z1 Thermal Zone, Outdoors, , SunExposed, WindExposed, , , 1.0, 2.1, 0.5, 1.0, 2.1, 0.0, 2.0, 2.0, 0.0, 2.0, 2.0, 0.5;
    BuildingSurface:Detailed, z1_WALL_0003, WALL, , z1 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 2.0, 2.0, 0.5, 2.0, 2.0, 0.0, 2.0, 1.0, 0.0, 2.0, 1.0, 0.5;
    BuildingSurface:Detailed, z1_WALL_0004, WALL, , z1 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 2.0, 1.0, 0.5, 2.0, 1.0, 0.0, 1.0, 1.1, 0.0, 1.0, 1.1, 0.5;
    BuildingSurface:Detailed, z2_FLOOR, Floor, , z2 Thermal Zone, ground, , NoSun, NoWind, , , 1.5, 3.05, 0.0, 2.5, 2.95, 0.0, 2.5, 1.95, 0.0, 1.5, 2.05, 0.0;
    BuildingSurface:Detailed, z2_ROOF, Roof, , z2 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 2.5, 1.95, 0.5, 2.5, 2.95, 0.5, 1.5, 3.05, 0.5, 1.5, 2.05, 0.5;
    BuildingSurface:Detailed, z2_WALL_0001, WALL, , z2 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 1.5, 2.05, 0.5, 1.5, 2.05, 0.0, 1.5, 3.05, 0.0, 1.5, 3.05, 0.5;
    BuildingSurface:Detailed, z2_WALL_0002, WALL, , z2 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 1.5, 3.05, 0.5, 1.5, 3.05, 0.0, 2.5, 2.95, 0.0, 2.5, 2.95, 0.5;
    BuildingSurface:Detailed, z2_WALL_0003, WALL, , z2 Thermal Zone, outdoors, , SunExposed, WindExposed, , , 2.5, 2.95, 0.5, 2.5, 2.95, 0.0, 2.5, 1.95, 0.0, 2.5, 1.95, 0.5;
    BuildingSurface:Detailed, z2_WALL_0004, Wall, , z2 Thermal Zone, Outdoors, , SunExposed, WindExposed, , , 2.5, 1.95, 0.5, 2.5, 1.95, 0.0, 1.5, 2.05, 0.0, 1.5, 2.05, 0.5;
    Shading:Zone:Detailed, z2_SHADE_0003, z2_WALL_0003, , 4, 2.5, 2.95, 0.5, 2.6, 2.95, 0.3, 2.6, 1.95, 0.3, 2.5, 1.95, 0.5;
    """


@pytest.fixture()
def base_idf():
    """A two-zone model with a shading surface on one wall."""
    iddfhandle = StringIO(iddcurrent.iddtxt)
    if IDF.getiddname() == None:
        IDF.setiddname(iddfhandle)

    return IDF(StringIO(base_idf_txt))


ring_idf_txt = """
    Version, 8.5;
    Building, Building 1, , , , , , , ;
    Zone, Thermal Zone 1, 0.0, 0.0, 0.0, 0.0, , 1, , , , , , Yes;
    Zone, Thermal Zone 2, 0.0, 0.0, 0.0, 0.0, , 1, , , , , , Yes;
    BuildingSurface:Detailed, z1 Floor 0001, Floor, , Thermal Zone 2, Ground, , NoSun, NoWind, , , 0.0, 2.9, 0.0, 0.0, 0.0, 0.0, -2.14, 0.0, 0.0, -2.14, 2.9, 0.0;
    BuildingSurface:Detailed, z1 Wall 0001, Wall, , Thermal Zone 2, Outdoors, , SunExposed, WindExposed, , , -2.14, 0.0, 1.5, -2.14, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5;
    BuildingSurface:Detailed, z1 Wall 0002, Wall, , Thermal Zone 2, Outdoors, , SunExposed, WindExposed, , , -2.14, 2.9, 1.5, -2.14, 2.9, 0.0, -2.14, 0.0, 0.0, -2.14, 0.0, 1.5;
    BuildingSurface:Detailed, z1 Wall 0003, Wall, , Thermal Zone 2, Outdoors, , SunExposed, WindExposed, , , 0.0, 2.9, 1.5, 0.0, 2.9, 0.0, -2.14, 2.9, 0.0, -2.14, 2.9, 1.5;
    BuildingSurface:Detailed, z1 Wall 0004, Wall, , Thermal Zone 2, Outdoors, , SunExposed, WindExposed, , , 0.0, 0.0, 1.5, 0.0, 0.0, 0.0, 0.0, 2.9, 0.0, 0.0, 2.9, 1.5;
    BuildingSurface:Detailed, z1 Roof 0001, Roof, , Thermal Zone 2, Outdoors, , SunExposed, WindExposed, , , 0.0, 0.0, 1.5, 0.0, 2.9, 1.5, -2.14, 2.9, 1.5, -2.14, 0.0, 1.5;
    
    BuildingSurface:Detailed, z2 Floor 0001, Floor, , Thermal Zone 1, Ground, , NoSun, NoWind, , , -0.259, 2.46, 1.5, -0.259, 0.4, 1.5, -1.68, 0.4, 1.5, -1.68, 2.46, 1.5;
    BuildingSurface:Detailed, z2 Wall 0001, Wall, , Thermal Zone 1, Outdoors, , SunExposed, WindExposed, , , -0.259, 2.46, 3.0, -0.259, 2.46, 1.5, -1.68, 2.46, 1.5, -1.68, 2.46, 3.0;
    BuildingSurface:Detailed, z2 Wall 0002, Wall, , Thermal Zone 1, Outdoors, , SunExposed, WindExposed, , , -0.259, 0.4, 3.0, -0.259, 0.4, 1.5, -0.259, 2.46, 1.5, -0.259, 2.46, 3.0;
    BuildingSurface:Detailed, z2 Wall 0003, Wall, , Thermal Zone 1, Outdoors, , SunExposed, WindExposed, , , -1.68, 0.4, 3.0, -1.68, 0.4, 1.5, -0.259, 0.4, 1.5, -0.259, 0.4, 3.0;
    BuildingSurface:Detailed, z2 Wall 0004, Wall, , Thermal Zone 1, Outdoors, , SunExposed, WindExposed, , , -1.68, 2.46, 3.0, -1.68, 2.46, 1.5, -1.68, 0.4, 1.5, -1.68, 0.4, 3.0;
    BuildingSurface:Detailed, z2 Roof 0001, Roof, , Thermal Zone 1, Outdoors, , SunExposed, WindExposed, , , -0.259, 0.4, 3.0, -0.259, 2.46, 3.0, -1.68, 2.46, 3.0, -1.68, 0.4, 3.0;
    """


@pytest.fixture()
def ring_idf():
    """A two-zone model with an inner ring."""
    iddfhandle = StringIO(iddcurrent.iddtxt)
    if IDF.getiddname() == None:
        IDF.setiddname(iddfhandle)

    return IDF(StringIO(ring_idf_txt))


@pytest.fixture()
def new_idf():
    """An empty model."""
    iddfhandle = StringIO(iddcurrent.iddtxt)
    IDF.setiddname(iddfhandle, testing=True)
    idf = IDF()
    idf.new()
    return idf


@pytest.fixture()
def wwr_idf(new_idf):
    """A model with just two walls and a window."""
    test_walls = [[0,0,0], [0,1,0], [0,1,1], [0,0,1]], [[0,0,0], [1,0,0], [1,0,1], [0,0,1]]
    for i, coords in enumerate(test_walls, 1):
        new_idf.newidfobject(
            'FENESTRATIONSURFACE:DETAILED',
            Name='window%s' % i,
            Surface_Type='window',
            Construction_Name='ExtWindow',
            Building_Surface_Name='wall%s' % i,
        )
        wall = new_idf.newidfobject(
            'BUILDINGSURFACE:DETAILED',
            Name='wall%s' % i,
            Surface_Type='wall',
            Outside_Boundary_Condition='Outdoors',
        )
        wall.setcoords(coords)
    return new_idf


extracts_idf_txt = """
    Version, 8.8;
    Zone, z1 Thermal Zone, 0.0, 0.0, 0.0, 0.0, , 1, , , , , , Yes;
    Material, Spam, Rough, 0.1, 1, 1000, 1000, 0.9, 0.9, 0.9;
    """

@pytest.fixture()
def extracts_idf():
    """A model with a minimal zone and material object."""
    iddfhandle = StringIO(iddcurrent.iddtxt)
    if IDF.getiddname() == None:
        IDF.setiddname(iddfhandle)

    return IDF(StringIO(extracts_idf_txt))