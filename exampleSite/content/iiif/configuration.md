---
title: IIIF configuration
displayinlist: false
metaPage: true
---

# Site configuration

All IIIF related settings live in `[params.iiif]`:

```toml
[params.iiif]
  # Presentation API version used for manifests: 3 (default) or 4 (draft)
  # Can be overridden per page, see 'Presentation 4'
  presentationVersion = 3

  # JS asset for the Presentation API viewer, default: 'ts/iiif/tify.ts' (TIFY)
  presentationViewer = "ts/iiif/tify.ts"

  # JS asset for the Image API viewer, default: 'ts/iiif-image-viewer.ts' (OpenLayers)
  imageViewer = "ts/iiif-image-viewer.ts"
```

In production, manifest and canvas IDs can be reprefixed to point to a dedicated IIIF server:

```toml
[params]
  productionIIIFURLPrefix = "https://iiif.example.org/"
```

When running with `hugo server` this is ignored and local URLs are used.

## Output formats

The theme doesn't define IIIF output formats itself — consuming sites opt in. Required definitions:

```toml
[mediaTypes."application/ld+json"]
  suffixes = ["json"]

[outputFormats.iiif-manifest]
  mediaType = "application/ld+json"
  isPlainText = true
  isHTML = false

[outputFormats.iiif-collection]
  mediaType = "application/ld+json"
  isPlainText = true
  isHTML = false
```

Manifests are then enabled per page via front matter:

```yaml
---
outputs: [html, iiif-manifest]
---
```

Collections are enabled globally for home and term pages:

```toml
[outputs]
  home = ["html", "rss", "iiif-collection"]
```

The legacy `[outputFormats.iiif]` (Presentation API 2) must be removed — it aborts the build with an error, see the [section overview](/iiif/).
