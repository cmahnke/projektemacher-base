import {Map, View} from 'ol';
import GeoJSON from 'ol/format/GeoJSON.js';
import VectorLayer from 'ol/layer/Vector.js';
import VectorSource from 'ol/source/Vector.js';
import {fromLonLat} from 'ol/proj.js';
import 'ol/ol.css';
import apply from 'ol-mapbox-style';

const prefix = 'https://static.projektemacher.org/maps/central-europe/tiles/'
const layer_url = prefix + '{z}/{x}/{y}.pbf';

export function mapViewer (elem, style, geoJson, source, bbox, center, initialZoom, maxZoom) {

  if (source !== undefined) {
    style.sources.vector_layer_.tiles = [layer_url];
  }
  if (bbox === undefined) {
    bbox = [];
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

  const map = new Map({
    target: elem,
    view: new View({
      center: fromLonLat(center),
      projection: 'EPSG:3857',
      zoom: initialZoom,
      maxZoom: maxZoom
    })
  });
  apply(map, style);

  if (geoJson !== undefined && geoJson !== [] && geoJson !== '') {
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
