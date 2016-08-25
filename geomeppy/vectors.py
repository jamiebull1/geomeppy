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

try:
    import numpy as np
except ImportError:
    import tinynumpy.tinynumpy as np


class Vector2D(object):
    """Two dimensional point."""
    def __init__(self, *args):
        self.args = list(args)
        self.x = float(args[0])
        self.y = float(args[1])
    
    def __iter__(self):
        return (i for i in self.args)

    def __repr__(self):
        class_name = type(self).__name__
        return '{}({!r}, {!r})'.format(class_name, *self.args)
    
    def __eq__(self, other):
        for a, b in zip(self, other):
            if a != b:
                return False
        return True
        
    def __sub__(self, other):
        return self.__class__(*[self[i] - other[i] for i in range(len(self))])
    
    def __add__(self, other):
        return self.__class__(*[self[i] + other[i] for i in range(len(self))])
    
    def __neg__(self):
        return self.__class__(*inverse_vector(self))
        
    def __len__(self):
        return len(self.args)
    
    def __getitem__(self, key):
        return self.args[key]

    def __setitem__(self, key, value):
        self.args[key] = value
        
    def dot(self, other):
        return np.dot(self, other)

    def cross(self, other):
        return np.cross(self, other)

    @property
    def length(self):
        """The length of a vector.
        
        Parameters
        ----------
        list-like
            A list or other iterable.
            
        """
        length = sum(x ** 2 for x in self) ** 0.5
    
        return length

    def normalize(self):
        return self.set_length(1.0)
    
    def set_length(self, new_length):
        current_length = self.length        
        multiplier = new_length / current_length
        self.args = [i * multiplier for i in self.args]
        return self
    
    def invert(self):
        return -self

class Vector3D(Vector2D):
    """Three dimensional point."""
    def __init__(self, x, y, z):
        super(Vector3D, self).__init__(x, y)
        self.z = float(z)
        self.args = (self.x, self.y, self.z)
        
    def __repr__(self):
        class_name = type(self).__name__
        return '{}({!r}, {!r}, {!r})'.format(class_name, *self.args)
    

def normalise_vector(v):
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

