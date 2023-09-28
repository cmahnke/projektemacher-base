import {Map, View} from 'ol';
import GeoJSON from 'ol/format/GeoJSON.js';
import VectorLayer from 'ol/layer/Vector.js';
import VectorSource from 'ol/source/Vector.js';
import {fromLonLat} from 'ol/proj.js';
import {boundingExtent} from 'ol/extent';
import apply from 'ol-mapbox-style';

import 'ol/ol.css';

const prefix = 'https://static.projektemacher.org/maps/central-europe/tiles/'
const layer_url = prefix + '{z}/{x}/{y}.pbf';

function checkMapboxStyle(style) {
  if (style.version !== undefined && style.sources !== undefined && style.sources.vector_layer_ !== undefined) {
    return true;
  }
  return false;
}

export function mapViewer (elem, style, geoJson, source, bbox, center, initialZoom, maxZoom) {

  if (source !== undefined || source != '') {
    source = layer_url;
  }
  if (bbox === undefined || bbox == [] || bbox == '') {
    bbox = [[-180, -85.051129] ,[180, 85.051129]];
  }
  if (center === undefined) {
    center = [9.93, 51.55];
  }
  if (initialZoom === undefined) {
    initialZoom = 6;
  }
  if (maxZoom === undefined) {
    maxZoom = 15;
  }

  var view;

  if (!checkMapboxStyle(style)) {
    view = new View({
      center: fromLonLat(center),
      projection: 'EPSG:3857',
      zoom: initialZoom,
      maxZoom: maxZoom,
      extent: boundingExtent(bbox)
    });
  } else {
    style.sources.vector_layer_.tiles = [layer_url];
    style.sources.vector_layer_.maxzoom = maxZoom;
    style.sources.vector_layer_.minzoom = 0;
    style.sources.vector_layer_.bounds = bbox.flat();
    style.center = center;
    style.zoom = initialZoom;
    view = new View({
      center: fromLonLat(center),
      projection: 'EPSG:3857',
      zoom: initialZoom,
      maxZoom: maxZoom,
    });
  }

  console.log(`Creating Map on '${elem}' from '${source}' with ${bbox}, centered at '${center}', initial ${initialZoom}, maximal ${maxZoom} Zoom`)

  const map = new Map({
    target: elem,
    view: view
  });
  apply(map, style);

  if (geoJson !== undefined && geoJson != [] && geoJson != '') {
    if (!Array.isArray(geoJson)) {
      geoJson = [geoJson];
    }
    geoJson.forEach(function(g) {
      const geoJsonLayer = new VectorLayer({
        source: new VectorSource({
          url: g,
          format: new GeoJSON(),
        }),
      });
      map.addLayer(geoJsonLayer);
    });

  }
  return map;
}
