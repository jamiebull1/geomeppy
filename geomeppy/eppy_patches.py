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

from eppy import bunchhelpers
from eppy import iddgaps
import eppy
from eppy.EPlusInterfaceFunctions import readidf
from eppy.bunch_subclass import EpBunch as BaseBunch
from eppy.idf_msequence import Idf_MSequence
from eppy.idfreader import addfunctions
from eppy.idfreader import convertallfields
from eppy.idfreader import iddversiontuple
from eppy.idfreader import idfreader1
from eppy.modeleditor import IDDNotSetError
from eppy.modeleditor import IDF as BaseIDF
from eppy.modeleditor import addthisbunch
from eppy.modeleditor import newrawobject
from eppy.modeleditor import obj2bunch
from geomeppy.intersect_match import set_coords


class EpBunch(BaseBunch):
    """Monkey-patched EpBunch to add the setcoords function.
    """
    
    def __init__(self, *args, **kwargs):
        super(EpBunch, self).__init__(*args, **kwargs)
    
    def setcoords(self, poly, ggr):
        """Set the coordinates of a surface.
        
        Parameters
        ----------
        poly : Polygon3D or list
             Either a Polygon3D object of a list of (x,y,z) tuples.
        ggr : EpBunch
            A GlobalGeometryRules IDF object.
            
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

eppy.bunch_subclass.EpBunch = EpBunch
        

def addfunctions2new(abunch, key):
    """Monkeypatched bugfix for add functions to a new bunch/munch object"""
    snames = [
        "BuildingSurface:Detailed",
        "Wall:Detailed",
        "RoofCeiling:Detailed",
        "Floor:Detailed",
        "FenestrationSurface:Detailed",
        "Shading:Site:Detailed",
        "Shading:Building:Detailed",
        "Shading:Zone:Detailed", ]
    snames = [sname.upper() for sname in snames]
    if key.upper() in snames:
        abunch.__functions.update({
            'area': eppy.function_helpers.area,
            'height': eppy.function_helpers.height,
            'width': eppy.function_helpers.width,
            'azimuth': eppy.function_helpers.azimuth,
            'tilt': eppy.function_helpers.tilt,
            'coords': eppy.function_helpers.getcoords,
        })
    return abunch

eppy.idfreader.addfunctions2new = addfunctions2new


def idfreader1(fname, iddfile, conv=True, commdct=None, block=None):
    """read idf file and return bunches"""
    versiontuple = iddversiontuple(iddfile)
    block, data, commdct = readidf.readdatacommdct1(
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
    iddgaps.missingkeys_nonstandard(commdct, dtls, nofirstfields)
  
    bunchdt = makebunches(data, commdct)
    addfunctions(dtls, bunchdt)
  
    return bunchdt, block, data, commdct
  
def makebunches(data, commdct):
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
        bunchdt[key] = Idf_MSequence(list1, objs)
    return bunchdt
  

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
    
    def read(self):
        """Read the IDF file and the IDD file.
        
        Monkey-patched by GeomEppy to allow us to add additional functions to
        IDF objects.
        
        If the idd file had been already read, it will not be read again.
        Read populates the following data structures:

        - idfobjects
        - model
        - idd_info # done only once
        
        """
        if self.getiddname() == None:
            errortxt = "IDD file needed to read the idf file. Set it using IDF.setiddname(iddfile)"
            raise IDDNotSetError(errortxt)
        readout = idfreader1(
            self.idfname, self.iddname,
            commdct=self.idd_info, block=self.block)
        self.idfobjects, block, self.model, idd_info = readout

        self.__class__.setidd(idd_info, block)
            
    def copyidfobject(self, idfobject):
        """Monkey-patched to add the return value.
        """
        abunch = addthisbunch(self.idfobjects,
                              self.model,
                              self.idd_info,
                              idfobject)
        abunch = addfunctions2new(abunch, abunch.key)
        
        return abunch

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
        self.idfobjects[key].append(abunch)
        for k, v in list(kwargs.items()):
            abunch[k] = v
        abunch = addfunctions2new(abunch, abunch.key)
        return abunch
        