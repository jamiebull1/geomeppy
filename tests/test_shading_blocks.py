# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""pytest for builder.py"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from tests.test_builder import idf_txt

from eppy.iddcurrent import iddcurrent
from geomeppy.eppy_patches import IDF
from six import StringIO


idf_txt = """
Version, 8.5;
"""


class TestAddShadingBlock():

    def setup(self):
        iddfhandle = StringIO(iddcurrent.iddtxt)
        if IDF.getiddname() == None:
            IDF.setiddname(iddfhandle)
        
        self.idf = IDF(StringIO(idf_txt))

    def test_add_shading_block_smoke_test(self):
        idf = self.idf
        name = "test"
        height = 7.5
        coordinates = [
            (87.25,24.0),(91.7,25.75),(90.05,30.25),
            (89.55,31.55),(89.15,31.35),(85.1,29.8),
            (86.1,27.2),(84.6,26.65),(85.8,23.5),
            (87.25,24.0)]
        idf.add_shading_block(name, coordinates, height)
        
        
