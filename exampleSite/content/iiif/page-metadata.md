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
      iiif: tiles/page0001/info.json  # Image API path, required
      hint: non-paged      # Canvas behavior, optional
      label: Front cover   # Canvas label, optional
```

Canvas labels are also derived automatically from the image directory name (`page0001`, `cover`, `front`, `back`, `title`, `end`, …).

For section manifests, `resources` of the section page itself and of all child pages are aggregated into one manifest.

## Viewers

A page with `iiif.context` starting with `http://iiif.io/api/presentation/` embeds the presentation viewer (see `[params.iiif] presentationViewer`), pages with an image context (`http://iiif.io/api/image/`) embed the image viewer.
