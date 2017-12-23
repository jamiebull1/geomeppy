# Copyright (c) 2016 Jamie Bull
# Copyright (c) 2012 Santosh Philip
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""
Monkey patches for changes to classes and functions in Eppy. These include
fixes which have not yet made it to the released version of Eppy. These will be
removed if/when they are added to Eppy. It also includes the addition of features
specific to geometry editing which may or may not be included future versions
of Eppy.

"""
import copy
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union  # noqa

from eppy import bunchhelpers, iddgaps
from eppy.EPlusInterfaceFunctions import eplusdata, iddindex, parse_idd
from eppy.EPlusInterfaceFunctions.eplusdata import Eplusdata  # noqa
from eppy.bunch_subclass import EpBunch as BaseBunch
from eppy.idf_msequence import Idf_MSequence
from eppy.idfreader import convertallfields, iddversiontuple
from eppy.modeleditor import IDDNotSetError, IDF as BaseIDF, namebunch, newrawobject
from six import StringIO  # noqa

from geomeppy.geom.intersect_match import (
    intersect_idf_surfaces,
    getidfsurfaces,
    getidfsubsurfaces,
    match_idf_surfaces,
    set_coords,
)
from .builder import Block, Zone
from .geom.polygons import Polygon, Polygon3D  # noqa
from .geom.vectors import Vector2D, Vector3D  # noqa
from .recipes import set_default_constructions, set_wwr, rotate, scale, translate, translate_to_origin
from .view_geometry import view_idf


class EpBunch(BaseBunch):
    """Monkeypatched EpBunch to add the setcoords function."""

    def setcoords(self,
                  poly,  # type: Union[List[Vector3D], Polygon3D]
                  ggr=None  # type: Union[List, None, Idf_MSequence]
                  ):
        # type: (...) -> None
        """Set the coordinates of a surface.

        :param poly: Either a Polygon3D object of a list of (x,y,z) tuples.
        :param ggr: A GlobalGeometryRules IDF object. Defaults to None.

        """
        surfaces = [
            "BUILDINGSURFACE:DETAILED",
            "WALL:DETAILED",
            "ROOFCEILING:DETAILED",
            "FLOOR:DETAILED",
            "FENESTRATIONSURFACE:DETAILED",
            "SHADING:SITE:DETAILED",
            "SHADING:BUILDING:DETAILED",
            "SHADING:ZONE:DETAILED", ]
        if self.key.upper() in surfaces:
            set_coords(self, poly, ggr)
        else:
            raise AttributeError


def idfreader1(fname,  # type: StringIO
               iddfile,  # type: StringIO
               theidf,  # type: IDF
               conv=True,  # type: Optional[bool]
               commdct=None,  # type: Optional[List[Union[List[Dict[str, Any]], List[Dict[str, Option]]]]]
               block=None  # type: Optional[List[List[str]]]
               ):
    # type: (...) -> Tuple[Dict, List, Eplusdata, List[Dict, Dict], Dict, Tuple[int]]
    # would like to have:
    # - type: (...) -> Tuple[Dict[str, Idf_MSequence], List[List[str]], Eplusdata, List[Union[List[Dict[str, Any]],
    # List[Dict[str, Optional[str]]]]], Dict[str, Dict[str, Any]], Tuple[int]]
    """Read idf file and return bunches.

    :param fname: Name of the IDF file to read.
    :param iddfile: Name of the IDD file to use to interpret the IDF.
    :param conv: If True, convert strings to floats and integers where marked in the IDD. Defaults to None.
    :param commdct: Descriptions of IDF fields from the IDD. Defaults to None.
    :param block: EnergyPlus field ID names of the IDF from the IDD. Defaults to None.
    :returns: bunchdt Dict of lists of idf_MSequence objects in the IDF.
    :returns: block EnergyPlus field ID names of the IDF from the IDD.
    :returns data: Eplusdata object containing representions of IDF objects.
    :returns: commdct List of names of IDF objects.
    :returns: idd_index A pair of dicts used for fast lookups of names of groups of objects.
    :returns: versiontuple Version of EnergyPlus from the IDD.

    """
    versiontuple = iddversiontuple(iddfile)
    block, data, commdct, idd_index = readdatacommdct1(
        fname,
        iddfile=iddfile,
        commdct=commdct,
        block=block)
    if conv:
        convertallfields(data, commdct)
    # fill gaps in idd
    if versiontuple < (8,):
        skiplist = ["TABLE:MULTIVARIABLELOOKUP"]
    else:
        skiplist = None
    nofirstfields = iddgaps.missingkeys_standard(
        commdct, data.dtls,
        skiplist=skiplist)
    iddgaps.missingkeys_nonstandard(block, commdct, data.dtls, nofirstfields)
    bunchdt = makebunches(data, commdct, theidf)

    return bunchdt, block, data, commdct, idd_index, versiontuple


def readdatacommdct1(idfname, iddfile='Energy+.idd', commdct=None, block=None):
    # type: (str, Optional[str], Optional[Dict], Optional[List]) -> Tuple[List, Eplusdata, List[Dict, Dict], Dict]
    """Read the idf file.

    This is patched so that the IDD index is not lost when reading a new IDF without reloading the modeleditor module.

    :param idfname: Name of the IDF file to read.
    :param iddfile: Name of the IDD file to use to interpret the IDF.
    :param commdct: Descriptions of IDF fields from the IDD. Defaults to None.
    :param block: EnergyPlus field ID names of the IDF from the IDD. Defaults to None.
    :returns: block EnergyPlus field ID names of the IDF from the IDD.
    :returns data: Eplusdata object containing representions of IDF objects.
    :returns: commdct List of names of IDF objects.
    :returns: idd_index A pair of dicts used for fast lookups of names of groups of objects.

    """
    if not commdct:
        block, commlst, commdct, idd_index = parse_idd.extractidddata(iddfile)
        theidd = eplusdata.Idd(block, 2)
    else:
        theidd = eplusdata.Idd(block, 2)
        name2refs = iddindex.makename2refdct(commdct)
        ref2namesdct = iddindex.makeref2namesdct(name2refs)
        idd_index = dict(name2refs=name2refs, ref2names=ref2namesdct)
        commdct = iddindex.ref2names2commdct(ref2namesdct, commdct)
    data = eplusdata.Eplusdata(theidd, idfname)
    return block, data, commdct, idd_index


def addthisbunch(bunchdt,  # type: Dict[str, Idf_MSequence]
                 data,  # type: Eplusdata
                 commdct,  # type: List[Union[List[Dict[str, Any]], List[Dict[str, Option]]]]
                 thisbunch,  # type: EpBunch
                 _idf  # type: IDF
                 ):
    # type: (...) -> EpBunch
    """Add an object to the IDF. Monkeypatched to return the object.

    `thisbunch` usually comes from another idf file or it can be used to copy within the idf file.

    :param bunchdt: Dict of lists of idf_MSequence objects in the IDF.
    :param data: Eplusdata object containing representions of IDF objects.
    :param commdct: Descriptions of IDF fields from the IDD.
    :param thisbunch: The object to add to the model.
    :param _idf: The IDF object. Not used either here or in Eppy but kept for consistency with Eppy.
    :returns: The EpBunch object added.

    """
    key = thisbunch.key.upper()
    obj = copy.copy(thisbunch.obj)
    abunch = obj2bunch(data, commdct, obj)
    bunchdt[key].append(abunch)
    return abunch


def makebunches(data,  # type: Eplusdata
                commdct,  # type: List[Union[List[Dict[str, Any]], List[Dict[str, Optiona]]]]
                theidf  # type: IDF
                ):
    # type: (...) -> Dict[str, Idf_MSequence]
    """Make bunches with data.

    :param data: Eplusdata object containing representions of IDF objects.
    :param commdct: Descriptions of IDF fields from the IDD.
    :param theidf: The IDF object.
    :returns: Dict of lists of idf_MSequence objects in the IDF.

    """
    bunchdt = {}
    dt, dtls = data.dt, data.dtls
    for obj_i, key in enumerate(dtls):
        key = key.upper()
        objs = dt[key]
        list1 = []
        for obj in objs:
            bobj = makeabunch(commdct, obj, obj_i)
            list1.append(bobj)
        bunchdt[key] = Idf_MSequence(list1, objs, theidf)
    return bunchdt


def obj2bunch(data,  # type: Eplusdata
              commdct,  # type: List[Union[List[Dict[str, Any]], List[Dict[str, Optiona]]]]
              obj  # type: Union[List[Union[float, str]], List[str]]
              ):
    # type: (...) -> EpBunch
    """Make a new bunch object using the data object.

    :param data: Eplusdata object containing representions of IDF objects.
    :param commdct: Descriptions of IDF fields from the IDD.
    :param obj: List of field values in an object.
    :returns: EpBunch object.

    """
    dtls = data.dtls
    key = obj[0].upper()
    key_i = dtls.index(key)
    abunch = makeabunch(commdct, obj, key_i)
    return abunch


def makeabunch(commdct,  # type: List[Union[List[Dict[str, Any]], List[Dict[str, Optional[str]]]]]
               obj,  # type: Union[List[Union[float, str]], List[str]]
               obj_i  # type: int
               ):
    # type: (...) -> EpBunch
    """Make a bunch from the object.

    :param commdct: Descriptions of IDF fields from the IDD.
    :param obj: List of field values in an object.
    :param obj_i: Index of the object in commdct.
    :returns: EpBunch object.

    """
    objidd = commdct[obj_i]
    objfields = [comm.get('field') for comm in commdct[obj_i]]
    objfields[0] = ['key']
    objfields = [field[0] for field in objfields]
    obj_fields = [bunchhelpers.makefieldname(field) for field in objfields]
    bobj = EpBunch(obj, obj_fields, objidd)
    return bobj


class IDF(BaseIDF):
    """Monkey-patched IDF.

    Patched to add read (to add additional functionality) and to fix copyidfobject and newidfobject.

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

    def rotate(self, angle, anchor=None):
        # type: (Union[int, float], Optional[Union[Vector2D, Vector3D]]) -> None
        """Rotate the IDF counterclockwise by the angle given.

        :param angle: Angle (in degrees) to rotate by.
        :param anchor: Point around which to rotate. Default is the centre of the the IDF's bounding box.

        """
        anchor = anchor or self.centroid
        surfaces = self.getsurfaces()
        subsurfaces = self.getsubsurfaces()
        self.translate(-anchor)
        rotate(surfaces, angle)
        rotate(subsurfaces, angle)
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
        self.translate(-anchor)
        scale(surfaces, factor)
        scale(subsurfaces, factor)
        self.translate(anchor)

    def set_default_constructions(self):
        # type: () -> None
        set_default_constructions(self)

    def getsurfaces(self, surface_type=None):
        # type: (Optional[str]) -> Union[List[EpBunch], Idf_MSequence]
        """Return all surfaces in the IDF.

        :param surface: Type of surface to get. Defaults to all.
        :returns: IDF surfaces.

        """
        return getidfsurfaces(self, surface_type)

    def bounding_box(self):
        # type: () -> Polygon
        """Calculate the site bounding box.

        :returns: A polygon of the bounding box.

        """
        floors = self.getsurfaces('floor')
        top_left = Vector2D(
            min(min(Polygon(f.coords).xs) for f in floors),
            max(max(Polygon(f.coords).ys) for f in floors)
        )
        bottom_left = Vector2D(
            min(min(Polygon(f.coords).xs) for f in floors),
            min(min(Polygon(f.coords).ys) for f in floors)
        )
        bottom_right = Vector2D(
            max(max(Polygon(f.coords).xs) for f in floors),
            min(min(Polygon(f.coords).ys) for f in floors)
        )
        top_right = Vector2D(
            max(max(Polygon(f.coords).xs) for f in floors),
            max(max(Polygon(f.coords).ys) for f in floors)
        )
        return Polygon([top_left, bottom_left, bottom_right, top_right])

    @property
    def centroid(self):
        # type: () -> Vector2D
        """Calculate the centroid of the site bounding box.

        :returns: The centroid of the site bounding box.

        """
        bbox = self.bounding_box()
        return bbox.centroid

    def getsubsurfaces(self, surface_type=None):
        # type: (Optional[str]) -> Union[List[EpBunch], Idf_MSequence]
        """Return all subsurfaces in the IDF.

        :returns: IDF surfaces.

        """
        return getidfsubsurfaces(self, surface_type)

    def set_wwr(self, wwr, construction=None, force=False):
        # type: (float, Optional[str], Optional[bool]) -> None
        """Add strip windows to all external walls.

        :param wwr: Window to wall ratio in the range 0.0 to 1.0.
        :param construction: Name of a window construction.
        :param force: True to remove all subsurfaces before setting the WWR.

        """
        set_wwr(self, wwr, construction, force)

    def view_model(self):
        # type: () -> None
        """Show a zoomable, rotatable representation of the IDF."""
        view_idf(idf_txt=self.idfstr())

    def add_block(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        """Add a block to the IDF.

        See Block class for parameters.

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

        See Block class for parameters.

        """
        block = Block(*args, **kwargs)
        for i, wall in enumerate(block.walls[0], 1):
            if wall.area <= 0:
                continue
            s = self.newidfobject(
                'SHADING:SITE:DETAILED',
                '%s_%s' % (block.name, i))
            try:
                s.setcoords(wall)
            except ZeroDivisionError:
                self.removeidfobject(s)

    def add_zone(self, zone):
        # type: (Zone) -> None
        """Add a zone to the IDF.

        :param zone:

        """
        try:
            ggr = self.idfobjects['GLOBALGEOMETRYRULES'][0]  # type: Dict[str, Idf_MSequence]
        except IndexError:
            ggr = None
        # add zone object
        self.newidfobject('ZONE', zone.name)

        for surface_type in zone.__dict__.keys():
            if surface_type == 'name':
                continue
            for i, surface_coords in enumerate(zone.__dict__[surface_type], 1):
                if not surface_coords:
                    continue
                name = '{name} {s_type} {num:04d}'.format(name=zone.name, s_type=surface_type[:-1].title(), num=i)
                s = self.newidfobject('BUILDINGSURFACE:DETAILED', name,
                                      Surface_Type=surface_type[:-1],
                                      Zone_Name=zone.name)
                s.setcoords(surface_coords, ggr)

    def read(self):
        # type: () -> None
        """Read the IDF file and the IDD file.

        If the IDD file had already been read, it will not be read again.

        Populates the following data structures::

        - idfobjects : list
        - model : list
        - idd_info : list
        - idd_index : dict

        """
        if self.getiddname() is None:
            errortxt = (
                "IDD file needed to read the idf file. Set it using IDF.setiddname(iddfile)")
            raise IDDNotSetError(errortxt)
        self.idfobjects, block, self.model, idd_info, idd_index, versiontuple = idfreader1(
            self.idfname,
            self.iddname,
            self,
            commdct=self.idd_info,
            block=self.block,
        )
        self.__class__.setidd(idd_info, idd_index, block, versiontuple)

    def newidfobject(self, key, aname='', **kwargs):
        # type: (str, str, **Any) -> EpBunch
        """Add a new idfobject to the model.

        If you don't specify a value for a field, the default value will be set.

        For example ::

            newidfobject("CONSTRUCTION")
            newidfobject("CONSTRUCTION",
                Name='Interior Ceiling_class',
                Outside_Layer='LW Concrete',
                Layer_2='soundmat')

        :param key: The type of IDF object. This must be in ALL_CAPS.
        :param aname: This parameter is not used. It is left there for backward compatibility.
        :param kwargs: Keyword arguments in the format `field=value` used to set fields in the EnergyPlus object.
        :returns: EpBunch object.

        """
        obj = newrawobject(self.model, self.idd_info, key)
        abunch = obj2bunch(self.model, self.idd_info, obj)
        if aname:
            warnings.warn(
                "The aname parameter should no longer be used.", UserWarning)
            namebunch(abunch, aname)
        self.idfobjects[key].append(abunch)  # type: Dict[str, Idf_MSequence]
        for k, v in kwargs.items():
            abunch[k] = v
        return abunch

    def copyidfobject(self, idfobject):
        # type: (EpBunch) -> EpBunch
        """Add an IDF object to the IDF.

        This has been monkey-patched to add the return value.

        :param idfobject: The IDF object to copy. Usually from another IDF, or it can be used to copy within this IDF.
        :returns: EpBunch object.

        """
        return addthisbunch(self.idfobjects, self.model, self.idd_info, idfobject, self)
