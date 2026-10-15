---
title: html/div
displayinlist: false
metaPage: true
---

# html/div

Wraps content in a plain `<div class="…">` — a workaround for Markdown's inability to group block elements with classes.

{{< html/div class="note" >}}Content inside a classed div.{{< /html/div >}}

## Parameters

| Parameter | Type | Required | Purpose |
|---|---|---|---|
| `class` | string | no | Class attribute of the div |
| `content` | string | no | Div body as raw string, overrides the inner content |

## Example

```text
{{</* html/div class="note" */>}}Content inside a classed div.{{</* /html/div */>}}
```
