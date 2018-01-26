"""Test for builder module."""
from geomeppy.builder import Block

breaking_coords = [
            (531023.28, 183220.85), (531023.09, 183220.78), (531022.99, 183220.74), 
            (531022.956, 183220.725), (531022.9, 183220.7), (531022.8, 183220.65), 
            (531022.71, 183220.6), (531022.62, 183220.55), (531022.54, 183220.49), 
            (531022.45, 183220.42), (531022.37, 183220.36), (531022.29, 183220.29), 
            (531022.22, 183220.22), (531022.15, 183220.14), (531022.08, 183220.06), 
            (531022.01, 183219.98), (531021.89, 183219.81), (531021.83, 183219.72), 
            (531021.78, 183219.63), (531021.74, 183219.53), (531021.69, 183219.44), 
            (531021.65, 183219.34), (531021.62, 183219.24), (531021.59, 183219.14), 
            (531021.56, 183219.04), (531021.54, 183218.94), (531021.52, 183218.84), 
            (531021.51, 183218.73), (531021.5, 183218.63), (531021.49, 183218.52), 
            (531021.49, 183218.42), (531021.49, 183218.31), (531021.5, 183218.21), 
            (531021.53, 183215.08), (531021.54, 183214.98), (531021.55, 183214.88), 
            (531021.57, 183214.78), (531021.59, 183214.68), (531021.62, 183214.58), 
            (531021.65, 183214.48), (531021.68, 183214.39), (531021.72, 183214.29), 
            (531021.76, 183214.2), (531021.79, 183214.146), (531021.81, 183214.11), 
            (531021.86, 183214.02), (531021.91, 183213.93), (531021.97, 183213.85), 
            (531022.03, 183213.77), (531022.09, 183213.69), (531022.16, 183213.61), 
            (531022.23, 183213.53), (531022.3, 183213.46), (531022.44, 183213.34), 
            (531022.52, 183213.28), (531022.6, 183213.22), (531022.69, 183213.17), 
            (531022.78, 183213.12), (531022.87, 183213.07), (531022.945, 183213.037), 
            (531022.96, 183213.03), (531023.06, 183212.99), (531023.15, 183212.95), 
            (531023.25, 183212.92), (531023.35, 183212.89), (531023.45, 183212.87), 
            (531023.55, 183212.85), (531023.65, 183212.84), (531023.75, 183212.83), 
            (531023.85, 183212.82), (531023.95, 183212.82), (531024.05, 183212.82), 
            (531024.15, 183212.82), (531024.26, 183212.83), (531024.36, 183212.85), 
            (531024.46, 183212.86), (531024.55, 183212.89), (531024.65, 183212.91), 
            (531024.82, 183212.97), (531028.5, 183214.02), (531028.61, 183214.08), 
            (531028.73, 183214.14), (531028.83, 183214.21), (531028.94, 183214.28), 
            (531029.04, 183214.35), (531029.14, 183214.43), (531029.24, 183214.52), 
            (531029.33, 183214.6), (531029.42, 183214.69), (531029.5, 183214.79), 
            (531029.59, 183214.89), (531029.66, 183214.99), (531029.74, 183215.09), 
            (531029.83, 183215.25), (531029.89, 183215.36), (531029.95, 183215.47), 
            (531030.0, 183215.59), (531030.05, 183215.71), (531030.09, 183215.83), 
            (531030.13, 183215.95), (531030.16, 183216.08), (531030.19, 183216.2), 
            (531030.21, 183216.33), (531030.23, 183216.45), (531030.24, 183216.64), 
            (531029.83, 183219.11), (531029.78, 183219.27), (531029.74, 183219.39), 
            (531029.69, 183219.51), (531029.63, 183219.63), (531029.57, 183219.75), 
            (531029.51, 183219.86), (531029.44, 183219.97), (531029.37, 183220.08), 
            (531029.29, 183220.18), (531029.21, 183220.28), (531029.13, 183220.38), 
            (531029.04, 183220.47), (531028.95, 183220.56), (531028.79, 183220.69), 
            (531028.69, 183220.77), (531028.59, 183220.85), (531028.48, 183220.92), 
            (531028.37, 183220.99), (531028.25, 183221.05), (531028.14, 183221.1), 
            (531028.02, 183221.16), (531027.9, 183221.2), (531027.77, 183221.24), 
            (531027.65, 183221.28), (531023.28, 183220.85)]


class TestAddBlock():

    def test_add_block_smoke_test(self, new_idf):
        # type: () -> None
        idf = new_idf
        name = "test"
        height = 7.5
        num_stories = 4
        below_ground_stories = 1
        below_ground_storey_height = 2.5
        coordinates = [
            (87.25,24.0),(91.7,25.75),(90.05,30.25),
            (89.55,31.55),(89.15,31.35),(85.1,29.8),
            (86.1,27.2),(84.6,26.65),(85.8,23.5),
            (87.25,24.0)]
        idf.add_block(name, coordinates, height, num_stories, below_ground_stories, below_ground_storey_height)
        idf.intersect_match()

    def test_add_two_blocks(self, new_idf):
        # type: () -> None
        idf = new_idf
        height = 5
        num_stories = 2
        block1 = [(0,0),(3,0),(3,3),(0,3)]
        block2 = [(3,1),(7,1),(7,5),(3,5)]
        idf.add_block('left', block1, height, num_stories)
        idf.add_block('right', block2, height, num_stories)
        idf.intersect_match()
        idf.set_wwr(0.25)
        idf.set_default_constructions()
        # Storey 0
        wall = idf.getobject(
            'BUILDINGSURFACE:DETAILED', 'Block left Storey 0 Wall 0002_1')
        assert wall.Construction_Name == 'Project Partition'
        
        wall = idf.getobject(
            'BUILDINGSURFACE:DETAILED', 'Block left Storey 0 Wall 0002_2')
        assert wall.Construction_Name == 'Project Wall'
        
        wall = idf.getobject(
            'BUILDINGSURFACE:DETAILED', 'Block right Storey 0 Wall 0004_1')
        assert wall.Construction_Name == 'Project Partition'
        
        wall = idf.getobject(
            'BUILDINGSURFACE:DETAILED', 'Block right Storey 0 Wall 0004_2')
        assert wall.Construction_Name == 'Project Wall'
        # Storey 1
        wall = idf.getobject(
            'BUILDINGSURFACE:DETAILED', 'Block left Storey 1 Wall 0002_1')
        assert wall.Construction_Name == 'Project Partition'
        
        wall = idf.getobject(
            'BUILDINGSURFACE:DETAILED', 'Block left Storey 1 Wall 0002_2')
        assert wall.Construction_Name == 'Project Wall'
        
        wall = idf.getobject(
            'BUILDINGSURFACE:DETAILED', 'Block right Storey 1 Wall 0004_1')
        assert wall.Construction_Name == 'Project Partition'
        
        wall = idf.getobject(
            'BUILDINGSURFACE:DETAILED', 'Block right Storey 1 Wall 0004_2')
        assert wall.Construction_Name == 'Project Wall'
        
        for window in idf.getsubsurfaces(surface_type='window'):
            wall = idf.getobject(
                'BUILDINGSURFACE:DETAILED', window.Building_Surface_Name)
            assert wall.Construction_Name == 'Project Wall'

    def test_add_two_concentric_blocks(self, new_idf):
        # type: () -> None
        idf = new_idf
        height = 5
        num_stories = 2
        block1 = [(0,0),(4,0),(4,4),(0,4)]
        block2 = [(1,1),(2,1),(2,2),(1,2)]
        idf.add_block('outer', block1, height, num_stories)
        idf.add_block('inner', block2, height, num_stories)
        idf.intersect_match()
        idf.set_wwr(0.25)
        idf.set_default_constructions()

    def test_known_breaking(self, new_idf):
        # type: () -> None
        idf = new_idf
        height = 5
        num_stories = 2
        coordinates = breaking_coords
        idf.add_block('breaker', coordinates, height, num_stories)
        idf.intersect_match()


def test_block():
    # type: () -> None
    name = "test"
    height = 7.5
    num_stories = 4
    below_ground_stories = 1
    below_ground_storey_height = 2.5
    coordinates = [
        (524287.25,181424.0),(524291.7,181425.75),(524290.05,181430.25),
        (524289.55,181431.55),(524289.15,181431.35),(524285.1,181429.8),
        (524286.1,181427.2),(524284.6,181426.65),(524285.8,181423.5),
        (524287.25,181424.0)]
    
    block = Block(name, coordinates, height, num_stories,
                  below_ground_stories, below_ground_storey_height)
    # number of surfaces
    assert len(block.surfaces['roofs']) == block.num_stories
    assert all(r == [] for r in block.surfaces['roofs'][:-1])
    assert len(block.surfaces['walls']) == block.num_stories
    assert len(block.surfaces['ceilings']) == block.num_stories
    assert len(block.surfaces['floors']) == block.num_stories
    # heights
    assert block.surfaces['floors'][0][0].vertices[0].z == (
        -below_ground_storey_height * below_ground_stories)
    assert block.surfaces['roofs'][-1][0].vertices[0].z == height
    # storey_nos
    assert block.stories[0]['storey_no'] == -below_ground_stories
    assert block.stories[-1]['storey_no'] == (
        num_stories - below_ground_stories - 1)
