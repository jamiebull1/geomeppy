"""Core and perimeter zoning approach."""
import math
import itertools


def slope_intercept(x_1, x_2, y_1, y_2):
    """Calculates the slope, intercept and intercept correction coefficient
    (case where x = constant) using two data points."""

    if (x_1 - x_2) != 0:
        slope = (y_1 - y_2) / (x_1 - x_2)
        corr_intercept = 1
    else:
        slope = 1
        corr_intercept = 0
    intercept = corr_intercept * y_1 - slope * x_1
    return (slope, intercept, corr_intercept)


def distance_on_curve(slope, intercept, perim_depth):
    """Calculates the projection of the perimeter depth on curve."""
    if slope != 0 and slope != 1:
        dist_on_curve = perim_depth / math.cos(math.atan(slope))
    else:
        dist_on_curve = perim_depth
    return dist_on_curve


def ajust_distance_on_curve(x_1, x_2, y_1, y_2, dist_on_curve):
    """Adjust calculated projection of the perimeter depth on the curve based on the
    position of two specified data points."""

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


def intersection_coordinates(corr_intercept_1, corr_intercept_2,
                             slope_1, slope_2, cste_1, cste_2):
    """Calculates the coordinates of the intersection point between two linear curves."""
    intersec_x = (corr_intercept_1 * cste_2 - corr_intercept_2 * cste_1) / \
                 (corr_intercept_2 * slope_1 - corr_intercept_1 * slope_2)
    try:
        intersec_y = (slope_1 * intersec_x + cste_1) / corr_intercept_1
    except Exception:
        intersec_y = (slope_2 * intersec_x + cste_2) / corr_intercept_2
    return (intersec_x, intersec_y)


def core_perim_zone_coordinates(floor_plan, perim_depth):
    """Returns a dictionary with the coordinates of the core/perimeter zones and
    a list of tuples containing the coordinates for the core zone."""

    floor_plan_it = itertools.cycle(floor_plan)

    int_floor_plan = []
    perim_zones_coords = []
    core_zone_coords = []
    prev_intersec = (0, 0)

    for i in range(len(floor_plan)):
        # Select the three next points in the floor plan
        pts = []
        for _ in range(3):
            pts.append(next(floor_plan_it))

        x_1 = float(pts[0][0])
        y_1 = float(pts[0][1])
        x_2 = float(pts[1][0])
        y_2 = float(pts[1][1])
        x_3 = float(pts[2][0])
        y_3 = float(pts[2][1])

        # Calculate the slopes and intercepts
        slope_1 = slope_intercept(x_1, x_2, y_1, y_2)[0]
        slope_2 = slope_intercept(x_2, x_3, y_2, y_3)[0]
        intercept_1 = slope_intercept(x_1, x_2, y_1, y_2)[1]
        intercept_2 = slope_intercept(x_2, x_3, y_2, y_3)[1]
        corr_intercept_1 = slope_intercept(x_1, x_2, y_1, y_2)[2]
        corr_intercept_2 = slope_intercept(x_2, x_3, y_2, y_3)[2]

        dist_1 = ajust_distance_on_curve(x_1, x_2, y_1, y_2,
                                         distance_on_curve(slope_1,
                                                           intercept_1,
                                                           perim_depth))
        dist_2 = ajust_distance_on_curve(x_2, x_3, y_2, y_3,
                                         distance_on_curve(slope_2,
                                                           intercept_2,
                                                           perim_depth))

        # Get the coordinates of the intersection of the two curves
        intersection = intersection_coordinates(corr_intercept_1,
                                                corr_intercept_2,
                                                slope_1,
                                                slope_2,
                                                intercept_1 + dist_1,
                                                intercept_2 + dist_2)
        intersec_x = intersection[0]
        intersec_y = intersection[1]

        # Add the new point to the interior floor plan
        int_floor_plan.append((intersec_x, intersec_y))

        # Iterate through the floor plan so
        # the next "point 2" is previous "point 3"
        for _ in range(len(floor_plan)-2):
            next(floor_plan_it)

        # Store the coordinate of the new core/perimeter zones away
        perim_zones_coords.append([(x_1, y_1), (x_2, y_2),
                                   (intersec_x, intersec_y),
                                   prev_intersec])
        prev_intersec = (intersec_x, intersec_y)
        if i == len(floor_plan) - 1:
            perim_zones_coords[0][3] = (intersec_x, intersec_y)
        core_zone_coords.append((intersec_x, intersec_y))

    # Format the perimeter and core zone coordinate in a dictionary
    perim_zones_coords.append(core_zone_coords)
    zones_dict = {}
    for i in range(len(perim_zones_coords)):
        if i < len(perim_zones_coords)-1:
            zone_name = "Perimeter_Zone_" + str(i+1)
        else:
            zone_name = "Core_Zone"
        zones_dict[zone_name] = perim_zones_coords[i]
    return zones_dict, int_floor_plan
