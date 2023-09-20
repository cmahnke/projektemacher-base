#!/usr/bin/env python
# Inspired by https://gist.github.com/JamesChevalier/b03b7423bf330f959076

import argparse, pathlib, json
from math import pow, sqrt
from geojson.utils import coords
from shapely.geometry import LineString
import pyproj

parser = argparse.ArgumentParser(description='Create bounding box')
parser.add_argument('--file', '-f', type=pathlib.Path, help='GeoJSON file to process', required=True)
parser.add_argument('--margin', '-m', type=int, help='margin in meter')
parser.add_argument('--json', '-j', action='store_true', default=False, help='Output json')

args = parser.parse_args()
gjson = json.load(args.file.open())
bounds = {}

def get_bbox(geometry):
    return LineString(coords(geometry)).bounds

def margin(bbox, meter):
    dist = sqrt(meter ** 2 + meter ** 2)
    # See https://stackoverflow.com/a/46098551
    geod = pyproj.Geod(ellps='WGS84')
    tl = geod.fwd(bbox[0], bbox[1], 315, dist)
    br = geod.fwd(bbox[2], bbox[3], 135, dist)
    return (tl[0], tl[1], br[0], br[1])

bounds = get_bbox(gjson)

if args.margin:
    bounds = margin(bounds, args.margin)

if args.json:
    print(json.dumps(bounds))
else:
    print(".env Format for OpenMaptiles {:0.4f},{:0.4f},{:0.4f},{:0.4f}".format(*bounds))
