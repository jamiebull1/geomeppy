"""Build IDF geometry from minimal inputs."""
from typing import Any, Dict, List, Tuple, Union  # noqa

from six.moves import zip

from .geom.polygons import Polygon, Polygon3D  # noqa
from .geom.segments import Segment  # noqa
from .geom.vectors import Vector3D


class Zone(object):
    """Represents a single zone for translation into an IDF."""

    def __init__(self, name, surfaces):
        # type: (str, Dict[str, Any]) -> None
        """Initialise the zone object.

        :param name: A name for the zone.
        :param surfaces: The surfaces that make up the zone.

        """
        self.name = name
        self.walls = [s for s in surfaces['walls'] if s.area > 0]
        self.floors = surfaces['floors']
        self.roofs = surfaces['roofs']
        self.ceilings = surfaces['ceilings']


class Block(object):
    def __init__(self,
                 name,  # type: str
                 coordinates,  # type: Union[List[Tuple[float, float]], List[Tuple[int, int]]]
                 height,  # type: float
                 num_stories=1,  # type: int
                 below_ground_stories=0,  # type: int
                 below_ground_storey_height=2.5  # type: float
                 ):
        # type: (...) -> None
        """Represents a single block for translation into an IDF.

        :param name: A name for the block.
        :param coordinates: A list of (x, y) tuples representing the building outline.
        :param height: The height of the block roof above ground level.
        :param num_stories: The total number of stories including basement stories. Default : 1.
        :param below_ground_stories: The number of stories below ground. Default : 0.
        :param below_ground_storey_height: The height of each basement storey. Default : 2.5.

        """
        self.name = name
        if coordinates[0] == coordinates[-1]:
            coordinates.pop()
        self.coordinates = coordinates
        self.height = height
        self.num_stories = num_stories
        self.num_below_ground_stories = below_ground_stories
        self.below_ground_storey_height = below_ground_storey_height

    @property
    def stories(self):
        # type: () -> List[Dict[str, Any]]
        """A list of dicts of the surfaces of each storey in the block.

        :returns: list of dicts

        Example dict format::
            {'floors': [...],
             'ceilings': [...],
             'walls': [...],
             'roofs': [...],
             }

        """
        stories = []
        if self.num_below_ground_stories != 0:
            floor_no = -self.num_below_ground_stories
        else:
            floor_no = 0
        for floor, ceiling, wall, roof in zip(
                self.floors, self.ceilings, self.walls, self.roofs):
            stories.append({
                'storey_no': floor_no,
                'floors': floor, 'ceilings': ceiling, 'walls': wall, 'roofs': roof})
            floor_no += 1
        return stories

    @property
    def footprint(self):
        # type: () -> Polygon3D
        """Ground level outline of the block.

        :returns: A 2D outline of the block.

        """
        coordinates = [(v[0], v[1], 0) for v in self.coordinates]
        return Polygon3D(coordinates)

    @property
    def storey_height(self):
        # type: () -> float
        """Height of above ground stories.

        :returns: Average storey height.

        """
        return float(self.height) / (self.num_stories - self.num_below_ground_stories)

    @property
    def floor_heights(self):
        # type: () -> List[float]
        """Floor height for each storey in the block.

        :returns: A list of floor heights.

        """
        lfl = self.lowest_floor_level
        sh = self.storey_height
        floor_heights = [lfl + sh * i for i in range(self.num_stories)]
        return floor_heights

    @property
    def ceiling_heights(self):
        # type: () -> List[float]
        """Ceiling height for each storey in the block.

        :returns: A list of ceiling heights.

        """
        lfl = self.lowest_floor_level
        sh = self.storey_height
        ceiling_heights = [lfl + sh * (i + 1) for i in range(self.num_stories)]
        return ceiling_heights

    @property
    def lowest_floor_level(self):
        # type: () -> float
        """Floor level of the lowest basement storey.

        :returns: Lowest floor height.

        """
        return -(self.num_below_ground_stories *
                 self.below_ground_storey_height)

    @property
    def walls(self):
        # type: () -> List[List[Polygon3D]]
        """Coordinates for each wall in the block.

        These are ordered as a list of lists, one for each storey.

        :returns: Coordinates for all walls.

        """
        walls = []
        for fh, ch in zip(self.floor_heights, self.ceiling_heights):
            floor_walls = [_make_wall(edge, fh, ch)
                           for edge in self.footprint.edges]
            walls.append(floor_walls)
        return walls

    @property
    def floors(self):
        """Coordinates for each floor in the block.

        :returns: Coordinates for all floors.

        """
        floors = [[self.footprint.invert_orientation() + Vector3D(0, 0, fh)]
                  for fh in self.floor_heights]
        return floors

    @property
    def ceilings(self):
        """Coordinates for each ceiling in the block.

        :returns: Coordinates for all ceilings.

        """
        ceilings = [[self.footprint + Vector3D(0, 0, ch)]
                    for ch in self.ceiling_heights[:-1]]

        ceilings.append([])
        return ceilings

    @property
    def roofs(self):
        """Coordinates for each roof of the block.

        This returns a list with an entry for each floor for consistency with
        the other properties of the Block object, but should only have roof
        coordinates in the list in the final position.

        :returns: Coordinates for all roofs.

        """
        roofs = [[] for ch in self.ceiling_heights[:-1]]  # type: List[List[Polygon]]
        roofs.append([self.footprint + Vector3D(0, 0, self.height)])
        return roofs

    @property
    def surfaces(self):
        # type: () -> Dict[str, Any]
        """Coordinates for all the surfaces in the block.

        :returns: Coordinates for all surfaces.

        """
        return {'walls': self.walls,
                'ceilings': self.ceilings,
                'roofs': self.roofs,
                'floors': self.floors}


def _make_wall(edge, floor_height, ceiling_height):
    # type: (Segment, float, float) -> Polygon3D
    """Create a polygon representing the vertices of a wall.

    :param edge: Segment of a floor outline at ground level.
    :param floor_height: Floor height.
    :param ceiling_height: Ceiling height.

    """
    return Polygon3D([edge.p1 + (0, 0, ceiling_height),  # upper left
                      edge.p1 + (0, 0, floor_height),  # lower left
                      edge.p2 + (0, 0, floor_height),  # lower right
                      edge.p2 + (0, 0, ceiling_height),  # upper right
                      ])
