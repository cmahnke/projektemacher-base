---
title: Presentation 3
params:
  displayinlist: false
  metaPage: true
  iiif:
    structure:
      - label: {en: ["Cover"]}
        page: page0001
outputs: [html, iiif-manifest]
resources:
  - name: page0001
    src: cc.png
    params:
      iiif: tiles/page0001/info.json
---

# Presentation API 3

This page generates a [Presentation API 3](https://iiif.io/api/presentation/3.0/) manifest from its page `resources`, see [Page metadata](../page-metadata/). The manifest is available as [`manifest.json`](manifest.json).
The `iiif.structure` front matter adds a logical structure (the `structures` in the manifest) with range and canvas identifiers generated at build time, see [Structure](../page-metadata/#structure).
