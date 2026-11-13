---
title: IIIF page metadata
params:
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
| --- | --- | --- |
| `iiif.presentationVersion` | int | `3` (default) or `4` (draft), see [Presentation 4](presentation-4/) |
| `iiif.behavior` | string | Manifest `behavior`, e.g. `paged` (default), `continuous`, `individuals` |
| `iiif.metadata` | list | Descriptive `metadata` entries with `label`/`value` (language maps, coerced to strings), see the example below |
| `iiif.structure` | list | Logical structure (ranges) from `label`/`page`/`end`/`items` entries — range and canvas IDs are generated at build time, see [Structure](#structure) |
| `iiif.annotations` | list | Annotation entries appended to the canvases' `AnnotationPage` — annotation IDs are generated at build time, see [Annotations](#annotations) |
| `iiif.rights` | string | Rights statement URL |
| `iiif.attribution` | string | Custom attribution text for the manifest `requiredStatement` (default: "Provided by Projektemacher" / "Bereitgestellt von Projektemacher"); the legacy `iiifAttribution` key aborts the build |
| `iiif.logo.img` | string | Logo image URL |
| `iiif.logo.url` | string | IIIF Image API service endpoint for the logo |
| `iiif.context` | string | Marks the page as IIIF content, e.g. `http://iiif.io/api/presentation/3/context.json` — enables the viewer in `<head>` and the page body |
| `iiif.manifest` | string | Two purposes: with a presentation `iiif.context`, the manifest URL used by the embedded viewer (defaults to the page's `manifest.json`); without, a [pre-made manifest](#pre-made-manifests) file looked up in the page bundle |
| `iiif.baseURL` | string | Base URL a [pre-made manifest](#pre-made-manifests) was generated with (the `--baseURL` of the generating build) — mandatory when that manifest contains absolute URLs |
| `iiifclass` | string | Additional CSS class for the `iiif` content wrapper |
| `subtype` | string | Additional CSS class for the `iiif` content wrapper |
| `preview` | string or object | Resource `name` — or an object `{image: <resource src>}` matched against `src` — used for manifest/collection thumbnails (falls back to resources named `preview`, `cover`, `front`, then the first resource) |
| `linkedart` | any | If present, adds a `seeAlso` link to the page's `linkedart` output format |

Legacy keys (`iiifMetadata`, `iiifStructure`) are no longer read and no longer abort the build — migrate to `iiif.metadata` / `iiif.structure`.

The page `description` becomes the manifest `summary`. Pages with an `issueYear` or `year` front matter param get an automatic `Erscheinungsjahr` / `Year of publication` entry appended to the manifest `metadata`; `scripts/pdf.py` writes the same year to the PDF XMP `dc:date`.

`iiif.metadata` entries accept language maps for both `label` and `value` (scalar values are coerced to strings):

```yaml
iiif:
  metadata:
    - label: {en: ["Shelf mark"], de: ["Signatur"]}
      value: {en: ["Ms. 123"], de: ["Ms. 123"]}
```

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
- Entries with nested `items` contain ONLY their sub-ranges (IIIF Cookbook recipe 0024); the result is wrapped in a single root range labeled via the `iiifTableOfContents` i18n key, and leaf ranges list all canvases of their span. No first/last canvas markers are emitted — with Tify ≤ 0.36.2 the previous/next-section pagination and the Info view's current-chapter display stay inactive until Tify implements descending span detection (the "dig deeper" TODO in its store)
- An entry must resolve to at least one canvas or group nested items, otherwise the build fails
- Hand-written `id`s or legacy IIIF Range entries abort the build
- `iiif.structure` is only expanded on pages; sections keep the raw value (leaflet mode computes its own ranges and ignores the key, see above)
- The same structure data drives the PDF bookmarks in `scripts/pdf.py`

## Annotations

The `iiif.annotations` key adds annotations to the manifest's canvases. Each entry appends an `Annotation` to the target canvas's painting `AnnotationPage`, with identifiers generated at build time using the same deployment prefix as the rest of the manifest — the front matter carries no IDs or URLs:

```yaml
---
title: Example
outputs: [html, iiif-manifest]
iiif:
  annotations:
    # Inline text (TextualBody) on a canvas region, with label and explicit slug
    - page: page004-verso
      xywh: "120,300,800,600"
      motivation: supplementing
      label: {de: ["Transkription"]}
      slug: transcription-1
      body:
        value: "Der Text der Anmerkung"
        format: text/plain
        language: de
    # Bilingual text: the language map value expands to one TextualBody per language,
    # the slug is generated
    - page: page012
      body:
        value: {de: ["Deutscher Kommentar."], en: ["English comment."]}
    # External resource body
    - page: front
      body:
        id: https://example.org/detail.jpg
        type: Image
        format: image/jpeg
    # Highlighting a region without a body
    - page: page001
      xywh: "0,0,100,100"
      motivation: highlighting
---
```

A working example covering every body shape is available as [Annotations](annotations/).

Rules:

- `page` is required and references a resource of the page bundle, resolved like `iiif.structure` (resource `name`, `params.iiif` directory or `src` basename)
- `xywh` (optional) targets a pixel region `x,y,w,h` on the canvas; without it the annotation targets the whole canvas
- `motivation` defaults to `commenting`; supported values are the W3C Web Annotation motivations used by IIIF: `assessing`, `bookmarking`, `classifying`, `commenting`, `describing`, `highlighting`, `identifying`, `linking`, `modifying`, `questioning`, `replying`, `tagging` (`painting` is reserved for the manifest's own resources)
- `slug` (optional) is the identifier suffix — the annotation ID becomes `annotation/{canvas}/{slug}`; when omitted a per-canvas running number (`1`, `2`, …) is generated. Slugs must be URL-safe (letters, digits, dash, underscore) and unique per canvas — duplicates, including collisions with generated numbers, abort the build
- `label` is an optional IIIF label object, coerced to strings
- `body` is one of:
  - a text body: `value` as a string or a language map (one `TextualBody` per language), optional `format` (`text/plain` by default, `text/html` allowed) and `language`
  - an external resource: `id` plus `type` (e.g. `Image`, `Text`), optional `format` and `label`
  - omitted: only valid with `motivation: highlighting`
- Hand-written `id`s abort the build — identifiers are generated
- Annotations are appended to the painting `AnnotationPage` of the target canvas, after the painting annotation
- `iiif.annotations` is only expanded on pages: sections ignore the value with a warning, leaflet mode ignores it (its canvases are computed), and pre-made manifests don't inject front-matter annotations
- Tify renders these annotations via the bundled `@projektemacher/tify-plugin-annotorious` plugin

## Pre-made manifests

A page bundle can carry an externally generated IIIF Presentation 3 manifest — e.g. produced by a digitisation or OCR pipeline — instead of building one from `resources`:

```yaml
---
title: Example
outputs: [html, iiif-manifest]
iiif:
  manifest: ./manifest.json                 # pre-made manifest file in the page bundle (file name only)
  baseURL: https://build.example.org/mysite/ # the --baseURL the manifest was generated with
---
```

Rules:

- Only the file name is used; the file must live in the page bundle itself (looked up as a page resource, so this works with any content directory name)
- The build aborts when the manifest contains absolute URLs without `iiif.baseURL`; manifests with relative URLs only need no param
- Presentation 3 manifests get every URL-bearing field rewritten for the deployment environment (dev server or `productionIIIFURLPrefix`, like generated manifests): absolute URLs starting with `iiif.baseURL` are cut to the deployment prefix, relative URLs are prepended with it, external URLs are kept. Covered: canvas IDs, thumbnail IDs, annotation IDs and targets, painting body and service IDs, and renderings on canvas and manifest level. The manifest's own `id` is left untouched (it documents the source file; consumers fetch the served URL)
- Thumbnail IDs are additionally snapped to the guaranteed `full/full/0/default.jpg` rendition — static level0 pipelines don't generate arbitrary widths — and the canvas dimensions are declared on the thumbnail entry
- `iiif.structure` (if set) replaces the manifest's own `structures`; a warning is logged when replacing. Pre-made manifests without front-matter structures keep their own
- Any other manifest version passes through unchanged; front-matter annotations are not injected into pre-made manifests

## Viewers

A page with `iiif.context` starting with `http://iiif.io/api/presentation/` embeds the presentation viewer (see `[params.iiif] presentationViewer`), pages with an image context (`http://iiif.io/api/image/`) embed the image viewer.
