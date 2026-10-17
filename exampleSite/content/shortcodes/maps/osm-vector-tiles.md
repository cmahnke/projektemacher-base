---
title: maps/osm-vector-tiles
displayinlist: false
metaPage: true
---

# maps/osm-vector-tiles

Renders an OpenStreetMap vector tile map using OpenLayers with an
[ol-mapbox-style](https://github.com/openlayers/ol-mapbox-style) compatible
style: `div.map-wrapper.script` with a `div.map` and a popup div, then an
inline script calling `window.projektemacherMap(...)`. The logic lives in
`ts/maps/` (`mapWrapper.ts` / `projektemacher-map.ts`).

## Parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `src` | string | yes | — | URL/path of the GeoJSON source |
| `style` | string | yes | — | Mapbox style — either an asset path (resolved via `resources.Get`, inlined) or a URL (loaded client side) |
| `source` | string | no | from style | Tile URL overriding the style's source, e.g. `https://tiles.versatiles.org/tiles/osm/{z}/{x}/{y}` |
| `marker` | string | no | `undefined` | OpenLayers icon options as JavaScript object literal, e.g. `{src: '/images/map-marker.svg', scale: 0.1}` |
| `cluster` | any | no | `false` | Cluster point features; clicking a cluster either zooms in or shows a merged popup |
| `bbox` | string | no | `undefined` | Bounding box `[minLon, minLat, maxLon, maxLat]` |
| `center` | string | no | `undefined` | Map center `[lon, lat]`, defaults to the GeoJSON center |

Unlike `maps/osm` this shortcode renders vector tiles via
[ol-mapbox-style](https://github.com/openlayers/ol-mapbox-style) — the `style`
parameter expects a Mapbox style JSON, not a tile layer name.

## Example

```text
{{</* maps/osm-vector-tiles src="/post/map.geojson" style="map-styles/shortbread.json" marker="{src: '/images/map-marker.svg', scale: 1, anchorXUnits: 'fraction', anchorYUnits: 'fraction', anchor: [0.5, 1]}" */>}}
```

The theme ships a generic pin at `static/images/map-marker.svg` (anchor at
the tip, `[0.5, 1]`); sites can replace it with their own marker graphic.
The sprite sheets are expected under `/map-styles/sprites/` and can be
vendored with `scripts/init/get-map-styles.sh` (downloads the sprites
release of [versatiles-org/versatiles-style](https://github.com/versatiles-org/versatiles-style)).

## Notes

- The shortcode declares a `*-metadata` include, so `ts/maps/mapWrapper.ts`
  and `scss/map.scss` are loaded automatically on pages using it
- Map labels are rendered with local webfonts (the style's `glyphs` entry is
  removed by the map wrapper), fonts are loaded from
  `/css/fonts/{font-family}.css` — publish them via `partials/fonts/css.html`
- The style's sprites are expected under `/map-styles/sprites/`
- Wrap the shortcode in `html/iframe-consent` when the external tile service
  requires consent
