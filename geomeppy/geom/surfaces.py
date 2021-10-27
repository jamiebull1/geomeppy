"""A collection of functions which act on surfaces or lists of surfaces."""
from collections import defaultdict
from itertools import combinations
from typing import Dict, List, Tuple, Union  # noqa
import warnings

from eppy.bunch_subclass import EpBunch  # noqa
from eppy.idf_msequence import Idf_MSequence  # noqa
from numpy import float64  # noqa
import numpy as np
from shapely.geometry import Polygon,LineString, Point
from shapely.ops import polygonize
from shapely.ops import unary_union

from geomeppy.geom.polygons import Polygon2D
from .polygons import intersect, Polygon3D
from .vectors import Vector2D, Vector3D  # noqa
from ..utilities import almostequal


def set_coords(
    surface,  # type: EpBunch
    coords,
    # type: Union[List[Vector3D], List[Tuple[float, float, float]], Polygon3D]
    ggr,  # type: Union[List, None, Idf_MSequence]
):
    # type: (...) -> None
    """Update the coordinates of a surface.

    :param surface: The surface to modify.
    :param coords: The new coordinates as lists of [x,y,z] lists.
    :param ggr: Global geometry rules.
    """
    coords = list(coords)
    deduped = [c for i, c in enumerate(coords) if c != coords[(i + 1) % len(coords)]]
    poly = Polygon3D(deduped)
    poly = poly.normalize_coords(ggr)
    coords = [i for vertex in poly for i in vertex]
    if len(coords)/3 > 120:     #the /3 is needed because the len takes into account the three direction thus, the numbers of vertexes are not equl to the length of the coordinates
        warnings.warn(
            "To create surfaces with >120 vertices, ensure you have customised your IDD before running EnergyPlus. "
            "https://unmethours.com/question/9343/energy-idf-parsing-error/?answer=9344#post-id-9344"
        )
    # find the vertex fields
    n_vertices_index = surface.objls.index("Number_of_Vertices")
    first_x = n_vertices_index + 1  # X of first coordinate
    surface.obj = surface.obj[:first_x]
    # set the vertex field values
    surface.fieldvalues.extend(coords)


def set_matched_surfaces(surface, matched):
    # type: (EpBunch, EpBunch) -> None
    """Set boundary conditions for two adjoining surfaces.

    :param surface: The first surface.
    :param matched: The second surface.
    """
    if (
        str(surface.key).upper() == "BUILDINGSURFACE:DETAILED"
        and str(matched.key).upper() == "BUILDINGSURFACE:DETAILED"
    ):
        for s in [surface, matched]:
            s.Outside_Boundary_Condition = "surface"
            s.Sun_Exposure = "NoSun"
            s.Wind_Exposure = "NoWind"
        surface.Outside_Boundary_Condition_Object = matched.Name
        matched.Outside_Boundary_Condition_Object = surface.Name
        return []
    elif str(surface.key).upper() == "BUILDINGSURFACE:DETAILED" and str(
        matched.key
    ).upper() in ({"SHADING:SITE:DETAILED", "SHADING:ZONE:DETAILED"}):
        surface.Outside_Boundary_Condition = "adiabatic"
        surface.Sun_Exposure = "NoSun"
        surface.Wind_Exposure = "NoWind"
        return (matched.key,matched.Name)
    elif str(matched.key).upper() == "BUILDINGSURFACE:DETAILED" and str(
        surface.key
    ).upper() in ({"SHADING:SITE:DETAILED", "SHADING:ZONE:DETAILED"}):
        matched.Outside_Boundary_Condition = "adiabatic"
        matched.Sun_Exposure = "NoSun"
        matched.Wind_Exposure = "NoWind"
        return (surface.key,surface.Name)


def set_unmatched_surface(surface, vector):
    # type: (EpBunch, Union[Vector2D, Vector3D]) -> None
    """Set boundary conditions for a surface which does not adjoin another one.

    :param surface: The surface.
    :param vector: The surface normal vector.
    """
    if not hasattr(surface, "View_Factor_to_Ground"):
        return
    surface.View_Factor_to_Ground = "autocalculate"
    poly = Polygon3D(surface.coords)
    if min(poly.zs) < 0 or all(z == 0 for z in poly.zs):
        # below ground or ground-adjacent surfaces
        surface.Outside_Boundary_Condition_Object = ""
        surface.Outside_Boundary_Condition = "ground"
        surface.Sun_Exposure = "NoSun"
        surface.Wind_Exposure = "NoWind"
    else:
        surface.Outside_Boundary_Condition = "outdoors"
        surface.Outside_Boundary_Condition_Object = ""
        surface.Wind_Exposure = "WindExposed"
        if almostequal(vector, (0, 0, -1)):
            # downward facing surfaces
            surface.Sun_Exposure = "NoSun"
        else:
            surface.Sun_Exposure = "SunExposed"  # other external surfaces


def getidfplanes(surfaces):
    # type: (Idf_MSequence) -> Dict[float64, Dict[Union[Vector2D, Vector3D], List[EpBunch]]]
    """Fast access data structure for potentially matched surfaces.

    Get a data structure populated with all the surfaces in the IDF, keyed by their distance from the origin, and their
    normal vector.

    :param surfaces: List of all the surfaces.
    :returns: Mapping to look up IDF surfaces.
    """
    round_factor = 2
    planes = {}  # type: Dict[float64, Dict[Union[Vector2D, Vector3D], List[EpBunch]]]
    for s in surfaces:
        poly = Polygon3D(s.coords)
        rounded_distance = round(poly.distance, round_factor)
        rounded_normal_vector = Vector3D(
            *[round(axis, round_factor) for axis in poly.normal_vector]
        )
        planes.setdefault(rounded_distance, {}).setdefault(
            rounded_normal_vector, []
        ).append(s)
    return planes


def get_adjacencies(surfaces):
    # type: (Idf_MSequence) -> defaultdict
    """Create a dictionary mapping surfaces to their adjacent surfaces.

    :param surfaces: A mutable list of surfaces.
    :returns: Mapping of surfaces to adjacent surfaces.
    """
    adjacencies = defaultdict(list)  # type: defaultdict
    adjacentShades = defaultdict(list)  # type: defaultdict
    # find all adjacent surfacesName
    for s1, s2 in combinations(surfaces, 2):
        BetweenShades = False
        if s1.key == 'SHADING:SITE:DETAILED' and s2.key =='SHADING:SITE:DETAILED':
            BetweenShades = True
            adjacentShades = populate_adjacencies(adjacentShades, s1, s2, BetweenShades)
            continue
        surf2lookat = ['floor','ceiling']
        # if s1.Surface_Type in surf2lookat and s2.Surface_Type in surf2lookat:
        #     a = 1
        if 'V69467-8' in s1.Name or 'V69467-8' in s2.Name:
            a = 1
        try:
            adjacencies = populate_adjacencies(adjacencies, s1, s2, BetweenShades)
        except:
            adjacencies = populate_adjacencies(adjacencies, s1, s2, BetweenShades)
    for adjacency, polys in adjacencies.items():
        try:
            adjacencies[adjacency] = minimal_set(polys,adjacency[1])
        except:
            adjacencies[adjacency] = minimal_set(polys, adjacency[1])
    return adjacencies, adjacentShades


def minimal_set(polys,name):
    """Remove overlaps from a set of polygons.

    :param polys: List of polygons.
    :returns: List of polygons with no overlaps.
    """
    normal = polys[0].normal_vector
    as_2d = [p.project_to_2D() for p in polys]
    as_shapely = [Polygon(p) for p in as_2d]
    lines = [p.boundary for p in as_shapely]
    borders = unary_union(lines)
    shapes = [Polygon2D(p.boundary.coords) for p in polygonize(borders)]
    as_3d = [p.project_to_3D(polys[0]) for p in shapes]
    if not almostequal(as_3d[0].normal_vector, normal):
        as_3d = [p.invert_orientation() for p in as_3d]
    ###############################################################
    # the following concern only the vertical surfaces
    if abs(normal[2]) < 1e-3:
        # for a set of polygons that doesn't matches at each vertex, the above approach add some points
        # even though these will be in the middle of some edges, it leads to defaults afterward for surface in EnergyPlus
        # the following proposal enable to clean those polygons before being transfered to idf's object
        for p in as_3d:
            # se need to project it in 2D to make operations:
            surf2Analyse = p.project_to_2D()
            # first filter on the edge length
            pt2remove = getTooCloseNodes(surf2Analyse, 1e-3)
            val2remove = [p.vertices[pt] for pt in pt2remove]
            for val in val2remove:
                p.vertices.remove(val)
            val2remove = [surf2Analyse.vertices[pt] for pt in pt2remove]
            for val in val2remove:
                surf2Analyse.vertices.remove(val)
            # second filter on the point between two parallel lines
            #only if we have more than 3 points with non null area! and four should be present
            if len(p.vertices)<4 and p.area== 0:
                continue    #it will be automatically reoved by checking the area afterward
            pt2remove = getNodesWithinString(surf2Analyse)
            val2remove = [p.vertices[pt] for pt in pt2remove]
            for val in val2remove:
                p.vertices.remove(val)
            #lastly, since we have suppressed the fifth vertex to close the surface (doesn't really know if needed, but it is so for all surfaces
            p.vertices.append(p.vertices[0])
        # because an empty as_3D polygon was found...
        as_3d = [p for p in as_3d if p.area>0]
    #             done = True
    #############################################
    # # xavfa : bug identified for some polygons, by changing the vertex order, the area was no more zero...
    # for idx, p in enumerate(as_3d):
    #     if p.area ==0:
    #         as_3d[idx] = as_3d[idx].order_points('upperleftcorner')
    #         if as_3d[idx].area ==0:
    #             as_3d[idx].order_points('lowerleftcorner')
    #################################################################

    return [p for p in as_3d if p.area > 0]


def populate_adjacencies(adjacencies, s1, s2, BetweenShades = False):
    # type: (defaultdict, EpBunch, EpBunch) -> defaultdict
    """Update the adjacencies dict with any intersections between two surfaces.

    :param adjacencies: Dict to contain lists of adjacent surfaces.
    :param s1: Object representing an EnergyPlus surface.
    :param s2: Object representing an EnergyPlus surface.
    :returns: An updated dict of adjacencies.
    """
    if s1.Name == 'Shading_V65174-20_1':
        a = 1
    poly1 = Polygon3D(s1.coords)
    poly2 = Polygon3D(s2.coords)
    if not almostequal(abs(poly1.distance), abs(poly2.distance), 3):
        return adjacencies
    if not almostequal(poly1.normal_vector, poly2.normal_vector, 4):
        if not almostequal(poly1.normal_vector, -poly2.normal_vector, 4):
            return adjacencies

    intersection = poly1.intersect(poly2)
    #intersection might of ull area, so the following are added. It could have been integrated but in order to keep the original package visible
    #it is added as extra lines
    newintersection = []
    for inter in intersection:
        if inter.area > 1e-3:
            newintersection.append(inter)
    intersection = newintersection
    #end of correction for null intersection's areas
    if intersection:
        #the two surfaces, if the intersect,need to be facing opposite direction
        if almostequal(poly1.normal_vector, poly2.normal_vector, 4):
            poly2 = poly2.invert_orientation()
        if BetweenShades:
            print(
                '[/!\ Warning] Special care should be taken to this one as overlap shading are computed even thought there is a mistake... ')
            if s1.height <= s2.height:
                adjacencies[(s1.key, s1.Name)] = s1.height
            else:
                adjacencies[(s2.key, s2.Name)] = s1.height
            return adjacencies
        new_surfaces = intersect(poly1, poly2)


        new_s1 = [
            s
            for s in new_surfaces
            if almostequal(s.normal_vector, poly1.normal_vector, 4)
        ]
        new_s2 = [
            s
            for s in new_surfaces
            if almostequal(s.normal_vector, poly2.normal_vector, 4)
        ]

        # function added in order to consider non convex vertidal wall
        new_s1 = check4newsplits(new_s1)
        # function added in order to consider non convex vertical wall
        new_s2 = check4newsplits(new_s2)


        adjacencies[(s1.key, s1.Name)] += new_s1
        adjacencies[(s2.key, s2.Name)] += new_s2
    return adjacencies

def point_on_line(a, b, p):
    import numpy as np
    a = np.array(a)
    b = np.array(b)
    p = np.array(p)
    ap = p - a
    ab = b - a
    result = a + np.dot(ap, ab) / np.dot(ab, ab) * ab
    return tuple(result)

def is_parallel(line1, line2):
    vector_a_x = line1[1][0] - line1[0][0]
    vector_a_y = line1[1][1] - line1[0][1]
    vector_b_x = line2[1][0] - line2[0][0]
    vector_b_y = line2[1][1] - line2[0][1]
    # slope1 = vector_a_y/vector_a_x
    # slope2 = vector_b_y/vector_b_x
    import numpy as np
    v = np.array([vector_a_x,vector_a_y])
    w = np.array([vector_b_x,vector_b_y])
    angledeg = abs(np.rad2deg(np.arccos(round(v.dot(w) / (np.linalg.norm(v) * np.linalg.norm(w)),4))))
    #slopediff = abs((slope1 - slope2) / (slope1))
    if angledeg <5 or abs(angledeg-180) < 5:# >slopediff < 0.05:# and slope1*slope2>0: #5%of tolerance in the slope difference
        return True
    else:
        return False

def check4newsplits(new_surfaces):
    # function addeded in order to consider non convex vertical wall and to make several rectangular polygon out of the previous function

    newsurf = []
    for s in new_surfaces:
        if abs(s.normal_vector[2]) < 1e-3: #means vertical surface
            if (s.area / s.bounding_box.area) < .99: #would mean that s is not a rectanglw
                splittedsurf = []
                surf2D = s.project_to_2D()
                box2D = s.bounding_box.project_to_2D()
                Pt2keep = []
                Pt2Project =[]
                for edgeid, edge in enumerate(box2D.edges):
                    for idx, pt in enumerate(surf2D.vertices):
                        if LineString(edge).distance(Point(pt)) < 1e-3:
                            Pt2keep.append(idx)
                for idx in range(0,len(surf2D.vertices)):
                    if idx not in Pt2keep:
                        Pt2Project.append(idx)
                if len(Pt2Project) ==2:
                    subsurf =[]
                    for ndedge, edge in enumerate(box2D.edges):
                        if subsurf:
                            edge1 = LineString((surf2D.vertices[Pt2Project[0]],surf2D.vertices[Pt2Project[1]]))
                        else:
                            edge1 = LineString((surf2D.vertices[Pt2Project[1]], surf2D.vertices[Pt2Project[0]]))
                        if is_parallel([edge.vertices[0],edge.vertices[1]],[edge1.coords[0],edge1.coords[1]]):
                            for pt in edge1.coords:
                                subsurf.append(point_on_line(edge.vertices[0], edge.vertices[1], pt))
                elif len(Pt2Project) ==1:
                    edgeMin = surf2D.edges[0]
                    edgeMax = surf2D.edges[0]
                    for ndedge, edge in enumerate(surf2D.edges[1:]):
                        if edge.vertices[0][1] < edgeMin.vertices[0][1] and edge.vertices[1][1] < edgeMin.vertices[1][1] :
                            edgeMin = edge
                        if edge.vertices[0][1] > edgeMax.vertices[0][1] and edge.vertices[1][1] > edgeMax.vertices[1][1] :
                            edgeMax = edge
                    Combinaison = [(1,0),(0,0),(0,1),(1,1)]
                    for comb in Combinaison:
                        subsurf = []
                        subsurf.append(point_on_line(edgeMin.vertices[0], edgeMin.vertices[1], surf2D.vertices[Pt2Project[0]]))
                        subsurf.append((edgeMin.vertices[comb[0]].x,edgeMin.vertices[comb[0]].y))
                        subsurf.append((edgeMax.vertices[comb[1]].x,edgeMax.vertices[comb[1]].y))     #because edges should be reversed
                        subsurf.append(point_on_line(edgeMax.vertices[0], edgeMax.vertices[1], surf2D.vertices[Pt2Project[0]]))
                        if Polygon2D(subsurf).is_convex:
                            break
                else:
                    print('Sorry about thatm, mistake in check4newsplits() function in surfaces.py...')
                newsurf2split = Polygon2D(subsurf).project_to_3D(s)
                if almostequal(newsurf2split.normal_vector,s.normal_vector,3):
                    newset =  intersect(s, newsurf2split.invert_orientation())
                else:
                    newset = intersect(s, newsurf2split)
                new_s1 = [s1 for s1 in newset if almostequal(s1.normal_vector, s.normal_vector, 4)]
                for p in new_s1:
                    node2remove =[]
                    #first filter on the edge length
                    for idx,length in enumerate(p.edges_length):
                        if length <1e-4:
                            node2remove.append(idx)
                    for node in node2remove:
                        p.vertices.remove(p.vertices[node])
                    #2nd filter on the angle between edges
                    node2remove = []
                    for idx,egde in enumerate(p.edges):
                        if abs(np.degrees(getAngle(p.edges[idx], p.edges[(idx+1)%len(p.edges)]))-90) > 5:
                            node2remove.append(egde.p2)
                    for node in node2remove:
                        p.vertices.remove(node)
                new_s1 = [p for p in new_s1 if p.area > 0]
                #last clean up the surfaces as it seems its required...
                for surfidx in new_s1:
                    node2remove = []
                    #Same as before forst on the edge length:
                    for idx, length in enumerate(surfidx.edges_length):
                        if length < 1e-4:
                            node2remove.append(idx)
                    for node in node2remove:
                        surfidx.vertices.remove(surfidx.vertices[node])
                    #surf2Analyse = surfidx.project_to_2D()
                    # #first filter on the edge length
                    # pt2remove = getTooCloseNodes(surf2Analyse, 1e-3)
                    #for pt in pt2remove:
                        #surfidx.vertices.remove(surfidx.vertices[pt])
                        #surf2Analyse.vertices.remove(surf2Analyse.vertices[pt])
                    #second filter on the point between two parallel lines
                    # only if we have more than 2 points ! and four should be present
                    if len(surfidx.vertices) < 4 and surfidx.area == 0:
                        continue  # it will be automatically reoved by checking the area
                    surf2Analyse = surfidx.project_to_2D()
                    pt2remove = getNodesWithinString(surf2Analyse)
                    for pt in pt2remove:
                        surfidx.vertices.remove(surfidx.vertices[pt])
                # because an empty as_3D polygon was found...
                new_s1 = [p for p in new_s1 if p.area > 0]
                for nb in new_s1:
                    newsurf.append(nb)
                continue
        newsurf.append(s)
    return newsurf

def getTooCloseNodes(surf2Analyse,tol):
    " get the indexes of nodes to remove, because of being closest to the tolerance to eachother "
    " paramters : 2D surface and tolerance"
    pt2remove = []
    nbnode = len(surf2Analyse.vertices)
    for ptidx in range(0, nbnode):
        line1 = [surf2Analyse.vertices[ptidx], surf2Analyse.vertices[(ptidx + 1) % nbnode]]
        if LineString(line1).length < tol:
            pt2remove.append(ptidx)
    return pt2remove


def getNodesWithinString(surf2Analyse):
    " get the indexes of nodes to remove, because of being closest to the tolerance to each other "
    " paramters : 2D surface"
    pt2remove = []
    nbnode = len(surf2Analyse.vertices)
    for ptidx in range(0, nbnode):
        line1 = [surf2Analyse.vertices[ptidx], surf2Analyse.vertices[(ptidx + 1) % nbnode]]
        line2 = [surf2Analyse.vertices[(ptidx + 1) % nbnode], surf2Analyse.vertices[(ptidx + 2) % nbnode]]
        if LineString(line1).length < 1e-3 or LineString(line2).length < 1e-3:
            continue
        if is_parallel(line1, line2):
            pt2remove.append((ptidx + 1) % nbnode)
    return pt2remove

def getAngle(Seg1,Seg2):
    "returns the angle between 3D vector"
    #the input are Segment object
    vector1 = [Seg1.p2.x-Seg1.p1.x,Seg1.p2.y-Seg1.p1.y,Seg1.p2.z-Seg1.p1.z]
    vector2 = [Seg2.p2.x - Seg2.p1.x, Seg2.p2.y - Seg2.p1.y, Seg2.p2.z - Seg2.p1.z]
    unit_vector1 = vector1 / np.linalg.norm(vector1)
    unit_vector2 = vector2 / np.linalg.norm(vector2)
    dot_product = np.dot(unit_vector1, unit_vector2)
    return np.arccos(dot_product)