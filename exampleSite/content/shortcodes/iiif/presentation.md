---
title: iiif/presentation
displayinlist: false
metaPage: true
---

# iiif/presentation

Embeds a [Presentation API](https://iiif.io/api/presentation/3.0/) manifest using the configured viewer (TIFY by default, see [IIIF configuration](/iiif/configuration/)): a `div.iiif > div.viewer.presentation-api` initialized by `iiifPresentationViewer()` with the manifest URL.

The manifest URL is resolved relative to the page permalink (translation-aware, `.html` stripped).

## Parameters

| Parameter | Type | Required | Purpose |
|---|---|---|---|
| `manifestUrl` | string | yes | Manifest path, relative to the page URL |

## Example

```text
{{</* iiif/presentation manifestUrl="subdir/manifest.json" */>}}
```

## Assets

Via the shortcode helper: JS `js/iiif/tify.js`, SCSS `scss/iiif/presentation-tify.scss`. For the Mirador variant and its build requirements see [Mirador](/posts/mirador/).
