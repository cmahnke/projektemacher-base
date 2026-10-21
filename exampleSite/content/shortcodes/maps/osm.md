---
title: maps/osm
displayinlist: false
metaPage: true
---

# maps/osm

Renders an OpenStreetMap container for OpenLayers: `div.map-wrapper.script` with a `div.map` and a popup div, then an inline script calling `window.initMap(id, geojsonURL, 'osm', cluster[, marker])` followed by `updateSize()`. The actual logic lives in the partial `maps/osm.html`; the shortcode is a thin wrapper.

## Parameters

| Parameter | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `src` | string | yes | — | URL/path of the GeoJSON source |
| `cluster` | any | no | `false` | Enable point clustering |
| `marker` | any | no | `false` | Marker configuration, passed through to the OpenLayers icon style |

## Example

```text
{{</* maps/osm src="/geojson/places.geojson" cluster="true" */>}}
```

## Live demo

Loads the example GeoJSON from [`static/geojson/`](https://github.com/cmahnke/projektemacher-base/tree/main/exampleSite/static/geojson) with clustering enabled:

{{< maps/osm src="/geojson/places.geojson" cluster="true" >}}

## Notes

- The map JS (`ts/maps/osm-map.ts`, exposing `window.initMap`) and the styles (`scss/map.scss`, `scss/openlayers.scss` with the OpenLayers base CSS) are loaded automatically via the shortcode metadata
- The partial has a TODO about wrapping the map in a consent overlay (see [html/iframe-consent](../html/iframe-consent/))
