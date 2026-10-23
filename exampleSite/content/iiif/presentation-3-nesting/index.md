---
title: Presentation 3 Structure Nesting
params:
  displayinlist: false
  metaPage: true
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
outputs: [html, iiif-manifest]
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

Regression fixture for nested `iiif.structure` entries: the output follows IIIF Cookbook recipe 0024 ("Table of Contents for Book Chapters") — a single, always-present root range labeled through the `iiifTableOfContents` i18n key holds the top-level ranges; ranges with sub-ranges list only those sub-ranges, leaf ranges list all canvases of their span, and no first/last canvas markers are emitted. Covers chapter nodes with `page` and sub-sections, a grouping node without `page`, and `end` spans. On Tify ≤ 0.36.2 the previous/next-section pagination and the Info view's current-chapter display stay inactive for such manifests until Tify implements descending span detection (the "dig deeper" TODO in its store). The manifest is available as [`manifest.json`](manifest.json).
