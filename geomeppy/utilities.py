"""Utilities for use in geomeppy."""
from typing import Any  # noqa

from six.moves import zip

from sympy import nsolve, Symbol
from sympy.solvers.solveset import nonlinsolve

import math
import itertools


def almostequal(first, second, places=7):
    # type: (Any, Any, int) -> bool
    """Tests a range of types for near equality."""
    try:
        # try converting to float first
        first = float(first)
        second = float(second)
        # test floats for near-equality
        if round(abs(second - first), places) != 0:
            return False
        else:
            return True
    except ValueError:
        # handle non-float types
        return str(first) == str(second)
    except TypeError:
        # handle iterables
        return all([almostequal(a, b, places) for a, b in zip(first, second)])

		
"""
Returns the perimeter and core zone coordinates of a particular floor plan and for a particular perimeter depth.
- The first output of core_perim_zone_coordinates is a dictionary where the key is the zone name and the values correspond to the zone coordinates
- The second output is a list of tuples of the coordinates for the core zone or, 'interior floor plan'
"""

def slope_intercept(x_1, x_2, y_1, y_2):
    if (x_1 - x_2) <> 0:
        slope = (y_1 - y_2) / (x_1 - x_2)
        corr_intercept = 1
    else:
        slope = 1
        corr_intercept = 0 
    intercept = corr_intercept * y_1 - slope * x_1        
    return (slope, intercept, corr_intercept)

def distance_on_curve(slope, intercept, perim_depth):
    if slope <> 0 and slope <> 1 :
        dist_on_curve = perim_depth / math.cos(math.atan(slope))
    else:
        dist_on_curve = perim_depth  
    return dist_on_curve

def ajust_distance_on_curve(x_1, x_2, y_1, y_2, dist_on_curve):
    if x_1 == x_2 and y_1 > y_2:
        adj_dist_on_curve = - dist_on_curve
    elif x_1 == x_2 and y_1 < y_2:
        adj_dist_on_curve = + dist_on_curve
    elif x_1 < x_2 and y_1 == y_2:
        adj_dist_on_curve = + dist_on_curve        
    elif x_1 > x_2 and y_1 == y_2:
        adj_dist_on_curve = - dist_on_curve        
    elif x_1 < x_2 and y_1 < y_2:
        adj_dist_on_curve = + dist_on_curve        
    elif x_1 > x_2 and y_1 > y_2:
        adj_dist_on_curve = - dist_on_curve        
    elif x_1 > x_2 and y_1 < y_2:
        adj_dist_on_curve = - dist_on_curve        
    elif x_1 < x_2 and y_1 > y_2:
        adj_dist_on_curve = + dist_on_curve  
    return adj_dist_on_curve

def intersection_coordinates(lin_curve_1, lin_curve_2, mid_pt_x, mid_pt_y, slope_1, slope_2, corr_intercept_1, corr_intercept_2):
    x = Symbol('x')
    y = Symbol('y')    
    if lin_curve_1 <> lin_curve_2:
        intersection = list(nonlinsolve([lin_curve_1, lin_curve_2], [x, y]))
        intersec_x = intersection[0][0]
        intersec_y = intersection[0][1]
    elif corr_intercept_1 == 0 and corr_intercept_2 == 0:
        intersection = list(nonlinsolve([lin_curve_1, lin_curve_2], [x, y]))
        intersec_x = intersection[0][0]
        intersec_y = mid_pt_y
    elif slope_1 == 0 and slope_2 == 0:
        intersection = list(nonlinsolve([lin_curve_1, lin_curve_2], [x, y]))
        intersec_x = mid_pt_x     
        intersec_y = intersection[0][1]        
    return (float(intersec_x), float(intersec_y))
    
def core_perim_zone_coordinates(floor_plan, perim_depth):
    floor_plan_it = itertools.cycle(floor_plan)
    
    int_floor_plan = []
    perim_zones_coords = []
    core_zone_coords = []
    prev_intersec = (0, 0)
    
    for i in range(0,len(floor_plan)):
        # Select the three next points in the floor plan
        pts =[]
        for _ in range(0,3):
            pts.append(next(floor_plan_it))
            
        x_1 = float(pts[0][0])
        y_1 = float(pts[0][1])
        x_2 = float(pts[1][0])
        y_2 = float(pts[1][1])
        x_3 = float(pts[2][0])
        y_3 = float(pts[2][1])   
        
        # Calculate the slopes and intercepts
        slope_1 = slope_intercept(x_1,x_2,y_1,y_2)[0]
        slope_2 = slope_intercept(x_2,x_3,y_2,y_3)[0]
        intercept_1 = slope_intercept(x_1,x_2,y_1,y_2)[1]
        intercept_2 = slope_intercept(x_2,x_3,y_2,y_3)[1]    
        corr_intercept_1 = slope_intercept(x_1,x_2,y_1,y_2)[2]
        corr_intercept_2 = slope_intercept(x_2,x_3,y_2,y_3)[2]          

        dist_1 = ajust_distance_on_curve(x_1, x_2, y_1, y_2, distance_on_curve(slope_1,intercept_1,perim_depth))
        dist_2 = ajust_distance_on_curve(x_2, x_3, y_2, y_3, distance_on_curve(slope_2,intercept_2,perim_depth))

        # f1 and f2 are the equation of the linear curves intersecting the curves defined by point 1 and point 2
        # and the curve defined by point 2 and point 3 perpendicularly at a distance defined by dist_1 and dist_2
        x = Symbol('x')
        y = Symbol('y')        
        lin_curve_1 = slope_1 * x + intercept_1 - y * corr_intercept_1 + dist_1
        lin_curve_2 = slope_2 * x + intercept_2 - y * corr_intercept_2 + dist_2
        
        # Get the coordinates of the intersection of the two curves
        intersection = intersection_coordinates(lin_curve_1, lin_curve_2, x_2, y_2, slope_1, slope_2, corr_intercept_1, corr_intercept_2)
        intersec_x = intersection[0]
        intersec_y = intersection[1]

        # Add the new point to the interior floor plan
        int_floor_plan.append((intersec_x,intersec_y))

        # Iterate through the floor plan so the next point 2 is previous point 3
        for _ in range(0,len(floor_plan)-2):
            next(floor_plan_it)
        
        # Store the coordinate of the new core/perimeter zones away
        perim_zones_coords.append([(x_1,y_1),(x_2,y_2),(intersec_x,intersec_y),prev_intersec])
        prev_intersec = (intersec_x, intersec_y)
        if i == len(floor_plan) - 1:
            perim_zones_coords[0][3] = (intersec_x, intersec_y)
        core_zone_coords.append((intersec_x,intersec_y))

    # Format the perimeter and core zone coordinate in a dictionary
    perim_zones_coords.append(core_zone_coords)
    zones_dict = {}
    for i in range(0,len(perim_zones_coords)):
        if i < len(perim_zones_coords)-1:
            zone_name = "Perimeter_Zone_" + str(i+1)
        else:
            zone_name = "Core_Zone"
        zones_dict[zone_name] = perim_zones_coords[i]
    return zones_dict, int_floor_plan