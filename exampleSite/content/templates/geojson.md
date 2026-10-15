---
title: GeoJSON
displayinlist: false
metaPage: true
---

# GeoJSON

Template: `_default/section.geojson`, output format `geojson`. It renders a section as a [GeoJSON](https://geojson.org/) `FeatureCollection` — one feature per page in the section that provides GeoJSON data.

## Usage

The template collects all pages of the current section with a `geojson` front matter parameter and renders them via the `geojson/featureCollection.geojson` partial, which uses the `geojson/feature.geojson` and `geojson/popupContent.html` partials per page.

A page needs at least a marker definition, e.g.:

```markdown
---
title: A place
geojson:
  coordinates: [10.0, 53.55]
---
```

The rendered popup content is the page content, an HTML preview can be generated separately (`geojson/popupContent-preview.html`).

## Enabling

```toml
[outputFormats]
  [outputFormats.geojson]
        mediaType = "application/geo+json"
        baseName = "geojson"

[outputs]
    section = ["HTML", "geojson"]
```

The generated file is available as `<section>/geojson.json` and can be loaded into the [OpenStreetMap shortcode](/shortcodes/maps/osm/).
