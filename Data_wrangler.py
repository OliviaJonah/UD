#import libaries
import os
import collections
import pprint
import xml.etree.cElementTree as ET
import re
import codecs
import csv
import cerberus
import copy
import schema
#!/usr/bin/env python
# -*- coding: utf-8 -*-

OSM_FILE = "freetown.osm"
SAMPLE_FILE = "freetown_sample.osm"

k = 30 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/
    inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')
DATADIR = "c:/udacity"
DATAFILE = "freetown.osm"

F_DATA = os.path.join(DATADIR, DATAFILE)
def count_tags(filename):
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag in tags:
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
    return tags

f_tags = count_tags(F_DATA)
pprint.pprint(f_tags)
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        if re.match(lower, element.attrib['k']):
            keys["lower"] += 1
        elif re.match(lower_colon, element.attrib['k']):
            keys["lower_colon"] += 1
        elif re.search(problemchars, element.attrib['k']):
            keys["problemchars"] += 1
        else:
            keys['other'] += 1
    return keys


def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

f_all_keys = process_map(F_DATA)
print f_all_keys
def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if 'user' in element.attrib:
            users.add(element.attrib['user'])
            
    return users

f_users = process_map(F_DATA)
pprint.pprint(len(f_users))
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Cove", "Alley", "Park", "Way", "Walk" "Circle", "Highway", 
            "Plaza", "Path", "Center", "Mission"]

mapping = { "Ave": "Avenue",
            "Ave.": "Avenue",
            "avenue": "Avenue",
            "ave": "Avenue",
            "Blvd": "Boulevard",
            "Blvd.": "Boulevard",
            "Blvd,": "Boulevard",
            "Boulavard": "Boulevard",
            "Boulvard": "Boulevard",
            "Ct": "Court",
            "Dr": "Drive",
            "Dr.": "Drive",
            "E": "East",
            "Hwy": "Highway",
            "Ln": "Lane",
            "Ln.": "Lane",
            "Pl": "Place",
            "Plz": "Plaza",
            "Rd": "Road",
            "Rd.": "Road",
            "St": "Street",
            "St.": "Street",
            "st": "Street",
            "street": "Street",
            "square": "Square",
            "parkway": "Parkway"
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

            
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = collections.defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping, regex):
    m = regex.search(name)
    if m:
        st_type = m.group()
        if st_type in mapping:
            name = re.sub(regex, mapping[st_type], name)
    return name
sf_st_types = audit(F_DATA)
pprint.pprint(dict(sf_st_types))
sf_st_types = audit(F_DATA)
pprint.pprint(dict(sf_st_types))
for street_type, ways in sf_st_types.iteritems():
    for name in ways:
        better_name = update_name(name, mapping, street_type_re)
        print name, "=>", better_name
def audit_zipcode(invalid_zipcodes, zipcode):
    twoDigits = zipcode[0:2]
    
    if twoDigits != 94 or not twoDigits.isdigit():
        invalid_zipcodes[twoDigits].add(zipcode)
        
def is_zipcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

def audit_zip(osmfile):
    osm_file = open(osmfile, "r")
    invalid_zipcodes = collections.defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_zipcode(tag):
                    audit_zipcode(invalid_zipcodes,tag.attrib['v'])

    return invalid_zipcodes

sf_zipcode = audit_zip(F_DATA)
pprint.pprint(dict(sf_zipcode))
def update_zip(zipcode):
    zipChar = re.findall('[a-zA-Z]*', zipcode)
    if zipChar:
        zipChar = zipChar[0]
    zipChar.strip()
    if zipChar == "CA":
        updateZip = re.findall(r'\d+', zipcode)
        if updateZip:
            return (re.findall(r'\d+', zipcode))[0]
    else:
        return (re.findall(r'\d+', zipcode))[0]


for street_type, ways in sf_zipcode.iteritems():
    for name in ways:
        better_name = update_zip(name)
        print name, "=>", better_name
