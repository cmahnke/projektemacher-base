---
title: print/image
displayinlist: false
metaPage: true
---

# print/image

Renders a `<figure><img src="…"></figure>` for the print edition, optionally wrapped in a link. The image path is the page path joined with `src`, then stripped of the first `print.relative` characters — a site parameter used to adjust paths for the print build's directory layout.

## Parameters

| Parameter | Type | Required | Purpose |
|---|---|---|---|
| `src` | string | yes | Image path relative to the page |
| `alt` | string | no | Alt text |
| `class` | string | no | Class on the `<figure>` |
| `link` | string | no | Wraps the figure in `<a href>` |

## Site config

`print.relative` — path offset applied to the computed image URL (default `0`).

## Example

```text
{{</* print/image src="images/scan.png" alt="Scan of page 12" */>}}
```
