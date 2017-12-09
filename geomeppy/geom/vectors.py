# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""Utilities for IDF vectors.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from typing import Any, Iterator, List, Tuple, Union

import numpy as np

MYPY = False
if MYPY:
    from .polygons import Polygon3D


class Vector2D(object):
    """Two dimensional point."""
    def __init__(self, *args):
        # type: (*Any) -> None
        self.args = list(args)
        self.x = float(args[0])
        self.y = float(args[1])
    
    def __iter__(self):
        # type: () -> Iterator
        return (i for i in self.args)

    def __repr__(self):
        # type: () -> str
        class_name = type(self).__name__
        return '{}({!r}, {!r})'.format(class_name, *self.args)
    
    def __eq__(self, other):
        # type: (Union[List[float], Vector2D, Vector3D]) -> bool
        for a, b in zip(self, other):
            if a != b:
                return False
        return True
    
    def __sub__(self, other):
        # type: (Union[Vector3D, ndarray]) -> Vector3D
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
        # type: (Vector3D) -> float64
        return np.dot(self, other)

    def cross(self, other):
        # type: (Vector3D) -> ndarray
        return np.cross(self, other)

    @property
    def length(self):
        # type: () -> float
        """The length of a vector.
        
        Parameters
        ----------
        list-like
            A list or other iterable.
            
        """
        length = sum(x ** 2 for x in self) ** 0.5
    
        return length

    def closest(self, poly):
        # type: (Polygon3D) -> Vector3D
        """Find the closest vector in a polygon.
        
        Parameters
        ----------
        poly : Polygon or Polygon3D
        
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
        # type: () -> Vector3D
        return self.set_length(1.0)
    
    def set_length(self, new_length):
        # type: (float) -> Vector3D
        current_length = self.length        
        multiplier = new_length / current_length
        self.args = [i * multiplier for i in self.args]
        return self
    
    def invert(self):
        # type: () -> Vector3D
        return -self

class Vector3D(Vector2D):
    """Three dimensional point."""
    def __init__(self,
                 x,  # type: Union[float, float64]
                 y,  # type: Union[float, float64]
                 z=0  # type: Union[float, float64]
                 ):
        # type: (...) -> None
        super(Vector3D, self).__init__(x, y)
        self.z = float(z)
        self.args = (self.x, self.y, self.z)
        
    def __repr__(self):
        # type: () -> str
        class_name = type(self).__name__
        return '{}({!r}, {!r}, {!r})'.format(class_name, *self.args)
    
    def __hash__(self):
        # type: () -> int
        return hash(self.x) ^ hash(self.y) ^ hash(self.z)
        

def normalise_vector(v):
    # type: (List[float]) -> List[float]
    """Convert a vector to a unit vector
    
    Parameters
    ----------
    v : list
        The vector.
        
    Returns
    -------
    list
    
    """
    magnitude = sum(abs(i) for i in v)
    normalised_v = [i / magnitude for i in v]
    
    return normalised_v


def inverse_vector(v):
    # type: (Union[Vector2D, Vector3D]) -> List[float]
    """Convert a vector to the same vector but in the opposite direction
    
    Parameters
    ----------
    v : list
        The vector.
        
    Returns
    -------
    list
    
    """    
    return [-i for i in v]

