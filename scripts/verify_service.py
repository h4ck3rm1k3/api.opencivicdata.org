#!/usr/bin/env python
u'''
test client for boundries
reads a file that contains lat, lon and a block list with comma sep
then it verifies that the blocks are in the response from the server
see resources/test_points.csv
'''

import urllib2
import json
import sys


URL_BASE = "http://localhost:8000"

def query_bs(lat, lon):
    u'''
    query a boundry for a point
    '''
    path = "/boundaries/?contains={lat},{lon}".format(**locals())
    url = "%s%s" % (URL_BASE, path)
    print ("[ fetch ] %s" % (url))
    return json.load(urllib2.urlopen(url))

# mock response:
#    return { 'objects' : [{ 'external_id' : 'sldu-13-1638' } ]}


def entries(file_path):
    u'''
    create a list of lat and lon with a set of blocks from a data file
    '''
    with open(file_path, 'r') as file_descriptor:
        for line in file_descriptor:
            lat, lon, blocks = line.split(",", 2)
            yield {"lat": lat, "lon": lon,
                   "blocks": [x.strip() for x in blocks.split(",")]}

def main():
    u'''
    main routine,
    '''
    for entry in entries(sys.argv[1]):
        obj = query_bs(entry['lat'], entry['lon'])
        response = list( x['external_id'] for x in obj['objects'])
        for expected in entry['blocks']:
            try:
                print ("expected %s is in %s" % (expected, response))
                assert expected in response
            except AssertionError:
                print ("expected %s not in %s" % (expected, response))
                raise
        print ("[ ok ] - %s / %s" % (entry['lat'], entry['lon']))


if __name__ == "__main__":
    main()
