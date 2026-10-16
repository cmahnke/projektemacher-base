---
title: Presentation 3 Structure Nesting
displayinlist: false
metaPage: true
outputs: [html, iiif-manifest]
iiif:
  structure:
    - label: {en: ["Chapter 1"]}
      page: page0002
      items:
        - label: {en: ["Chapter 1a"]}
          page: page0002
        - label: {en: ["Chapter 1b"]}
          page: page0003
    - label: {en: ["Part 2"]}
      items:
        - label: {en: ["Chapter 2a"]}
          page: page0003
          end: page0004
        - label: {en: ["Chapter 2b"]}
          page: page0004
    - label: {en: ["Appendix"]}
      page: page0005
resources:
  - name: page0001
    src: cc.png
    params:
      iiif: tiles/page0001/info.json
  - name: page0002
    src: cc.png
    params:
      iiif: tiles/page0001/info.json
  - name: page0003
    src: cc.png
    params:
      iiif: tiles/page0001/info.json
  - name: page0004
    src: cc.png
    params:
      iiif: tiles/page0001/info.json
  - name: page0005
    src: cc.png
    params:
      iiif: tiles/page0001/info.json
---

# Presentation API 3 Structure Nesting

Regression fixture for nested `iiif.structure` entries: ranges with inline children are emitted as `startCanvas … childRanges … endCanvas` so consumers relying on the first/last `items` entry being a canvas (e.g. Tify's table of contents heuristic) compute the correct page span. Covers chapter nodes with `page` and sub-sections, a grouping node without `page`, and `end` spans. The manifest is available as [`manifest.json`](manifest.json).
