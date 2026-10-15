---
title: figure
displayinlist: false
metaPage: true
---

# figure

Renders a `<figure>` with `<img>` and optional `<figcaption>` (based on [kaushalmodi's refined theme](https://gitlab.com/kaushalmodi/hugo-theme-refined/blob/master/layouts/shortcodes/figure.html)).

Handles three `src` modes: full URLs (`http(s)…` or `//`), site-absolute paths (`/…`, prepended with the site BaseURL) and page-relative paths (prepended with the page permalink — the default language's permalink for translated pages).

{{< figure src="/images/cc.png" alt="CC logo" caption="Example caption" >}}

## Parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `src` | string | yes | — | Image URL or path |
| `link` | string | no | — | Wrap the image in `<a href>` |
| `target`, `rel` | string | no | — | Attributes for the wrapping `<a>` (with `link`) |
| `alt` | string | no | caption | Image alt text |
| `caption` | string | no | — | Figure caption (markdownified) |
| `title` | string | no | — | Rendered as `<h4>` in the figcaption |
| `width`, `height` | string | no | — | Image dimensions |
| `class` | string | no | — | Class on the `<figure>` |
| `attr` | string | no | — | Attribution (markdownified) |
| `attrlink` | string | no | — | Wraps the attribution in `<a href>` |

## Example

```text
{{</* figure src="/images/cc.png" caption="Example caption" */>}}
```
