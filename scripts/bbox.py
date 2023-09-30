#!/usr/bin/env python
# Inspired by https://gist.github.com/JamesChevalier/b03b7423bf330f959076

import argparse, pathlib, json
from math import pow, sqrt
from geojson.utils import coords
from shapely.geometry import LineString
import pyproj

# See https://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Python_Parsing
def parse_poly(lines):
    """ Parse an Osmosis polygon filter file.

        Accept a sequence of lines from a polygon file, return a shapely.geometry.MultiPolygon object.

        http://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format
    """
    in_ring = False
    coords = []

    for (index, line) in enumerate(lines):
        if index == 0:
            # first line is junk.
            continue

        elif index == 1:
            # second line is the first polygon ring.
            coords.append([[], []])
            ring = coords[-1][0]
            in_ring = True

        elif in_ring and line.strip() == 'END':
            # we are at the end of a ring, perhaps with more to come.
            in_ring = False

        elif in_ring:
            # we are in a ring and picking up new coordinates.
            ring.append(list(map(float, line.split())))

        elif not in_ring and line.strip() == 'END':
            # we are at the end of the whole polygon.
            break

        elif not in_ring and line.startswith('!'):
            # we are at the start of a polygon part hole.
            coords[-1][1].append([])
            ring = coords[-1][1][-1]
            in_ring = True

        elif not in_ring:
            # we are at the start of a polygon part.
            coords.append([[], []])
            ring = coords[-1][0]
            in_ring = True

    return MultiPolygon(coords)

def load_poly(file):
    with open(file) as f:
        contents = f.readlines()
    return parse_poly(contents)

def get_bbox(geometry):
    return LineString(coords(geometry)).bounds

def margin(bbox, meter):
    dist = sqrt(meter ** 2 + meter ** 2)
    # See https://stackoverflow.com/a/46098551
    geod = pyproj.Geod(ellps='WGS84')
    tl = geod.fwd(bbox[0], bbox[1], 315, dist)
    br = geod.fwd(bbox[2], bbox[3], 135, dist)
    return (tl[0], tl[1], br[0], br[1])

parser = argparse.ArgumentParser(description='Create bounding box')
input = parser.add_mutually_exclusive_group(required=True)
input.add_argument('--file', '-f', type=pathlib.Path, help='GeoJSON file to process')
input.add_argument('--poly', '-p', type=pathlib.Path, help='Poly file to process')
parser.add_argument('--margin', '-m', type=int, help='margin in meter')
parser.add_argument('--json', '-j', action='store_true', default=False, help='Output json')

args = parser.parse_args()
if args.file:
    gjson = json.load(args.file.open())
    bounds = get_bbox(gjson)
elif args.poly:
    poly = load_poly(args.poly)
    bounds = LineString(coords(poly)).bounds

if args.margin:
    bounds = margin(bounds, args.margin)

if args.json:
    print(json.dumps(bounds))
else:
    print(".env Format for OpenMaptiles {:0.4f},{:0.4f},{:0.4f},{:0.4f}".format(*bounds))
