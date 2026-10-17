---
title: pdf
displayinlist: false
metaPage: true
---

# pdf

Renders a PDF viewer container (`div.pdf-viewer`) initialized by the global `addPDFViewer()` JS function, plus an optional download link. The path is relative to the page permalink.

JS `ts/pdf-viewer.ts` and SCSS `scss/pdf-viewer.scss` are loaded automatically via the shortcode metadata.

## Parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `file` | string | yes | — | PDF path relative to the page |
| `download` | string | no | `true` | Set to anything but `true` to hide the download link |

## Example

```text
{{</* pdf file="document.pdf" */>}}
```

## Live demo

Loads the [demo.pdf](demo.pdf) page resource of this page:

{{< pdf file="demo.pdf" >}}
