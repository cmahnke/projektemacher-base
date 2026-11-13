---
title: Annotations
params:
  displayinlist: false
  metaPage: true
outputs: [html, iiif-manifest]
resources:
  - name: page0001
    src: cc-page0001.png
    params:
      iiif: tiles/page0001/info.json
      annotations:
        # Inline text (TextualBody) on a canvas region, with a label and a given slug
        - xywh: "4,4,40,20"
          motivation: supplementing
          label: {en: ["Transcription"], de: ["Transkription"]}
          slug: transcription-1
          body:
            value: "This is a supplemental text annotation."
            format: text/plain
            language: en
        # Bilingual text: the language map value expands to one TextualBody per language,
        # the slug is generated (per-canvas running number), the motivation defaults to commenting
        - label: {en: ["Comment"], de: ["Kommentar"]}
          body:
            value: {en: ["An English comment."], de: ["Ein deutscher Kommentar."]}
  - name: page0002
    src: cc-page0002.png
    params:
      iiif: tiles/page0002/info.json
      annotations:
        # Page bundle resource as body: emitted as an Image body with format and
        # dimensions, the motivation defaults to supplementing
        - xywh: "4,4,80,23"
          label: {en: ["Photo"]}
          body:
            id: cc-page0001.png
        # External resource body
        - body:
            id: https://iiif.io/api/image/3.0/example/reference.jpg
            type: Image
            format: image/jpeg
        # Highlighting a region without a body, generated slug,
        # the motivation defaults to highlighting
        - xywh: "44,8,40,19"
---

# Annotations

This page generates a [Presentation API 3](https://iiif.io/api/presentation/3.0/) manifest with annotations added through the `annotations` resource params, see [Page metadata](../page-metadata/#annotations). The manifest is available as [`manifest.json`](manifest.json).

The annotations cover every supported body shape: inline text on a canvas region (`xywh` fragment, `supplementing` motivation, explicit `slug`), a bilingual language map value (one `TextualBody` per language, generated slug), a page bundle resource as image body, an external image resource as body, and a bodyless `highlighting` annotation. They are appended to the painting `AnnotationPage` of their resource's canvas with identifiers generated at build time.
