---
title: IIIF partials
displayinlist: false
metaPage: true
---

# IIIF partials

The `iiif/` partials render IIIF content and build the JSON documents for the [IIIF output formats](../iiif-templates/). Configuration and front matter are documented in the [IIIF section](/iiif/).

## Viewers

These partials render viewer markup for a page's `resources`. They are called by the [IIIF shortcodes](/shortcodes/iiif/iiif/) and by consuming sites directly:

| Partial | Purpose |
| --- | --- |
| `iiif/iiif-image.html` | [Image API](https://iiif.io/api/image/3.0/) viewer (OpenLayers). Called with a dict of `context` (resource), `contextPath`, `pageURL`, `pageContext` and `site` |
| `iiif/_iiif-image.html` | Internal markup used by the image viewer |
| `iiif/iiif-presentation.html` | [Presentation API](https://iiif.io/api/presentation/3.0/) viewer (TIFY) for a page's manifest (`iiifManifest` front matter parameter) |
| `iiif/iiif-presentation-pdf.html` | Presentation viewer with PDF download link (site parameter `pdfDownload`) |
| `iiif/iiif-content.html` | Renders a page's IIIF image resources directly (Image API `iiifcontext`), CSS class from the `subtype` and `iiifclass` page parameters |
| `iiif/kenburns.html` | Ken Burns style slideshow over the page's `resources` (the `featured` parameter selects images) |
| `iiif/preview.html` | Renders a preview image of a page's IIIF resource, called with the page or a dict of `context`, `name` and `src` |

### Site parameters

| Parameter | Used by | Purpose |
| --- | --- | --- |
| `productionIIIFURLPrefix` | `iiif-presentation.html` | URL prefix for manifests in production builds (parts are commented out, currently unused) |
| `pdfDownload` | `iiif-presentation-pdf.html` | PDF download link |
| `minimalUI` | viewer partials | Minimal viewer UI |
| `iiif.presentationVersion` | manifest generation, see [version resolution](../iiif-templates/#presentation-api-version) | Presentation API version 3 or 4 |

## Manifest and collection building blocks

The JSON partials under `iiif/3/` and `iiif/4/` assemble the Presentation API documents — they are called by the [IIIF templates](../iiif-templates/), `iiif/4/manifest.json` is dispatched dynamically by the resolved [presentation version](../iiif-templates/#presentation-api-version):

- `iiif/3/collection.json` — collection wrapper, also used by the collection output formats
- `iiif/3/common.json`, `manifest.json`, `manifest-label.json`, `manifest-summary.json`, `required-statement.json`, `provider.json`, `thumbnail.json`
- `iiif/4/manifest.json` — Presentation API 4 (draft) manifest

Site parameters `iiif.requiredStatement`, `iiif.logo`, `iiif.provider` etc. feed these partials, see [IIIF page metadata](/iiif/page-metadata/).
