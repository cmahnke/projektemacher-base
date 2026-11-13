---
title: Annotations
params:
  displayinlist: false
  metaPage: true
  iiif:
    annotations:
      # Inline text (TextualBody) on a canvas region, with a label and a given slug
      - page: page0001
        xywh: "10,10,120,120"
        motivation: supplementing
        label: {en: ["Transcription"], de: ["Transkription"]}
        slug: transcription-1
        body:
          value: "This is a supplemental text annotation."
          format: text/plain
          language: en
      # Bilingual text: the language map value expands to one TextualBody per language,
      # the slug is generated (per-canvas running number)
      - page: page0001
        label: {en: ["Comment"], de: ["Kommentar"]}
        body:
          value: {en: ["An English comment."], de: ["Ein deutscher Kommentar."]}
      # External resource body on the second canvas
      - page: page0002
        body:
          id: https://iiif.io/api/image/3.0/example/reference.jpg
          type: Image
          format: image/jpeg
      # Highlighting a region without a body, generated slug
      - page: page0002
        xywh: "0,0,64,64"
        motivation: highlighting
outputs: [html, iiif-manifest]
resources:
  - name: page0001
    src: cc-page0001.png
    params:
      iiif: tiles/page0001/info.json
  - name: page0002
    src: cc-page0002.png
    params:
      iiif: tiles/page0002/info.json
---

# Annotations

This page generates a [Presentation API 3](https://iiif.io/api/presentation/3.0/) manifest with annotations added through the `iiif.annotations` front matter, see [Page metadata](../page-metadata/#annotations). The manifest is available as [`manifest.json`](manifest.json).

The annotations cover every supported body shape: inline text on a canvas region (`xywh` fragment, `supplementing` motivation, explicit `slug`), a bilingual language map value (one `TextualBody` per language, generated slug), an external image resource as body, and a bodyless `highlighting` annotation. They are appended to the painting `AnnotationPage` of their target canvas with identifiers generated at build time.
