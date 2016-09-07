# Copyright (c) 2016 Jamie Bull
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================
"""pytest for builder.py"""
#from six import StringIO

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from geomeppy.builder import Block
from geomeppy.eppy_patches import IDF

from eppy.iddcurrent import iddcurrent
from six import StringIO


idf_txt = """
Version, 8.5;
"""

class TestAddBlock():

    def setup(self):
        iddfhandle = StringIO(iddcurrent.iddtxt)
        if IDF.getiddname() == None:
            IDF.setiddname(iddfhandle)
        
        self.idf = IDF(StringIO(idf_txt))
            
    def test_add_block(self):
        idf = self.idf
        name = "test"
        height = 7.5
        num_stories = 4
        below_ground_stories = 1
        below_ground_storey_height = 2.5
        coordinates = [
            (87.25,24.0),(91.7,25.75),(90.05,30.25),
            (89.55,31.55),(89.15,31.35),(85.1,29.8),
            (86.1,27.2),(84.6,26.65),(85.8,23.5),
            (87.25,24.0)]
        idf.add_block(name, coordinates, height, num_stories,
                  below_ground_stories, below_ground_storey_height)
        
def test_block():
    name = "test"
    height = 7.5
    num_stories = 4
    below_ground_stories = 1
    below_ground_storey_height = 2.5
    coordinates = [
        (524287.25,181424.0),(524291.7,181425.75),(524290.05,181430.25),
        (524289.55,181431.55),(524289.15,181431.35),(524285.1,181429.8),
        (524286.1,181427.2),(524284.6,181426.65),(524285.8,181423.5),
        (524287.25,181424.0)]
    
    block = Block(name, coordinates, height, num_stories,
                  below_ground_stories, below_ground_storey_height)
    # number of surfaces
    assert len(block.surfaces['roofs']) == block.num_stories
    assert all(r == [None] for r in block.surfaces['roofs'][:-1])
    assert len(block.surfaces['walls']) == block.num_stories
    assert len(block.surfaces['ceilings']) == block.num_stories
    assert len(block.surfaces['floors']) == block.num_stories
    # heights
    assert block.surfaces['floors'][0][0].vertices[0].z == (
        -below_ground_storey_height * below_ground_stories)
    assert block.surfaces['roofs'][-1][0].vertices[0].z == height
    # storey_nos
    assert block.stories[0]['storey_no'] == -below_ground_stories
    assert block.stories[-1]['storey_no'] == (
        num_stories - below_ground_stories - 1)
    
    
