---
title: footnote
displayinlist: false
metaPage: true
---

# footnote

Renders a superscript footnote reference (`<sup id="fnref:…">` linking to `#fn:…`) and stores the footnote text in the page's store for later output by [footnote-list](../footnote-list/).

This is a test of the footnote shortcode{{< footnote 1 "This is the footnote text." >}} in a page.

## Parameters

Positional arguments:

| Position | Type | Required | Purpose |
| --- | --- | --- | --- |
| 0 | string | yes | Footnote ID |
| 1 | string | yes | Footnote text (markdownified) |

## Example

```text
Some text{{</* footnote 1 "The footnote text." */>}} continues here.
```
