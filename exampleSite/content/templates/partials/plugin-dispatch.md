---
title: Plug-in dispatch
displayinlist: false
metaPage: true
---

# Plug-in dispatch

Several theme features select a partial **by name** at build time — new variants can be added by a site without touching the theme.

## Tag cloud {#tag-cloud}

The [`tags/cloud` shortcode](/shortcodes/tags/cloud/) and [`meta/tags.html`](structural/#tags) render each tag through a partial selected by name:

- `meta/tags.html`: the page parameter `render` names the variant, prefixed with `tag-` (default: `tag.html`)
- `tags/cloud` shortcode: the `tag` parameter names the variant, prefixed with `tag-` (default: `tag.html`)

Shipped variants (all receive the tag as input, via the `tag2str` normalizer which accepts strings, terms and taxonomy entries):

| Partial | Rendering |
|---|---|
| `tagcloud/tag.html` | Raw tag string |
| `tagcloud/tag-humanize.html` | Humanized (`my-tag` → `My tag`) |
| `tagcloud/tag-i18n.html` | Translated via the i18n files |
| `tagcloud/tag-page.html` | Title of the tag's term page (needs a page as context) |
| `tagcloud/tag-replace-hyphen.html` | Hyphens replaced with spaces |

A site adds its own variant by creating `layouts/partials/tagcloud/tag-<name>.html`.

## GeoJSON popups {#geojson-popups}

The [`geojson` template](../geojson/) renders each feature's popup content through a partial selected by the `popupContent` scratch value:

- `geojson/popupContent.html` — default: title, markdownified raw content (shortcodes stripped) and a "read more" link in a `geojsonPopup` div
- `geojson/popupContent-preview.html` — preview variant

A site adds variants as `layouts/partials/geojson/popupContent-<name>.html`.

## schema.org templates

The `metadata/schema.org/schema.org.html` dispatcher selects the rendering template per page, see [metadata partials](metadata-partials/) and the site provided templates in [extension points](extension-points/#schemaorghash-html-per-type-metadata).

## IIIF manifests

The manifest templates select `iiif/3/manifest.json` or `iiif/4/manifest.json` by the resolved [Presentation API version](../iiif-templates/#presentation-api-version).
