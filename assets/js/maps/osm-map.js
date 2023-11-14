import Map from 'ol/Map';
import {Tile as TileLayer, Vector as VectorLayer} from 'ol/layer';
import View from 'ol/View';
import GeoJSON from 'ol/format/GeoJSON';
import Overlay from 'ol/Overlay';
import {OSM, XYZ, Vector as VectorSource} from 'ol/source';
import {Control, FullScreen, Zoom} from 'ol/control';

var layers = {};

layers['wiki'] = new TileLayer({
    source: new XYZ({
        attributions: [
            OSM.ATTRIBUTION, 'Map data &copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap contributors</a>'],
        url: 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png?lang=en'
    })
});

layers['osm'] = new TileLayer({source: new OSM()});

export function initMap(element, url, source) {
    // Languages
    var lang = 'en';
    if (document.documentElement.lang !== undefined) {
        /* TODO: Check for lang locale combinations here: "de-de" instead of "de" will currently break this. */
        lang = document.documentElement.lang;
    }
    var toolTips = { 'de': {'zoomIn': 'Vergrößern', 'zoomOut': 'Verkleinern', 'fullscreen': 'Vollbildansicht', 'rotate': 'Rotation zurücksetzen', 'rotateLeft': '90° nach links drehen', 'rotateRight': '90° nach rechst drehen'},
                     'en': {'zoomIn': 'Zoom in', 'zoomOut': 'Zoom out', 'fullscreen': 'Toggle full-screen', 'rotate': 'Reset rotation', 'rotateLeft': 'Rotate 90° left', 'rotateRight': 'Rotate 90° right'}};

    var padding = [30, 30, 30, 30];

    // Popup elements
    var container = document.getElementById(element + '-popup');
    var content = document.getElementById(element + '-popup-content');
    var closer = document.getElementById(element + '-popup-closer');

    // Base layer
    var baseLayer;
    if (source !== undefined && source !== '') {
        if (source in layers) {
            baseLayer = layers[source];
        } else {
            baseLayer = new TileLayer({source: new XYZ({url: source})});
        }
    } else {
        baseLayer = layers['osm'];
    }

    var map = new Map({
            controls: [new Zoom({zoomInTipLabel: toolTips[lang]['zoomIn'], zoomOutTipLabel: toolTips[lang]['zoomOut']}),
                       new FullScreen({tipLabel: toolTips[lang]['fullscreen']})],
            layers: [baseLayer],
            target: element,
        }),
    overlay = new Overlay({
        element: container,
        autoPan: true,
        autoPanAnimation: {
            duration: 250
        }
    });

    map.addOverlay(overlay);
    map.on('click', function (event) {
        var feature = map.forEachFeatureAtPixel(event.pixel,
            function(feature, layer) {
                return feature;
            });

        if (feature) {
            var geometry = feature.getGeometry();
            var coord = geometry.getCoordinates();
            var popup = '<h1>' + feature.get('name') + '</h1>';
            popup += feature.get('popupContent');
            content.innerHTML = popup;
            overlay.setPosition(coord);
        }

    });
    closer.onclick = function() {
        overlay.setPosition(undefined);
        closer.blur();
        return false;
    };

    fetch(url)
        .then(function(response) {
            response
                .json()
                .then(function(geojson) {
                    // See https://openlayers.org/en/latest/examples/geojson.html

                    // See https://gis.stackexchange.com/questions/373285/geojson-doesnt-render-on-map-in-openlayers-project
                    var parser = new GeoJSON({dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});

                    var vectorSource = new VectorSource({
                        features: parser.readFeatures(geojson)
                    });

                    var vectorLayer = new VectorLayer({
                        source: vectorSource
                    });
                    vectorLayer.reportError = true;
                    map.addLayer(vectorLayer);

                    map.setView(
                        new View({
                            center: [0, 0],
                            zoom: 2
                        })
                    );

                    map.getView().fit(vectorSource.getExtent(),
                        {size: map.getSize(), padding: padding}
                    );

                })
                .catch(function(body) {
                    console.log('Could not read GeoJSON. ' + body);
                });
        })
        .catch(function() {
            console.log('Could not read data from URL.');
        });
    return map;
}
