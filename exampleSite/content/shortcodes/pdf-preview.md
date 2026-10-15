---
title: pdf-preview
displayinlist: false
metaPage: true
---

# pdf-preview

Embeds an inline PDF preview via [PDFObject](https://pdfobject.com/) (`PDFObject.embed`) into a uniquely ID'd div, with a fallback notice (i18n `InlinePDFNotSupported`) and an optional download link (i18n `pdfDownload`). The path is relative to the page permalink (translation-aware).

## Parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `pdf` | string | yes | — | PDF path relative to the page (nothing rendered when empty) |
| `page` | int | no | `1` | Initial page |
| `class` | string | no | `pdf-preview` | Class on the container |
| `download` | any | no | `false` | Show the download link |

## Example

```text
{{</* pdf-preview pdf="document.pdf" page="2" download="true" */>}}
```

## Assets

Via the shortcode helper: JS `js/pdf-preview.js`, SCSS `scss/pdf-preview.scss`.

## Warnings

- `warnf "File <page path>/<pdf> doens't exist!"` when the file can't be found on disk (rendering continues)
