---
title: pdf
displayinlist: false
metaPage: true
---

# pdf

Renders a PDF viewer container (`div.pdf-viewer`) initialized by the global `addPDFViewer()` JS function, plus an optional download link. The path is relative to the page permalink.

Unlike [pdf-preview](../pdf-preview/) this shortcode declares no metadata — its viewer JS/CSS must be loaded globally (e.g. `assets/js/pdf-viewer.js`).

## Parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `file` | string | yes | — | PDF path relative to the page |
| `download` | string | no | `true` | Set to anything but `true` to hide the download link |

## Example

```text
{{</* pdf file="document.pdf" */>}}
```
