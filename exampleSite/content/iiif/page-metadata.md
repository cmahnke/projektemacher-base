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
| `iiif.structure` | list | Logical structure (ranges) from `label`/`page`/`end`/`items` entries — range and canvas IDs are generated at build time, see [Structure](#structure) |
| `iiif.rights` | string | Rights statement URL |
| `iiif.logo.img` | string | Logo image URL |
| `iiif.logo.url` | string | IIIF Image API service endpoint for the logo |
| `iiif.context` | string | Marks the page as IIIF content, e.g. `http://iiif.io/api/presentation/3/context.json` — enables the viewer in `<head>` and the page body |
| `iiif.manifest` | string | Manifest URL used by the embedded viewer (defaults to the page's `manifest.json`) |
| `iiifclass` | string | Additional CSS class for the `iiif` content wrapper |
| `subtype` | string | Additional CSS class for the `iiif` content wrapper |
| `preview` | string | Resource `name` used for manifest/collection thumbnails (falls back to resources named `preview`, `cover`, `front`, then the first resource) |
| `linkedart` | any | If present, adds a `seeAlso` link to the page's `linkedart` output format |

Legacy keys (`iiifMetadata`, `iiifStructure`) are no longer read and no longer abort the build — migrate to `iiif.metadata` / `iiif.structure`.

Pages with an `issueYear` front matter param get an automatic `Erscheinungsjahr` / `Year of publication` entry appended to the manifest `metadata`; `scripts/pdf.py` writes the same year to the PDF XMP `dc:date`.

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

The `iiif` path is optional for pages: a resource without it is embedded as a plain image — the canvas references the file itself instead of an Image API service (no `service` entry in the manifest). The canvas label then falls back to the file name without extension. Audio resources work the same way and are emitted as `Sound` bodies. Resources without `params.iiif` that are neither image, audio nor model are skipped with a debug warning. Note that leaflet mode (below) and section manifests still require `params.iiif`.

### 3D models

GLB resources (`model/gltf-binary`) are painted into [Presentation API 4 `Scene` containers](https://iiif.io/api/presentation/4.0/#scene) with an annotation whose body has the type `Model` — the API 3 canvas model has no depth, so 3D models require `iiif.presentationVersion: 4` and abort the build otherwise:

```yaml
---
title: Example
outputs: [html, iiif-manifest]
iiif:
  presentationVersion: 4
  behavior: individuals
resources:
  - src: model/example.glb
    params:
      label: Example model
---
```

Rules and options:

- The Scene has no `height`/`width` — the Presentation 4 `Scene` container is boundless by design
- A sibling image file named like the GLB (`example.jpg` next to `example.glb`) is used as thumbnail for the Scene and the manifest — a missing poster just omits the thumbnail, the build doesn't fail
- Resources outside the page bundle are supported for GLB models: a `src` starting with `/` or `http` is referenced by URL
- For section manifests, GLB resources need a truthy `params.iiif` marker like image resources
- The site must register the media type:

```toml
[mediaTypes."model/gltf-binary"]
  suffixes = ["glb"]
```

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

## Structure

The `iiif.structure` key describes the logical structure of a manifest — table of contents entries, chapters, significant full-page illustrations — as nested entries. Range and canvas identifiers are generated at build time with the same deployment prefix as the rest of the manifest, so the front matter carries no IDs or URLs:

```yaml
---
title: Example
outputs: [html, iiif-manifest]
iiif:
  structure:
    - label: {de: ["Einband"]}
      page: front
    - label: {de: ["Kapitel 1"]}
      page: page012
      items:
        - label: {de: ["Kapitel 1.1"]}
          page: page012
        - label: {de: ["Illustration"]}
          page: page014
    - label: {de: ["Kapitel 2"]}
      page: page016
      end: page021
---
```

Rules:

- `label` is a required IIIF label object, coerced to strings
- `page` references a resource of the page bundle, resolved by the resource's `name`, its `params.iiif` directory or its `src` basename (without extension) — the same chain used for canvas naming
- `end` (optional) spans the range over all canvases from `page` to `end`, inclusive
- `items` nests entries with the same shape; an entry without `page` is a grouping node
- Entries with nested `items` are emitted as a full canvas span: their first and last `items` entry are Canvas references (wrapping the inline child ranges), so viewers that derive a range's page span from the first and last item (e.g. Tify's table of contents) cover the whole section — grouping nodes without `page` get both a leading and a trailing canvas reference
- An entry must resolve to at least one canvas or group nested items, otherwise the build fails
- Hand-written `id`s or legacy IIIF Range entries abort the build
- `iiif.structure` is only expanded on pages; sections keep the raw value (leaflet mode computes its own ranges and ignores the key, see above)
- The same structure data drives the PDF bookmarks in `scripts/pdf.py`

## Viewers

A page with `iiif.context` starting with `http://iiif.io/api/presentation/` embeds the presentation viewer (see `[params.iiif] presentationViewer`), pages with an image context (`http://iiif.io/api/image/`) embed the image viewer.
