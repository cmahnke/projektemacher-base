---
title: IIIF templates
displayinlist: false
metaPage: true
---

# IIIF templates

The IIIF related output formats generate [IIIF Presentation API](https://iiif.io/api/presentation/3.0/) resources. All details about configuration and front matter are documented in the [IIIF section](/iiif/), this page lists the templates involved.

| Template | Output format | Purpose |
|---|---|---|
| `_default/home.iiif-collection.json` | `iiif-collection` | Collection of all manifests, merging pages of all languages |
| `_default/term.iiif-collection.json` | `iiif-collection` | Collection for a term or section page |
| `_default/single.iiif-manifest.json` | `iiif-manifest` | Manifest for a single page |
| `_default/section.iiif-manifest.json` | `iiif-manifest` | Manifest for a section page |

All of them delegate to the `iiif/3/` partials (and `iiif/4/` for the Presentation API 4 draft). Pages with `displayinlist: false` are excluded from collections.

## Presentation API version

The version (3 or 4) is resolved per page with this priority:

1. Page front matter: `iiif.presentationVersion`
2. Site parameter: `[params.iiif] presentationVersion`
3. Default: `3`

Any other value aborts the build, see [Presentation 4](/iiif/presentation-4/).

## Enabling

```toml
[outputFormats]
  [outputFormats.iiif-manifest]
    mediaType = "application/ld+json"
    baseName = "manifest"
    isPlainText = true
    isHTML = false

[outputs]
    page = ["HTML", "iiif-manifest"]
```

Working examples: [Presentation 3](/iiif/presentation-3/) and [Presentation 4](/iiif/presentation-4/).
