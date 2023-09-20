#!/usr/bin/env python
# Inspired by https://gist.github.com/JamesChevalier/b03b7423bf330f959076

import argparse, pathlib, json

parser = argparse.ArgumentParser(description='Create bounding box')
parser.add_argument('--file', '-f', type=pathlib.Path, help='GeoJSON file to process', required=True)
parser.add_argument('--margin', '-m', type=int, help='margin in percent')

args = parser.parse_args()
geojson = json.load(args.file.open())
bounds = {}

def margin_bounds(bounds, margin):
    bounds['xMin'] = bounds['xMin'] - (bounds['xMin'] / 100) * margin
    bounds['yMin'] = bounds['yMin'] - (bounds['yMin'] / 100) * margin
    bounds['xMax'] = bounds['xMax'] + (bounds['xMax'] / 100) * margin
    bounds['yMax'] = bounds['yMax'] + (bounds['yMax'] / 100) * margin
    return bounds

def updade_bounds(bounds, lon, lat):
    bounds['xMin'] = lon if not 'xMin' in bounds else bounds['xMin']
    bounds['xMax'] = lon if not 'xMax' in bounds else bounds['xMax']
    bounds['yMin'] = lat if not 'yMin' in bounds else bounds['yMin']
    bounds['yMax'] = lat if not 'yMax' in bounds else bounds['yMax']

    bounds['xMin'] = bounds['xMin'] if bounds['xMin'] < lon else lon;
    bounds['xMax'] = bounds['xMax'] if bounds['xMax'] > lon else lon;
    bounds['yMin'] = bounds['yMin'] if bounds['yMin'] < lat else lat;
    bounds['yMax'] = bounds['yMax'] if bounds['yMax'] > lat else lat;
    return bounds

for i in range(len(geojson['features'])):
    coordinates = geojson['features'][i]['geometry']['coordinates']
    if not any(isinstance(c, list) for c in coordinates):
        lon = coordinates[0];
        lat = coordinates[1];
        bounds = updade_bounds(bounds, lon, lat)
    else:
        if (len(coordinates) == 1):
            for j in range(len(coordinates[0])):
                lon = coordinates[0][j][0];
                lat = coordinates[0][j][1];
                bounds = updade_bounds(bounds, lon, lat)
        else:
            for j in range(len(coordinates)):
                for k in range(len(coordinates[j][0])):
                    lon = coordinates[j][0][k][0];
                    lat = coordinates[j][0][k][1];
                    bounds = updade_bounds(bounds, lon, lat)

if (args.margin):
    bounds = margin_bounds(bounds, args.margin)

print(".env Format for OpenMaptiles {:0.4f},{:0.4f},{:0.4f},{:0.4f}".format(bounds['xMin'], bounds['yMin'], bounds['xMax'], bounds['yMax']))
