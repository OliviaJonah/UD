# -*- coding: utf-8 -*-
"""
Created on Thu Jan 05 10:00:10 2017

@author: Victor
"""

"""
Parse the OSM file and count the numbers of unique tag
"""

import xml.etree.cElementTree as ET
import pprint


OSMFILE = "freetown.osm"

def count_tags(filename):
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag in tags: 
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
    return tags
    
pprint.pprint(count_tags(OSMFILE))