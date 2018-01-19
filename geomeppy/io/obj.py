"""Module for import and export of .obj files as produced by Blender.

These can be viewed online at https://3dviewer.net/

OBJ file specifications: https://www.cs.utah.edu/~boulos/cs3505/obj_spec.pdf
MTL file specifications: http://people.sc.fsu.edu/~jburkardt/data/mtl/mtl.html

Example polygon:

 # vertices
 v 0.0 0.0 0.0
 v 1.0 0.0 0.0
 v 1.0 0.0 1.0
 v 0.0 0.0 1.0

 # face
 f 1// 2// 3// 4//

"""
from itertools import product

import pypoly2tri as p2t

from ..geom.polygons import Polygon2D, Polygon3D


def export_to_obj(idf, fname=None, mtllib=None):
    # type: (IDF, Optional[str], Optional[str]) -> None
    """Export an OBJ file representation of the IDF.

    This can be used for viewing in tools which support the .obj format.

    :param idf: An IDF to export.
    :param fname: A filename for the .obj file. If None we try to base it on IDF.idfname and change the filetype.
    :param mtllib: The name of a .mtl file to be referenced from the .obj file. If None, we use default.mtl.
    """
    if not fname:
        fname = idf.idfname.replace('.idf', '.obj')
    if not mtllib:
        mtllib = 'default.mtl'
    vertices = []
    faces = []
    surfaces = idf.getsurfaces()
    subsurfaces = idf.getsubsurfaces()
    shading_surfaces = idf.getshadingsurfaces()
    faces, vertices = get_faces_and_vertices(faces, shading_surfaces, subsurfaces, surfaces, vertices)
    write_obj(faces, vertices, fname, mtllib)


def get_faces_and_vertices(faces, shading_surfaces, subsurfaces, surfaces, vertices):
    faces, vertices = prepare_surfaces(faces, subsurfaces, surfaces, vertices)
    faces, vertices = prepare_subsurfaces(faces, subsurfaces, vertices)
    faces, vertices = prepare_shadingsurfaces(faces, shading_surfaces, vertices)
    return faces, vertices


def prepare_shadingsurfaces(faces, shading_surfaces, vertices):
    for s in shading_surfaces:
        face = []
        for v in s.coords:
            if v not in vertices:
                vertices.append(v)
            face.append(vertices.index(v) + 1)
        faces.append({'face': face, 'mtl': 'shade'})
    return faces, vertices


def prepare_subsurfaces(faces, subsurfaces, vertices):
    for s in subsurfaces:
        face = []
        for v in s.coords:
            if v not in vertices:
                vertices.append(v)
            face.append(vertices.index(v) + 1)
        faces.append({'face': face, 'mtl': s.Surface_Type})
    return faces, vertices


def prepare_surfaces(faces, subsurfaces, surfaces, vertices):
    for surface in surfaces:
        face_subsurfaces = [ss for ss in subsurfaces if ss.Building_Surface_Name == surface.Name]
        faces, vertices = build_face(surface, face_subsurfaces, faces, vertices)
    return faces, vertices


def build_face(surface, face_subsurfaces, faces, vertices):
    if not face_subsurfaces:
        return build_simple_surface(faces, surface, vertices)
    return build_surface_with_hole(face_subsurfaces, faces, surface, vertices)


def build_simple_surface(faces, surface, vertices):
    poly = Polygon3D(surface.coords)
    poly2d = poly.project_to_2D()
    coords = [p2t.shapes.Point(x, y) for x, y in poly2d.vertices]
    cdt = p2t.cdt.CDT(coords)
    cdt.Triangulate()
    triangles = cdt.GetTriangles()
    for t in triangles:
        face = []
        tri2d = Polygon2D([(p.x, p.y) for p in t.points_])
        tri3d = tri2d.project_to_3D(poly)
        for v in tri3d:
            if v not in vertices:
                vertices.append(v)
            face.append(vertices.index(v) + 1)
        faces.append({'face': face, 'mtl': surface.Surface_Type})
    return faces, vertices


def build_surface_with_hole(face_subsurfaces, faces, surface, vertices):
    outer_poly = Polygon3D(surface.coords)
    inner_poly = Polygon3D(face_subsurfaces[0].coords)
    for edge in outer_poly.edges:
        links = product(edge, inner_poly)
        links = sorted(links, key=lambda x: x[0].relative_distance(x[1]))
        pt1, pt2 = edge
        t1 = [pt1, links[0][1], pt2]
        face = []
        for v in t1:
            if v not in vertices:
                vertices.append(v)
            face.append(vertices.index(v) + 1)
        faces.append({'face': face, 'mtl': surface.Surface_Type})
        t2 = [pt2, t1[1], links[1][1]]
        face = []
        for v in t2:
            if v not in vertices:
                vertices.append(v)
            face.append(vertices.index(v) + 1)
        faces.append({'face': face, 'mtl': surface.Surface_Type})
    return faces, vertices


def write_obj(faces, vertices, fname, mtllib):
    with open(fname, 'w') as f_out:
        f_out.write('# exported using geomeppy\n# https://github.com/jamiebull1/geomeppy\n')
        f_out.write('\n# vertices\n')
        for v in vertices:
            f_out.write('v %.6f %.6f %.6f\n' % (v[0], v[1], v[2]))
        f_out.write('\n# materials library\n')
        f_out.write('mtllib %s\n' % mtllib)
        f_out.write('\n# faces\n')
        for f in faces:
            f_out.write('usemtl %s\n' % f['mtl'].lower())
            f_out.write('f %s//\n' % '// '.join((str(i) for i in f['face'])))
