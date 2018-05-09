"""
This module contains the implementation of `geomeppy.IDF`.
"""
import itertools
from typing import Any, Dict, List, Optional, Union  # noqa

from eppy.bunch_subclass import EpBunch  # noqa
from eppy.idf_msequence import Idf_MSequence  # noqa

from .geom.intersect_match import intersect_idf_surfaces, match_idf_surfaces
from .builder import Block, Zone
from .geom.polygons import bounding_box, Polygon2D  # noqa
from .geom.vectors import Vector2D, Vector3D  # noqa
from .io.obj import export_to_obj
from .patches import PatchedIDF
from .recipes import set_default_constructions, set_wwr, rotate, scale, translate, translate_to_origin
from .view_geometry import view_idf


def new_idf(fname):
    # type (Optional[str]) -> IDF
    """Create a new blank IDF.

    :param fname: A name for the new IDF.

    """
    idf = IDF()
    idf.new(fname)
    return idf


class IDF(PatchedIDF):
    """Geometry-enabled IDF class, usable in the same way as Eppy's IDF.

    This adds geometry functionality to Eppy's IDF class.

    """

    def intersect_match(self):
        # type: () -> None
        """Intersect all surfaces in the IDF, then set boundary conditions."""
        self.intersect()
        self.match()

    def intersect(self):
        # type: () -> None
        """Intersect all surfaces in the IDF."""
        intersect_idf_surfaces(self)

    def match(self):
        # type: () -> None
        """Set boundary conditions for all surfaces in the IDF."""
        match_idf_surfaces(self)

    def translate_to_origin(self):
        # type: () -> None
        """Move an IDF close to the origin so that it can be viewed in SketchUp."""
        translate_to_origin(self)

    def translate(self, vector):
        # type: (Vector2D) -> None
        """Move the IDF in the direction given by a vector.

        :param vector: A vector to translate by.

        """
        surfaces = self.getsurfaces()
        translate(surfaces, vector)
        subsurfaces = self.getsubsurfaces()
        translate(subsurfaces, vector)
        shadingsurfaces = self.getshadingsurfaces()
        translate(shadingsurfaces, vector)

    def rotate(self, angle, anchor=None):
        # type: (Union[int, float], Optional[Union[Vector2D, Vector3D]]) -> None
        """Rotate the IDF counterclockwise by the angle given.

        :param angle: Angle (in degrees) to rotate by.
        :param anchor: Point around which to rotate. Default is the centre of the the IDF's bounding box.

        """
        anchor = anchor or self.centroid
        surfaces = self.getsurfaces()
        subsurfaces = self.getsubsurfaces()
        shadingsurfaces = self.getshadingsurfaces()
        self.translate(-anchor)
        rotate(surfaces, angle)
        rotate(subsurfaces, angle)
        rotate(shadingsurfaces, angle)
        self.translate(anchor)

    def scale(self, factor, anchor=None):
        # type: (Union[int, float], Optional[Union[Vector2D, Vector3D]]) -> None
        """Scale the IDF by a scaling factor.

        :param factor: Factor to scale by.
        :param anchor: Point to scale around. Default is the centre of the the IDF's bounding box.

        """
        anchor = anchor or self.centroid
        surfaces = self.getsurfaces()
        subsurfaces = self.getsubsurfaces()
        shadingsurfaces = self.getshadingsurfaces()
        self.translate(-anchor)
        scale(surfaces, factor)
        scale(subsurfaces, factor)
        scale(shadingsurfaces, factor)
        self.translate(anchor)

    def set_default_constructions(self):
        # type: () -> None
        set_default_constructions(self)

    def bounding_box(self):
        # type: () -> Polygon2D
        """Calculate the site bounding box.

        :returns: A polygon of the bounding box.

        """
        floors = self.getsurfaces('floor')
        return bounding_box(floors)

    @property
    def centroid(self):
        # type: () -> Vector2D
        """Calculate the centroid of the site bounding box.

        :returns: The centroid of the site bounding box.

        """
        bbox = self.bounding_box()
        return bbox.centroid

    def getsurfaces(self, surface_type=None):
        # type: (Optional[str]) -> Union[List[EpBunch], Idf_MSequence]
        """Return all surfaces in the IDF.

        :param surface_type: Type of surface to get. Defaults to all.
        :returns: IDF surfaces.

        """
        surfaces = itertools.chain.from_iterable(
            [self.idfobjects[key.upper()] for key in self.idd_index['ref2names']['SurfaceNames']]
        )
        if surface_type:
            surfaces = filter(lambda x: x.Surface_Type.lower() == surface_type.lower(), surfaces)
        return list(surfaces)

    def getsubsurfaces(self, surface_type=None):
        # type: (Optional[str]) -> Union[List[EpBunch], Idf_MSequence]
        """Return all subsurfaces in the IDF.

        :param surface_type: Type of surface to get. Defaults to all.
        :returns: IDF surfaces.

        """
        surfaces = itertools.chain.from_iterable(
            [self.idfobjects[key.upper()] for key in self.idd_index['ref2names']['SubSurfNames']]
        )
        if surface_type:
            surfaces = filter(lambda x: x.Surface_Type.lower() == surface_type.lower(), surfaces)
        return list(surfaces)

    def getshadingsurfaces(self, surface_type=None):
        # type: (Optional[str]) -> Union[List[EpBunch], Idf_MSequence]
        """Return all subsurfaces in the IDF.

        :param surface_type: Type of surface to get. Defaults to all.
        :returns: IDF surfaces.

        """
        surfaces = itertools.chain.from_iterable(
            [self.idfobjects[key.upper()] for key in self.idd_index['ref2names']['AllShadingSurfNames']]
        )
        if surface_type:
            surfaces = filter(lambda x: x.Surface_Type.lower() == surface_type.lower(), surfaces)
        return list(surfaces)

    def set_wwr(self, wwr=0.2, construction=None, force=False, wwr_map={}, orientation=None):
        # type: (Optional[float], Optional[str], Optional[bool], Optional[dict], Optional[str]) -> None
        """Add strip windows to all external walls.

        Different WWR can be applied to specific wall orientations using the `wwr_map` keyword arg.
        This map is a dict of wwr values, keyed by `wall.azimuth`, which overrides the default passed as `wwr`.

        They can also be applied to walls oriented to a compass point, e.g. north, which will apply to walls which
        have an azimuth within 45 degrees of due north.

        :param wwr: Window to wall ratio in the range 0.0 to 1.0.
        :param construction: Name of a window construction.
        :param force: True to remove all subsurfaces before setting the WWR.
        :param wwr_map: Mapping from wall orientation (azimuth) to WWR, e.g. {180: 0.25, 90: 0.2}.
        :param orientation: One of "north", "east", "south", "west". Walls within 45 degrees will be affected.

        """
        set_wwr(self, wwr, construction, force, wwr_map, orientation)

    def view_model(self, test=False):
        # type: (Optional[bool]) -> None
        """Show a zoomable, rotatable representation of the IDF."""
        view_idf(idf_txt=self.idfstr(), test=test)

    def to_obj(self, fname=None, mtllib=None):
        # type: (Optional[str], Optional[str]) -> None
        """Export an OBJ file representation of the IDF.

        This can be used for viewing in tools which support the .obj format.

        :param fname: A filename for the .obj file. If None we try to base it on IDF.idfname and change the filetype.
        :param mtllib: The name of a .mtl file to be referenced from the .obj file. If None, we use default.mtl.
        """
        if not fname:
            try:
                fname = self.idfname.replace('.idf', '.obj')
            except AttributeError:
                fname = 'default.obj'
        export_to_obj(self, fname, mtllib)

    def add_block(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        """Add a block to the IDF.

        :param name: A name for the block.
        :param coordinates: A list of (x, y) tuples representing the building outline.
        :param height: The height of the block roof above ground level.
        :param num_stories: The total number of stories including basement stories. Default : 1.
        :param below_ground_stories: The number of stories below ground. Default : 0.
        :param below_ground_storey_height: The height of each basement storey. Default : 2.5.

        """
        block = Block(*args, **kwargs)
        zoning = kwargs.get('zoning', 'by_storey')
        if zoning == 'by_storey':
            zones = [Zone('Block %s Storey %i' %
                          (block.name, storey['storey_no']), storey)
                     for storey in block.stories]
        else:
            raise ValueError('%s is not a valid zoning rule' % zoning)
        for zone in zones:
            self.add_zone(zone)

    def add_shading_block(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        """Add a shading block to the IDF.

        :param name: A name for the block.
        :param coordinates: A list of (x, y) tuples representing the building outline.
        :param height: The height of the block roof above ground level.
        :param num_stories: The total number of stories including basement stories. Default : 1.
        :param below_ground_stories: The number of stories below ground. Default : 0.
        :param below_ground_storey_height: The height of each basement storey. Default : 2.5.

        """
        block = Block(*args, **kwargs)
        for i, wall in enumerate(block.walls[0], 1):
            if wall.area <= 0:
                continue
            s = self.newidfobject(
                'SHADING:SITE:DETAILED',
                Name='%s_%s' % (block.name, i),
            )
            try:
                s.setcoords(wall)
            except ZeroDivisionError:
                self.removeidfobject(s)

    def add_zone(self, zone):
        # type: (Zone) -> None
        """Add a zone to the IDF.

        :param zone: A Zone object holding details about the zone.

        """
        try:
            ggr = self.idfobjects['GLOBALGEOMETRYRULES'][0]  # type: Dict[str, Idf_MSequence]
        except IndexError:
            ggr = None
        # add zone object
        self.newidfobject('ZONE', Name=zone.name)

        for surface_type in zone.__dict__.keys():
            if surface_type == 'name':
                continue
            for i, surface_coords in enumerate(zone.__dict__[surface_type], 1):
                if not surface_coords:
                    continue
                name = '{name} {s_type} {num:04d}'.format(name=zone.name, s_type=surface_type[:-1].title(), num=i)
                s = self.newidfobject(
                    'BUILDINGSURFACE:DETAILED',
                    Name=name,
                    Surface_Type=surface_type[:-1],
                    Zone_Name=zone.name,
                )
                s.setcoords(surface_coords, ggr)
