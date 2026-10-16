---
title: IIIF page metadata
displayinlist: false
metaPage: true
---

# Page metadata

Manifest generation is opt-in per page and driven by front matter.

## Enabling manifests

```yaml
---
title: Example
outputs: [html, iiif-manifest]
---
```

Pages without an explicit `outputs` entry are collected into collections only if the site config defines them, see [Configuration](configuration/).

## Manifest properties (`iiif.` namespace)

| Key | Type | Purpose |
|---|---|---|
| `iiif.presentationVersion` | int | `3` (default) or `4` (draft), see [Presentation 4](presentation-4/) |
| `iiif.behavior` | string | Manifest `behavior`, e.g. `paged` (default), `continuous`, `individuals` |
| `iiif.metadata` | list | Descriptive `metadata` labels/values as JSON list |
| `iiif.structure` | list | JSON list of `structures` (ranges) |
| `iiif.rights` | string | Rights statement URL |
| `iiif.logo.img` | string | Logo image URL |
| `iiif.logo.url` | string | IIIF Image API service endpoint for the logo |
| `iiif.context` | string | Marks the page as IIIF content, e.g. `http://iiif.io/api/presentation/3/context.json` — enables the viewer in `<head>` and the page body |
| `iiif.manifest` | string | Manifest URL used by the embedded viewer (defaults to the page's `manifest.json`) |
| `iiifclass` | string | Additional CSS class for the `iiif` content wrapper |
| `subtype` | string | Additional CSS class for the `iiif` content wrapper |
| `preview` | string | Resource `name` used for manifest/collection thumbnails (falls back to resources named `preview`, `cover`, `front`, then the first resource) |
| `linkedart` | any | If present, adds a `seeAlso` link to the page's `linkedart` output format |

Legacy keys (`iiifMetadata`, `iiifStructure`) abort the build — use `iiif.metadata` / `iiif.structure`.

## Resources

Each entry in `resources` describes one canvas:

```yaml
resources:
  - name: cover            # Canvas name (used in the canvas ID), optional
    src: scan.tif          # Page resource referenced, required
    params:
      iiif: tiles/page0001/info.json  # Image API path, optional — omit for plain images
      hint: non-paged      # Canvas behavior, optional
      label: Front cover   # Canvas label, optional
```

Canvas labels are also derived automatically from the image directory name (`page0001`, `cover`, `front`, `back`, `title`, `end`, …).

For section manifests, `resources` of the section page itself and of all child pages are aggregated into one manifest.

### Plain images

The `iiif` path is optional for pages: a resource without it is embedded as a plain image — the canvas references the file itself instead of an Image API service (no `service` entry in the manifest). The canvas label then falls back to the file name without extension. Audio resources work the same way and are emitted as `Sound` bodies. Resources without `params.iiif` that are neither image nor audio are skipped with a debug warning. Note that leaflet mode (below) and section manifests still require `params.iiif`.

### Leaflet mode

Setting `hint: leaflet-front` or `hint: leaflet-back` on a resource switches manifest generation to the two-sided leaflet layout: one wide canvas per side ("Front"/"Back"), with the panels of that side stitched horizontally via `xywh` fragment targets.

Rules and options:

- Leaflet mode triggers when at least one resource carries a leaflet hint — sections also inspect the resources of their child pages
- In leaflet mode **every** resource with a `params.iiif` path must be sided (`leaflet-front` or `leaflet-back`), and at least one resource of each side is required — the build fails otherwise
- The `structures` (a range per side plus one range per panel) are computed automatically and override `iiif.structure`; setting that key in leaflet mode logs a warning
- `params.label` overrides the default panel label (`Page 1`, `Page 2`, …)
- `iiifLeafletContinuous: true` (a top-level page param, not under `iiif.`) adds `behavior: continuous` to both side ranges

```yaml
---
title: Leaflet example
outputs: [html, iiif-manifest]
iiifLeafletContinuous: true
resources:
  - src: front.tif
    params:
      iiif: tiles/front/info.json
      hint: leaflet-front
  - src: back.tif
    params:
      iiif: tiles/back/info.json
      hint: leaflet-back
---
```

## Viewers

A page with `iiif.context` starting with `http://iiif.io/api/presentation/` embeds the presentation viewer (see `[params.iiif] presentationViewer`), pages with an image context (`http://iiif.io/api/image/`) embed the image viewer.
