---
title: html/rawhtml
params:
  displayinlist: false
  metaPage: true
---

# html/rawhtml

Bypasses Hugo's Markdown sanitization by emitting the inner content verbatim, preceded by an `<!-- raw html -->` comment (the [anaulin.org raw HTML shortcode](https://anaulin.org/blog/hugo-raw-html-shortcode/) pattern). Useful when Markdown mangles otherwise valid HTML.

## Parameters

None (inner content only).

## Example

```html
{{</* html/rawhtml */>}}
<details><summary>Click me</summary>Raw HTML content</details>
{{</* /html/rawhtml */>}}
```
