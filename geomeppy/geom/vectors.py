"""2D and 3D vector classes.

These are used to represent points in 2D and 3D, as well as directions for translations.
"""

from typing import Any, Iterable, Iterator, List, Sized, Tuple, Union  # noqa

import numpy as np
from six.moves import zip

if False: from .polygons import Polygon3D  # noqa


class Vector2D(Sized, Iterable):
    """Two dimensional point."""

    def __init__(self, *args):
        # type: (*Any) -> None
        self.args = list(args)
        self.x = float(args[0])
        self.y = float(args[1])
        self.z = 0.0

    def __iter__(self):
        # type: () -> Iterator
        return (i for i in self.args)

    def __repr__(self):
        # type: () -> str
        class_name = type(self).__name__
        return '{}({!r}, {!r})'.format(class_name, *self.args)

    def __eq__(self, other):
        for a, b in zip(self, other):
            if a != b:
                return False
        return True

    def __sub__(self, other):
        # type: (Any) -> Union[Vector2D, Vector3D]
        return self.__class__(*[self[i] - other[i] for i in range(len(self))])

    def __add__(self, other):
        # type: (Any) -> Union[Vector2D, Vector3D]
        return self.__class__(*[self[i] + other[i] for i in range(len(self))])

    def __neg__(self):
        # type: () -> Union[Vector2D, Vector3D]
        return self.__class__(*inverse_vector(self))

    def __len__(self):
        # type: () -> int
        return len(self.args)

    def __getitem__(self, key):
        # type: (Union[int, slice]) -> Union[Tuple[float, float, float], float]
        return self.args[key]

    def __setitem__(self, key, value):
        self.args[key] = value

    def __hash__(self):
        return hash(self.x) ^ hash(self.y)

    def dot(self, other):
        # type: (Vector3D) -> np.float64
        return np.dot(self, other)

    def cross(self, other):
        # type: (Union[Vector2D, Vector3D]) -> np.ndarray
        return np.cross(self, other)

    @property
    def length(self):
        # type: () -> float
        """The length of a vector."""
        length = sum(x ** 2 for x in self.args) ** 0.5

        return length

    def closest(self, poly):
        # type: (Polygon3D) -> Union[Vector2D, Vector3D]
        """Find the closest vector in a polygon.

        :param poly: Polygon or Polygon3D

        """
        min_d = float('inf')
        closest_pt = None
        for pt2 in poly:
            direction = self - pt2
            sq_d = sum(x ** 2 for x in direction)
            if sq_d < min_d:
                min_d = sq_d
                closest_pt = pt2
        return closest_pt

    def normalize(self):
        # type: () -> Union[Vector2D, Vector3D]
        return self.set_length(1.0)

    def set_length(self, new_length):
        # type: (float) -> Union[Vector2D, Vector3D]
        current_length = self.length
        multiplier = new_length / current_length
        self.args = [i * multiplier for i in self.args]
        return self

    def invert(self):
        # type: () -> Union[Vector2D, Vector3D]
        return -self

    def as_array(self, dims=3):
        # type: (Union[Vector2D, Vector3D], int) -> np.ndarray
        """Convert a point to a numpy array.

        Converts a Vector3D to a numpy.array([x,y,z]) or a Vector2D to a numpy.array([x,y]).
        Ensures all values are floats since some other types cause problems in pyclipper (notably where sympy.Zero is
        used to represent 0.0).

        :param pt: The point to convert.
        :param dims: Number of dimensions {default : 3}.
        :returns: Vector as a Numpy array.

        """
        # handle Vector3D
        if dims == 3:
            return np.array([float(self.x), float(self.y), float(self.z)])
        # handle Vector2D
        elif dims == 2:
            return np.array([float(self.x), float(self.y)])
        else:
            raise ValueError('%s-dimensional vectors are not supported.' % dims)

    def as_tuple(self, dims=3):
        # type: (Union[Vector2D, Vector3D, int]) -> Union[Tuple[float, float], Tuple[float, float, float]]
        """Convert a point to a numpy array.

        Convert a Vector3D to an (x,y,z) tuple or a Vector2D to an (x,y) tuple.
        Ensures all values are floats since some other types cause problems in pyclipper (notably where sympy.Zero is
        used to represent 0.0).

        :param pt: The point to convert.
        :param dims: Number of dimensions {default : 3}.
        :returns: Vector as a tuple.

        """
        # handle Vector3D
        if dims == 3:
            return float(self.x), float(self.y), float(self.z)
        # handle Vector2D
        elif dims == 2:
            return float(self.x), float(self.y)
        else:
            raise ValueError('%s-dimensional vectors are not supported.' % dims)

    def relative_distance(self, v2):
        # type: (Vector3D) -> float
        """A distance function for sorting vectors by distance.

        This only provides relative distance, not actual distance since we only use it for sorting.

        :param v2: Another vector.
        :returns: Relative distance between two point vectors.

        """
        direction = self - v2
        return sum(x ** 2 for x in direction)


class Vector3D(Vector2D):
    """Three dimensional point."""

    def __init__(self,
                 x,  # type: Union[float, np.float64]
                 y,  # type: Union[float, np.float64]
                 z=0,  # type: Union[float, np.float64]
                 ):
        # type: (...) -> None
        super(Vector3D, self).__init__(x, y, z)
        self.z = float(z)
        self.args = [self.x, self.y, self.z]

    def __repr__(self):
        # type: () -> str
        class_name = type(self).__name__
        return '{}({!r}, {!r}, {!r})'.format(class_name, *self.args)

    def __hash__(self):
        # type: () -> int
        return hash(self.x) ^ hash(self.y) ^ hash(self.z)


def inverse_vector(v):
    # type: (Union[Vector2D, Vector3D]) -> List[float]
    """Convert a vector to the same vector but in the opposite direction

    :param v: The vector.
    :returns: The vector reversed.

    """
    return [-i for i in v]
