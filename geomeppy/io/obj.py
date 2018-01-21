"""
Module for export of .obj files
-------------------------------

The OBJ file format developed by Wavefront Technologies is used in programs like Blender to represent 3D models.

`Geomeppy` is able to output simple .obj files, and accompanying .mtl files to represent materials. This module
contains the source code for this operation. It should be treated as developers' reference only. As a user, if you
want to create a .obj file it is best to use the `IDF.to_obj()` function.

The generated files can be viewed online at https://3dviewer.net/. Drag the .obj file and the .mtl file into the
browser and you will be able to interact with a zoomable, rotatable model of your IDF.

`OBJ file specifications <https://www.cs.utah.edu/~boulos/cs3505/obj_spec.pdf>`_

`MTL file specifications <http://people.sc.fsu.edu/~jburkardt/data/mtl/mtl.html>`_

Example polygon::

    # vertices
    v 0.0 0.0 0.0
    v 1.0 0.0 0.0
    v 1.0 0.0 1.0
    v 0.0 0.0 1.0

    # face
    f 1// 2// 3// 4//

"""
from itertools import product
import shutil
from typing import List, Optional, Set  # noqa
import os

import pypoly2tri as p2t

if False: from ..idf import IDF  # noqa
from ..geom.polygons import Polygon2D, Polygon3D
from ..geom.vectors import Vector3D  # noqa

THIS_DIR = os.path.abspath(os.path.dirname(__file__))


class ObjWriter(object):
    """Container class holding the data needed to generate the .obj file."""
    faces = []  # type: List[int]
    vertices = []  # type: List[Vector3D]
    # v_set is used for fast testing if a vertex is in vertices
    v_set = set()  # type: Set[Vector3D]

    def from_surfaces(self, surfaces, subsurfaces, shading_surfaces):
        self.prepare_surfaces(surfaces, subsurfaces)
        self.prepare_shadingsurfaces(shading_surfaces)

    def prepare_surfaces(self, surfaces, subsurfaces):
        for i, surface in enumerate(surfaces):
            face_subsurfaces = [ss for ss in subsurfaces if ss.Building_Surface_Name == surface.Name]
            if face_subsurfaces:
                subsurface = face_subsurfaces[0]
                self.build_surface_with_subsurface(surface, subsurface)
            else:
                self.build_simple_surface(surface)

    def build_simple_surface(self, surface):
        poly = Polygon3D(surface.coords)
        poly2d = poly.project_to_2D()
        if poly2d.is_convex:
            # no need to triangulate the surface
            self.add_face(surface.coords, surface.Surface_Type)
            return
        coords = [p2t.shapes.Point(x, y) for x, y in poly2d.vertices]
        cdt = p2t.cdt.CDT(coords)
        cdt.Triangulate()
        triangles = cdt.GetTriangles()
        for t in triangles:
            tri2d = Polygon2D([(p.x, p.y) for p in t.points_])
            tri3d = tri2d.project_to_3D(poly)
            self.add_face(tri3d, surface.Surface_Type)
        return

    def build_surface_with_subsurface(self, surface, subsurface):
        outer_poly = Polygon3D(surface.coords)
        inner_poly = Polygon3D(subsurface.coords)
        for edge in outer_poly.edges:
            links = product(edge, inner_poly)
            links = sorted(links, key=lambda x: x[0].relative_distance(x[1]))
            pt1, pt2 = edge
            t1 = [pt1, links[0][1], pt2]
            t2 = [pt2, t1[1], links[1][1]]
            self.add_face(t1, surface.Surface_Type)
            self.add_face(t2, surface.Surface_Type)
        self.add_face(subsurface.coords, subsurface.Surface_Type, test=False)

    def prepare_shadingsurfaces(self, shading_surfaces):
        for s in shading_surfaces:
            self.add_face(s.coords, 'shade')

    def add_face(self, coords, mtl, test=True):
        face = []
        for v in coords:
            if test and v not in self.v_set:
                self.vertices.append(v)
                self.v_set.add(v)
                face.append(len(self.vertices))
            else:
                face.append(self.vertices.index(v) + 1)
        self.faces.append({'face': face, 'mtl': mtl})

    def write(self, fname, mtllib):
        """Write the .obj file.

        :param fname: A filename for the .obj file.
        :param mtllib: The name of a .mtl file to be referenced from the .obj file.
        """
        with open(fname, 'w') as f_out:
            f_out.write('# exported using geomeppy\n# https://github.com/jamiebull1/geomeppy\n')
            f_out.write('\n# vertices\n')
            for v in self.vertices:
                f_out.write('v %.6f %.6f %.6f\n' % (v[0], v[1], v[2]))
            f_out.write('\n# materials library\n')
            f_out.write('mtllib %s\n' % os.path.basename(mtllib))
            f_out.write('\n# faces\n')
            for f in self.faces:
                f_out.write('usemtl %s\n' % f['mtl'].lower())
                f_out.write('f %s//\n' % '// '.join((str(i) for i in f['face'])))


def export_to_obj(idf, fname=None, mtllib=None):
    # type: (IDF, Optional[str], Optional[str]) -> None
    """Export an OBJ file representation of the IDF.

    This can be used for viewing in tools which support the .obj format.

    :param idf: An IDF to export.
    :param fname: A filename for the .obj file. If None we try to base it on IDF.idfname and change the filetype.
    :param mtllib: The name of a .mtl file to be referenced from the .obj file. If None, we use default.mtl.
    """
    if not fname:
        name, _ext = os.path.splitext(idf.idfname)
        fname = '%s.obj' % name
    if not mtllib:
        name, _ext = os.path.splitext(fname)
        mtllib = '%s.mtl' % name
        shutil.copy(os.path.join(THIS_DIR, 'default.mtl'), mtllib)
    obj_writer = ObjWriter()
    surfaces = idf.getsurfaces()
    subsurfaces = idf.getsubsurfaces()
    shading_surfaces = idf.getshadingsurfaces()
    obj_writer.from_surfaces(surfaces, subsurfaces, shading_surfaces)
    obj_writer.write(fname, mtllib)
