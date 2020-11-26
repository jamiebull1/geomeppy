"""Core and perimeter zoning approach."""
from itertools import product
from geomeppy.geom.polygons import Polygon2D, is_convex_polygon
from shapely.geometry import LineString

def get_core(footprint, perim_depth=None):
    poly = Polygon2D(footprint)
    try:
        core = poly.buffer(distance=-perim_depth)
        if perim_depth:
            newcore = check_core(core,perim_depth/2) #the tolerance is defined as half the perim depth
        else:
            newcore = core
    except:
        newcore = False
    return newcore

def check_core(core,epsilon):
    # #filtering with edges length. length below 1m are removed #modif from xavfa
    #but also vertexes that are closer to the same distance (balcony effect : merge point on the balcony bit not at its birth, on the wall
    #this modification is associated with the one in identifying the perimeters zone
    #first, let removed the edge that are smaller then epsilon
    checked_core = True
    corecoord = [core.vertices_list[i] for i, v in enumerate(core.edges_length[:-1]) if v > epsilon]
    #than lets remove eventually the nodes that creates narrow triangles in the core zone so nomore than one in between
    node2remove = []
    newcorecoord = []
    nd2rm = []
    #corecoord.append(corecoord[0])
    corecoordtotest=list(corecoord)
    corecoordtotest += corecoordtotest
    for idx, nodei in enumerate(corecoordtotest):
        for jdx, nodej in enumerate(corecoordtotest):
            if jdx>idx:
                if ((nodei[0]-nodej[0])**2+(nodei[1]-nodej[1])**2)**0.5<epsilon:
                        if jdx%len(corecoord)!=idx%len(corecoord) and jdx-idx<3:
                            node2remove.append((idx, jdx))
    if node2remove:
        for node in node2remove:
            nd2rm += [(i + node[0])%len(corecoord) for i in range(node[1] - node[0])]
        for idx, node in enumerate(corecoord):
            if not idx in nd2rm:
                newcorecoord.append(node)
    else:
        newcorecoord = corecoord
    if len(newcorecoord)<3:
            checked_core = False
    if checked_core:
        newcorecoord.append(newcorecoord[0]) # to close the loop
        checked_core = Polygon2D(newcorecoord)
    return checked_core


def get_perims(footprint, core):
    perims = []
    poly = Polygon2D(footprint)
    if not(core):
        print('The perimetre width aksed for is too wide to build the core zone')
        return False
    poly1 = Polygon2D(core)
    original = False
    if original:
        for edge in poly.edges:
            c1 = sorted(
                product([edge.p1] * len(core), core),
                key=lambda x: x[0].relative_distance(x[1]),
            )[0][1]
            c2 = sorted(
                product([edge.p2] * len(core), core),
                key=lambda x: x[0].relative_distance(x[1]),
            )[0][1]
            perims.append(Polygon2D([c1, edge.p1, edge.p2, c2]))
    else:
        GoodPoint = True
        for idx, edge in enumerate(poly1.edges):
            if poly1.edges_length[idx]>1:
                if idx==0:
                    c1 = FindClosestNode(edge.p1, poly1, footprint)
                    coreEdge1 = edge.p1
                elif GoodPoint:
                    coreEdge1 = edge.p1
                    c1 = c2
                #integration of a try in order to avoid havoing triangle zone due to the same point for c1 and c2.
                c2, GoodPoint = FindClosestNode(edge.p2, poly1, footprint, EdgeP1 = c1)
                if GoodPoint:
                    startidx = 0
                    endidx = 0
                    for i,pt in enumerate(footprint):
                        if str(c1) in str(pt):
                            startidx = i
                        if str(c2) in str(pt):
                            endidx = i
                    if startidx>endidx:
                        if not str(coreEdge1) in str(edge.p1):
                            perim_coord = [coreEdge1]+footprint[startidx:]+footprint[:endidx+1]+[edge.p2]+[edge.p1]
                        else:
                            perim_coord = [coreEdge1] + footprint[startidx:] + footprint[:endidx + 1] + [edge.p2]
                    else:
                        if not str(coreEdge1) in str(edge.p1):
                            perim_coord = [coreEdge1]+footprint[startidx:endidx+1]+[edge.p2]+[edge.p1]
                        else:
                            perim_coord = [coreEdge1] + footprint[startidx:endidx + 1] + [edge.p2]
                    perims.append(Polygon2D(perim_coord))
    return perims

def FindClosestNode(edgePoint,poly1,footprint, EdgeP1 = (None,None)):
    shorter = 0
    satisfied = 0
    Point = []
    GoodPoint = True
    while satisfied == 0:
        Point = sorted(
            product([edgePoint] * len(footprint), footprint),
            key=lambda x: x[0].relative_distance(x[1]),
        )[shorter * len(footprint)][1]
        seg1 = LineString([edgePoint, Point])

        shorter += 1
        for i in poly1.edges:
            satisfied = 1
            if seg1.intersects(LineString(i)):
                if not edgePoint in i:
                    satisfied = 0
                    break
            else:
                if EdgeP1:                        #tries to avoid triangles is possible, but...some case might lead to more weird situations...
                    if Point == EdgeP1:
                        GoodPoint = False
                #         break
                if shorter == len(poly1.edges):
                    satisfied = 1
    return Point, GoodPoint

def CheckFootprintNodes(footprint):
    node2remove = []
    newfootprint =[]
    for i in range(len(footprint)-2):
        slope1 = abs((footprint[i][1]-footprint[i+1][1])/(footprint[i][0]-footprint[i+1][0]))
        slope2 = abs((footprint[i+1][1] - footprint[i+2][1]) / (footprint[i+1][0] - footprint[i+2][0]))
        if abs(slope1-slope2)<1e-1:
            node2remove.append(i+1)
    for idx, node in enumerate(footprint):
        if not idx in node2remove:
            newfootprint.append(node)
    return newfootprint

def core_perim_zone_coordinates(footprint, perim_depth):
    """Returns a dictionary with the coordinates of the core/perimeter zones and
    a list of tuples containing the coordinates for the core zone."""
    #check for any angle to close to 180deg because it generates extra perimeter's zones
    footprint = CheckFootprintNodes(footprint)
    zones_perim = get_perims(footprint, get_core(footprint, perim_depth))
    core = get_core(footprint, perim_depth)

    zones_dict = {}
    if not(zones_perim):
        return False
    for idx, zone_perim in enumerate(zones_perim, 1):
        zone_name = "Perimeter_Zone_%i" % idx
        perim_zones_coords = []
        for pts in zone_perim:
            perim_zones_coords.append(pts.as_tuple(dims=2))
        zones_dict[zone_name] = perim_zones_coords
    core_zone_coords = []
    for pts in core:
        core_zone_coords.append(pts.as_tuple(dims=2))

    zones_dict["Core_Zone"] = core_zone_coords
    return zones_dict, core_zone_coords
