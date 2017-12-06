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
removed as soon as Eppy catches up. It also includes the addition of features
specific to geometry editing which may or may not be included future versions
of Eppy.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy
from geomeppy.builder import Block
from geomeppy.builder import Zone
from geomeppy.intersect_match import getidfsubsurfaces
from geomeppy.intersect_match import getidfsurfaces
from geomeppy.intersect_match import intersect_idf_surfaces
from geomeppy.intersect_match import match_idf_surfaces
from geomeppy.intersect_match import set_coords
from geomeppy.recipes import set_default_constructions
from geomeppy.recipes import set_wwr
from geomeppy.recipes import translate
from geomeppy.recipes import translate_to_origin
from geomeppy.view_geometry import view_idf

from eppy import bunchhelpers
from eppy import iddgaps
from eppy.EPlusInterfaceFunctions import readidf
from eppy.bunch_subclass import EpBunch as BaseBunch
from eppy.idf_msequence import Idf_MSequence
from eppy.idfreader import convertallfields
from eppy.idfreader import iddversiontuple
from eppy.idfreader import idfreader1
from eppy.idfreader import makeabunch
from eppy.modeleditor import IDDNotSetError
from eppy.modeleditor import IDF as BaseIDF
from eppy.modeleditor import addthisbunch
from eppy.modeleditor import namebunch
from eppy.modeleditor import newrawobject
from eppy.modeleditor import obj2bunch
from py._log import warning


class EpBunch(BaseBunch):
    """Monkey-patched EpBunch to add the setcoords function.
    """
     
    def __init__(self, *args, **kwargs):
        super(EpBunch, self).__init__(*args, **kwargs)

    def setcoords(self, poly, ggr=None):
        """Set the coordinates of a surface.
         
        Parameters
        ----------
        poly : Polygon3D or list
             Either a Polygon3D object of a list of (x,y,z) tuples.
        ggr : EpBunch, optional
            A GlobalGeometryRules IDF object. Defaults to None.
             
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
             

def idfreader1(fname, iddfile, theidf, conv=True, commdct=None, block=None):
    """read idf file and return bunches"""
    versiontuple = iddversiontuple(iddfile)
    block, data, commdct, idd_index = readidf.readdatacommdct1(
        fname,
        iddfile=iddfile,
        commdct=commdct,
        block=block)
    if conv:
        convertallfields(data, commdct)
    # fill gaps in idd
    ddtt, dtls = data.dt, data.dtls
    if versiontuple < (8,):
        skiplist = ["TABLE:MULTIVARIABLELOOKUP"]
    else:
        skiplist = None
    nofirstfields = iddgaps.missingkeys_standard(
        commdct, dtls,
        skiplist=skiplist)
    iddgaps.missingkeys_nonstandard(block, commdct, dtls, nofirstfields)
    # bunchdt = makebunches(data, commdct)
    bunchdt = makebunches(data, commdct, theidf)

    return bunchdt, block, data, commdct, idd_index, versiontuple


def addthisbunch(bunchdt, data, commdct, thisbunch, theidf):
    """add a bunch to model.
    abunch usually comes from another idf file
    or it can be used to copy within the idf file"""
    key = thisbunch.key.upper()
    obj = copy.copy(thisbunch.obj)
    abunch = obj2bunch(data, commdct, obj)
    bunchdt[key].append(abunch)
    return abunch


def makebunches(data, commdct, theidf):
    """make bunches with data"""
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


def obj2bunch(data, commdct, obj):
    """make a new bunch object using the data object"""
    dtls = data.dtls
    key = obj[0].upper()
    key_i = dtls.index(key)
    abunch = makeabunch(commdct, obj, key_i)
    return abunch


def makeabunch(commdct, obj, obj_i):
    """make a bunch from the object"""
    objidd = commdct[obj_i]
    objfields = [comm.get('field') for comm in commdct[obj_i]]
    objfields[0] = ['key']
    objfields = [field[0] for field in objfields]
    obj_fields = [bunchhelpers.makefieldname(field) for field in objfields]
    bobj = EpBunch(obj, obj_fields, objidd)
    return bobj


class IDF(BaseIDF):
    """Monkey-patched IDF.
    
    Patched to add read (to add additional functionality) and to fix 
    copyidfobject and newidfobject.
    
    """
    
    def __init__(self, *args, **kwargs):
        super(IDF, self).__init__(*args, **kwargs)
        
    def intersect_match(self):
        """Intersect all surfaces in the IDF, then set boundary conditions.
        """
        self.intersect()
        self.match()
        
    def intersect(self):
        """Intersect all surfaces in the IDF.
        """
        intersect_idf_surfaces(self)
        
    def match(self):
        """Set boundary conditions for all surfaces in the IDF.
        """
        match_idf_surfaces(self)
    
    def translate_to_origin(self):
        """
        Move an IDF close to the origin so that it can be viewed in SketchUp.
        """
        translate_to_origin(self)
    
    def translate(self, vector):
        """Move the IDF in the direction given by a vector.
        
        Parameters
        ----------
        vector : Vector2D, Vector3D, (x,y) or (x,y,z) list-like
            Representation of a vector to translate by.
            
        """
        surfaces = self.getsurfaces()
        translate(surfaces, vector)
    
    def set_default_constructions(self):
        set_default_constructions(self)
    
    def getsurfaces(self, surface_type=None):
        """Return all surfaces in the IDF.
        
        Returns
        -------
        list
        
        """
        return getidfsurfaces(self, surface_type)
    
    def getsubsurfaces(self, surface_type=None):
        """Return all subsurfaces in the IDF.
        
        Returns
        -------
        list
        
        """
        return getidfsubsurfaces(self, surface_type)
    
    def set_wwr(self, wwr):
        """Add strip windows to all external walls.
        
        Parameters
        ----------
        wwr : float
            Window to wall ratio in the range 0-1.
            
        """
        set_wwr(self, wwr)
    
    def view_model(self):
        """Show a zoomable, rotatable representation of the IDF.
        """
        view_idf(idf_txt=self.idfstr())
        
    def add_block(self, *args, **kwargs):
        """Add a block to the IDF
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
        """Add a shading block to the IDF
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
        try:
            ggr = self.idfobjects['GLOBALGEOMETRYRULES'][0]
        except IndexError:
            ggr = None
        # add zone object
        self.newidfobject('ZONE', zone.name)
        # add wall objects
        for i, surface_coords in enumerate(zone.walls, 1):
            if not surface_coords:
                continue
            name = '%s Wall %04d' % (zone.name, i)
            s = self.newidfobject('BUILDINGSURFACE:DETAILED', name,
                    Surface_Type = 'wall',
                    Zone_Name = zone.name)
            s.setcoords(surface_coords, ggr)
        # add floor objects
        for i, surface_coords in enumerate(zone.floors, 1):
            if not surface_coords:
                continue
            name = '%s Floor %04d' % (zone.name, i)
            s = self.newidfobject('BUILDINGSURFACE:DETAILED', name,
                    Surface_Type = 'floor',
                    Zone_Name = zone.name)
            s.setcoords(surface_coords, ggr)
        # add ceiling objects
        for i, surface_coords in enumerate(zone.ceilings, 1):
            if not surface_coords:
                continue
            name = '%s Ceiling %04d' % (zone.name, i)
            s = self.newidfobject('BUILDINGSURFACE:DETAILED', name,
                    Surface_Type = 'ceiling',
                    Zone_Name = zone.name)
            s.setcoords(surface_coords, ggr)
        # add roof objects
        for i, surface_coords in enumerate(zone.roofs, 1):
            if not surface_coords:
                continue
            name = '%s Roof %04d' % (zone.name, i)
            s = self.newidfobject('BUILDINGSURFACE:DETAILED', name,
                    Surface_Type = 'roof',
                    Zone_Name = zone.name)
            s.setcoords(surface_coords, ggr)

    def read(self):
        """
        Read the IDF file and the IDD file. If the IDD file had already been
        read, it will not be read again.

        Read populates the following data structures:

        - idfobjects : list
        - model : list
        - idd_info : list
        - idd_index : dict

        """
        if self.getiddname() == None:
            errortxt = ("IDD file needed to read the idf file. "
                        "Set it using IDF.setiddname(iddfile)")
            raise IDDNotSetError(errortxt)
        readout = idfreader1(
            self.idfname, self.iddname, self,
            commdct=self.idd_info, block=self.block)
        self.idfobjects, block, self.model, idd_info, idd_index, versiontuple = readout
        self.__class__.setidd(idd_info, idd_index, block, versiontuple)
            

    def newidfobject(self, key, aname='', **kwargs):
        """
        Add a new idfobject to the model. If you don't specify a value for a
        field, the default value will be set.

        For example ::

            newidfobject("CONSTRUCTION")
            newidfobject("CONSTRUCTION",
                Name='Interior Ceiling_class',
                Outside_Layer='LW Concrete',
                Layer_2='soundmat')

        Parameters
        ----------
        key : str
            The type of IDF object. This must be in ALL_CAPS.
        aname : str, deprecated
            This parameter is not used. It is left there for backward 
            compatibility.
        **kwargs
            Keyword arguments in the format `field=value` used to set the value
            of fields in the IDF object when it is created. 

        Returns
        -------
        EpBunch object

        """
        obj = newrawobject(self.model, self.idd_info, key)
        abunch = obj2bunch(self.model, self.idd_info, obj)
        if aname:
            warning.warn("The aname parameter should no longer be used.")
            namebunch(abunch, aname)
        self.idfobjects[key].append(abunch)
        for k, v in kwargs.items():
            abunch[k] = v
        return abunch

    def copyidfobject(self, idfobject):
        """Add an IDF object to the IDF.
        
        This has been monkey-patched to add the return value.

        Parameters
        ----------
        idfobject : EpBunch object
            The IDF object to remove. This usually comes from another idf file,
            or it can be used to copy within this idf file.
        
        Returns
        -------
        EpBunch object

        """
        abunch = addthisbunch(self.idfobjects,
                             self.model,
                             self.idd_info,
                             idfobject,
                             self)
         
        return abunch
