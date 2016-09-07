# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""
Recipes for making changes to EnergyPlus IDF files.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from geomeppy.intersect_match import getidfsurfaces
from geomeppy.polygons import Polygon3D

from geomeppy.vectors import Vector3D


def translate_to_origin(idf):
    """
    Move an IDF close to the origin so that it can be viewed in SketchUp.
    
    Parameters
    ----------
    idf : IDF object
    
    """
    surfaces = getidfsurfaces(idf)
    windows = idf.idfobjects['FENESTRATIONSURFACE:DETAILED']
        
    min_x = min(min(Polygon3D(s.coords).xs) for s in surfaces)
    min_y = min(min(Polygon3D(s.coords).ys) for s in surfaces)

    translate(surfaces, (-min_x, -min_y))
    translate(windows, (-min_x, -min_y))
    
def translate(surfaces, vector):
    """Translate all surfaces by a vector.
    
    Parameters
    ----------
    surfaces : list
        A list of EpBunch objects.
    vector : Vector2D, Vector3D, (x,y) or (x,y,z) list-like
        Representation of a vector to translate by.
        
    """
    vector = Vector3D(*vector)
    for s in surfaces:
        new_coords = [Vector3D(*v) + vector for v in s.coords]
        s.setcoords(new_coords)

def set_wwr(idf, wwr=0.2):
    """Set the window to wall ratio on all external walls.
    
    Parameters
    ----------
    idf : IDF object
        The IDF to edit.
    wwr : float
        The window to wall ratio.
        
    """
    try:
        ggr = idf.idfobjects['GLOBALGEOMETRYRULES'][0]
    except IndexError:
        ggr = []
    walls = [s for s in idf.idfobjects['BUILDINGSURFACE:DETAILED']
             if s.Surface_Type.lower() == 'wall'
             and s.Outside_Boundary_Condition.lower() == 'outdoors']
    windows = idf.idfobjects['FENESTRATIONSURFACE:DETAILED']
    for window in windows:
        idf.removeidfobject(window)
    for wall in walls:
        coords = window_vertices_given_wall(wall, wwr)
        window = idf.newidfobject(
            'FENESTRATIONSURFACE:DETAILED',
            Name = "%s window" % wall.Name,
            Surface_Type = 'Window',
            Building_Surface_Name = wall.Name,
            View_Factor_to_Ground = 'autocalculate', # from the surface angle
            )
        window.setcoords(coords, ggr)
    
    
def window_vertices_given_wall(wall, wwr):
    """Calculate window vertices given wall vertices and glazing ratio.
    
    For each axis:
    1) Translate the axis points so that they are centred around zero
    2) Either:
        a) Multiply the z dimension by the glazing ratio to shrink it vertically
        b) Multiply the x or y dimension by 0.995 to keep inside the surface
    3) Translate the axis points back to their original positions
    
    Parameters
    ----------
    wall : EpBunch
        The wall to add a window on. We expect each wall to have four vertices.
    wwr : float
        Window to wall ratio.
    
    Returns
    -------
    list 
        Window vertices bounding a vertical strip midway up the surface.
    
    """
    vertices = wall.coords
    average_x = sum([x for x, _y, _z in vertices]) / len(vertices)
    average_y = sum([y for _x, y, _z in vertices]) / len(vertices)
    average_z = sum([z for _x, _y, z in vertices]) / len(vertices)
    # move windows in 0.5% from the edges so they can be drawn in SketchUp
    window_points = [[
                      ((x - average_x) * 0.999) + average_x,
                      ((y - average_y) * 0.999) + average_y,
                      ((z - average_z) * wwr) + average_z
                      ]
                     for x, y, z in vertices]

    return Polygon3D(window_points)
