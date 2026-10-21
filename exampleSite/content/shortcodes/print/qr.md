---
title: print/qr
displayinlist: false
metaPage: true
---

# print/qr

Generates a QR code image at build time (Hugo's `images.QR`) and renders it as an `<img>`; the URL is adjusted by the `print.relative` site parameter. The payload comes from the `text` parameter or the inner content.

## Parameters

| Parameter | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `text` | string | yes* | — | QR payload (if no inner content is given) |
| `scale` | int | no | `4` | Pixel scale of the generated image |
| `alt` | string | no | `""` | Alt text |
| `class` | string | no | `""` | Class on the `<img>` |
| `title` | string | no | `""` | Title attribute |

\* required unless the inner content provides the payload.

## Example

```text
{{</* print/qr text="https://example.org/" scale="6" */>}}
```

## Errors

- `errorf "The %q shortcode requires a %q argument…"` when neither `text` nor inner content is given
