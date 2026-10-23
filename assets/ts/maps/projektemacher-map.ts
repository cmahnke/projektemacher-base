import { Map as OlMap, View } from 'ol';
import { ViewOptions } from 'ol/View';
import Attribution from 'ol/control/Attribution.js';
import GeoJSON from 'ol/format/GeoJSON.js';
import VectorSource from 'ol/source/Vector.js';
import VectorLayer from 'ol/layer/Vector.js';
import VectorTileLayer from 'ol/layer/VectorTile.js';
import VectorTileSource from 'ol/source/VectorTile.js';
import TileLayer from 'ol/layer/Tile.js';
import { TileDebug } from 'ol/source.js';
import { Cluster } from 'ol/source.js';
import MVT from 'ol/format/MVT';
import { boundingExtent, getCenter, Extent, createEmpty, extend, getWidth, getHeight } from 'ol/extent';
import { fromLonLat } from 'ol/proj';
import { apply, applyStyle } from 'ol-mapbox-style';
import { debugStyle, setupDefaultStyle } from './projektemacher-default-map-style';
import { updateStyle } from './styles';
import {
  toolTips,
  defaultPadding,
  getLang,
  addOverlay,
  createOverlay,
  mergeFeatures,
  absUrl,
  bboxExtent,
  loadOrParse,
  setupMarker,
  featurePopUp,
  setControlAriaLabels,
  type Lang,
} from './base-map';
import { center as turf_center } from '@turf/turf';
import type Interaction from 'ol/interaction/Interaction';
import { Control, FullScreen, Zoom, MousePosition } from 'ol/control';
import Feature from 'ol/Feature';
import type { FeatureLike } from 'ol/Feature';
import Geometry from 'ol/geom/Geometry';
import BaseLayer from 'ol/layer/Base';
import { Coordinate } from 'ol/coordinate';
import { StyleLike } from 'ol/style/Style';
import { Circle as CircleStyle, Fill, Icon, Stroke, Style, Text } from 'ol/style.js';
import type { Options as IconOptions } from 'ol/style/Icon';

const defaultSprites = '/map-styles/sprite';
const defaultFonts = '/css/fonts/{font-family}.css';
const defaultAttribution =
  '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap contributors</a>';

export interface GeoJSONFeatureCollection {
  type: string;
  features: unknown[];
  [key: string]: unknown;
}

interface ClusterMarkerOptions extends IconOptions {
  clusterScaleFactor?: number;
  clusterScaleMax?: number;
}

const clusterScaleFactorDefault = 0.25;
const clusterScaleMaxDefault = 3;

type BBoxInput = number[] | number[][] | string;

function geoJSONVectorSource(
  geojson: GeoJSONFeatureCollection
): VectorSource<Feature<Geometry>> {
  const parser = new GeoJSON({ dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857' });

  const vectorSource = new VectorSource({
    features: parser.readFeatures(geojson),
  });
  return vectorSource;
}

interface MapMetadata {
  bounds: BBoxInput;
  [key: string]: unknown;
}

export async function getMapMetadata(url: string): Promise<MapMetadata> {
  const metadataFile = 'metadata.json';
  if (url.includes('{')) {
    url = url.substring(0, url.indexOf('{'));
  }
  if (!url.endsWith(metadataFile) && !url.endsWith('/')) {
    url += '/' + metadataFile;
  } else if (!url.endsWith(metadataFile)) {
    url += metadataFile;
  }
  url = absUrl(url);
  return loadOrParse(url) as Promise<MapMetadata>;
}

interface MapboxStyleLike {
  version?: number;
  sources?: {
    vector_layer_?: unknown;
    [key: string]: unknown;
  };
  [key: string]: unknown;
}

function checkMapboxStyle(style: MapboxStyleLike): boolean {
  if (
    style.version !== undefined &&
    style.sources !== undefined &&
    style.sources.vector_layer_ !== undefined
  ) {
    return true;
  }
  return false;
}

interface ProjektemacherViewOptions extends ViewOptions {
  smoothResolutionConstraint?: boolean;
  smoothExtentConstraint?: boolean;
}

interface MapControlsConfig {
  controls?: Control[];
  interactions?: Interaction[];
}

export async function projektemacherMap(
  elem: string | HTMLElement,
  geojson?: string | GeoJSONFeatureCollection,
  source?: string,
  style?: string | object,
  bbox?: string | BBoxInput,
  center?: string | Coordinate,
  initialZoom?: number,
  minZoom?: number,
  maxZoom?: number,
  cluster?: boolean,
  disabled?: boolean,
  popup?: boolean,
  background?: string,
  debug?: boolean,
  marker?: string | object | StyleLike,
  font?: string,
  attribution?: string
): Promise<OlMap> {
  const geojsonObj = (await loadOrParse(geojson as string)) as GeoJSONFeatureCollection;
  let styleObj: any;
  let bboxObj: number[][] | undefined;
  let centerObj: Coordinate | undefined;
  let markerObj: object | StyleLike | undefined;

  const lang = getLang();
  const langKey = (lang in toolTips ? lang : 'en') as Lang;
  source = absUrl(source as string);

  if (bbox !== undefined) {
    const rawBbox = (await loadOrParse(bbox as string)) as number[] | number[][];
    if ((rawBbox as number[]).length === 4) {
      const flat = rawBbox as number[];
      bboxObj = [
        [flat[0], flat[1]],
        [flat[2], flat[3]],
      ];
    } else {
      bboxObj = rawBbox as number[][];
    }
  }

  if (center !== undefined) {
    centerObj = (await loadOrParse(center as string)) as Coordinate;
  } else {
    if (geojsonObj !== undefined && geojsonObj.features.length !== 0) {
      centerObj = turf_center(geojsonObj as any).geometry.coordinates as Coordinate;
    } else if (bboxObj !== undefined && bboxObj.length !== 0) {
      centerObj = getCenter(boundingExtent(bboxObj));
    } else {
      console.warn("Can't create center from features or bbox");
      centerObj = [0, 0];
    }
  }

  if (marker !== undefined && !(typeof marker === 'function')) {
    markerObj = (await loadOrParse(marker as string)) as object;
  } else if (marker !== undefined && typeof marker === 'function') {
    markerObj = marker as unknown as StyleLike;
  }

  if (maxZoom === undefined) {
    maxZoom = 16;
  }
  if (bbox === undefined || bboxObj === undefined || Object.keys(bboxObj).length === 0) {
    bboxObj = [
      [-180, -85.051129],
      [180, 85.051129],
    ];
  }

  // Disabled should also stop popups
  if (disabled === undefined) {
    disabled = false;
  }
  if (popup === undefined && !disabled) {
    popup = true;
  }

  if (debug === undefined) {
    debug = false;
  }

  if (attribution === undefined) {
    attribution = defaultAttribution;
  }

  if (initialZoom === undefined) {
    initialZoom = 0;
  }

  const viewConfig: ProjektemacherViewOptions = {
    center: fromLonLat(centerObj as Coordinate),
    projection: 'EPSG:3857',
    zoom: initialZoom,
  };

  if (minZoom !== undefined) {
    viewConfig.minZoom = minZoom;
    viewConfig.smoothResolutionConstraint = false;
  }
  if (maxZoom !== undefined) {
    viewConfig.maxZoom = maxZoom;
    viewConfig.smoothResolutionConstraint = false;
  }
  if (bboxObj !== undefined) {
    viewConfig.smoothExtentConstraint = false;
    viewConfig.extent = bboxExtent(bboxObj);
  }

  if (style !== undefined) {
    styleObj = await loadOrParse(style as string);
    styleObj = updateStyle(
      styleObj,
      source,
      initialZoom,
      undefined,
      undefined,
      bboxObj,
      centerObj as [number, number],
      background,
      absUrl(defaultSprites),
      defaultFonts,
      font,
      attribution
    );
  } else {
    styleObj = setupDefaultStyle(source, initialZoom, minZoom, maxZoom, bboxObj, centerObj, background);
  }

  const view = new View(viewConfig);
  const layers: BaseLayer[] = [];
  const geojsonSource = geoJSONVectorSource(geojsonObj);

  const controls: MapControlsConfig = {
    controls: [
      new Attribution({
        collapsible: false,
      }),
    ],
  };
  if (disabled) {
    controls.interactions = [];
  } else {
    controls.controls = [
      new Zoom({
        zoomInTipLabel: toolTips[langKey]['zoomIn'],
        zoomOutTipLabel: toolTips[langKey]['zoomOut'],
      }),
      new FullScreen({ tipLabel: toolTips[langKey]['fullscreen'] }),
      new Attribution({ collapsible: true }),
    ];
  }

  if (debug) {
    console.log(
      `Adding map on ${elem}, with '${JSON.stringify(geojsonObj)}', from '${source}', style ${style}: options cluster '${cluster}', marker '${JSON.stringify(
        markerObj
      )}', bbox '${bbox}', center '${center}', initialZoom '${initialZoom}', min zoom '${minZoom}', max zoom '${maxZoom}', popup '${popup}', disabled '${disabled}'  - debug '${debug}'`
    );
    controls.controls!.push(new MousePosition());
    console.log('Active style', styleObj);
    const debugLayer = new TileLayer({
      source: new TileDebug({ zDirection: 1, template: '{z}/{x}/{y}' } as any),
    });
    layers.push(debugLayer);
  }

  let geojsonLayer: VectorLayer;
  if (cluster === true) {
    const clusterSource = new Cluster({
      distance: 25,
      source: geojsonSource,
    });

    const outerCircleFill = new Fill({ color: 'rgba(255, 255, 255, 0.7)' });
    const innerCircleFill = new Fill({ color: 'rgba(255, 255, 255, 0.3)' });
    const innerCircle = new CircleStyle({
      radius: 8,
      fill: innerCircleFill,
      stroke: new Stroke({ color: 'rgba(51, 153, 204, 0.7)', width: 1.25 }),
    });
    const outerCircle = new CircleStyle({
      radius: 15,
      fill: outerCircleFill,
      stroke: new Stroke({ color: 'rgba(51, 153, 204, 0.3)', width: 1.25 }),
    });
    const textFill = new Fill({ color: '#fff' });
    const textStroke = new Stroke({ color: 'rgba(0, 0, 0, 0.6)', width: 3 });

    const markerOptions: ClusterMarkerOptions | undefined =
      markerObj !== undefined && !(typeof markerObj === 'function')
        ? (markerObj as ClusterMarkerOptions)
        : undefined;
    const clusterScaleFactor = markerOptions?.clusterScaleFactor ?? clusterScaleFactorDefault;
    const clusterScaleMax = markerOptions?.clusterScaleMax ?? clusterScaleMaxDefault;
    const clusterIcons = new Map<number, Icon>();

    const getMarkerIcon = (size: number): Icon | undefined => {
      if (markerOptions === undefined) {
        return undefined;
      }
      const scaleOption = markerOptions.scale ?? 1;
      const baseScale = typeof scaleOption === 'number' ? scaleOption : 1;
      const growthFactor =
        size > 1 ? Math.min(1 + clusterScaleFactor * Math.log2(size), clusterScaleMax) : 1;
      const scale = baseScale * growthFactor;
      let icon = clusterIcons.get(scale);
      if (icon === undefined) {
        const iconOptions: Record<string, unknown> = { ...markerOptions };
        delete iconOptions.clusterScaleFactor;
        delete iconOptions.clusterScaleMax;
        iconOptions.scale = scale;
        icon = new Icon(iconOptions as unknown as IconOptions);
        clusterIcons.set(scale, icon);
      }
      return icon;
    };

    const clusterMemberStyle = (clusterMember: Feature<Geometry>): Style => {
      const memberIcon = getMarkerIcon(1);
      if (memberIcon !== undefined) {
        return new Style({
          geometry: clusterMember.getGeometry(),
          image: memberIcon,
        });
      }
      return new Style({
        geometry: clusterMember.getGeometry(),
        image: innerCircle,
      });
    };

    const clusterStyle = (feature: FeatureLike): Style | Style[] => {
      const size = (feature.get('features') as Feature<Geometry>[]).length;
      if (size > 1) {
        const clusterIcon = getMarkerIcon(size);
        if (clusterIcon !== undefined) {
          const growthFactor = Math.min(1 + clusterScaleFactor * Math.log2(size), clusterScaleMax);
          return [
            new Style({ image: clusterIcon }),
            new Style({
              image: new CircleStyle({
                radius: 15 * growthFactor,
                displacement: [-10 * growthFactor, 25 * growthFactor],
                fill: new Fill({ color: 'rgba(255, 255, 255, 0.7)' }),
              }),
              text: new Text({
                text: size.toString(),
                fill: textFill,
                stroke: textStroke,
                offsetY: -25 * growthFactor,
                offsetX: -10 * growthFactor,
              }),
            }),
          ];
        }
        return [
          new Style({ image: outerCircle }),
          new Style({
            image: innerCircle,
            text: new Text({
              text: size.toString(),
              fill: textFill,
              stroke: textStroke,
            }),
          }),
        ];
      }
      const originalFeature = (feature.get('features') as Feature<Geometry>[])[0];
      return clusterMemberStyle(originalFeature);
    };

    geojsonLayer = new VectorLayer({
      source: clusterSource,
      style: clusterStyle,
    });
  } else {
    geojsonLayer = new VectorLayer({
      source: geojsonSource,
    });
    if (markerObj !== undefined) {
      if (!(typeof marker === 'function')) {
        setupMarker(markerObj as any, geojsonLayer as any);
      } else {
        geojsonLayer.setStyle(markerObj as StyleLike);
      }
    }
  }
  layers.push(geojsonLayer);

  const map = new OlMap({
    //layers: layers,
    target: elem,
    view: view,
    ...controls,
  });
  setControlAriaLabels(map, [
    ['.ol-zoom-in', toolTips[langKey]['zoomIn']],
    ['.ol-zoom-out', toolTips[langKey]['zoomOut']],
    ['.ol-full-screen button', toolTips[langKey]['fullscreen']],
  ]);

  const mapMetadata = await getMapMetadata(source);

  let vectorTileLayer: VectorTileLayer | undefined;
  if (styleObj !== undefined) {
    apply(map, styleObj);
  } else {
    const bounds = bboxExtent(mapMetadata.bounds as BBoxInput);
    vectorTileLayer = new VectorTileLayer({
      // NOTE: "extend" is not a valid VectorTileLayer option (likely meant "extent"); preserved from original.
      extend: bounds,
      maxZoom: maxZoom,
      source: new VectorTileSource({
        format: new MVT(),
        url: source,
        extent: bounds,
      }),
      style: debugStyle,
    } as any);
    applyStyle(vectorTileLayer, styleObj);

    map.addLayer(vectorTileLayer);
  }

  layers.forEach((layer) => {
    map.addLayer(layer);
  });

  if (geojson !== undefined) {
    if (!disabled && popup) {
      if (cluster === true) {
        const { overlay, content } = createOverlay(map);
        map.on('click', (event) => {
          geojsonLayer.getFeatures(event.pixel).then((features) => {
            if (features.length === 0) {
              return;
            }
            const clusterMembers = features[0].get('features') as Feature<Geometry>[];
            if (clusterMembers.length > 1) {
              const extent = createEmpty();
              clusterMembers.forEach((feature) =>
                extend(extent, feature.getGeometry()!.getExtent())
              );
              const view = map.getView();
              const resolution = map.getView().getResolution() as number;
              if (
                view.getZoom() === view.getMaxZoom() ||
                (getWidth(extent) < resolution && getHeight(extent) < resolution)
              ) {
                featurePopUp(mergeFeatures(clusterMembers), overlay, content);
              } else {
                view.fit(extent, { duration: 500, padding: [50, 50, 50, 50] });
              }
            } else if (clusterMembers.length === 1) {
              featurePopUp(clusterMembers[0], overlay, content);
            }
          });
        });
      } else {
        addOverlay(map, { hitTolerance: 10 });
      }
    }

    if (geojsonObj.features.length) {
      const extent = geojsonLayer.getSource()?.getExtent() as Extent;
      map.getView().fit(extent, { size: map.getSize(), padding: defaultPadding });
    }
  }

  map.updateSize();
  return map;
}

//window.projektemacherMap = projektemacherMap;
