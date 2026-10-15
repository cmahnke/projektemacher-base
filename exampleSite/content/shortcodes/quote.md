---
title: quote
displayinlist: false
metaPage: true
---

# quote

Renders a `div.quote` with a `<blockquote class="quote-body">` and an optional `div.quote-from` attribution. The quote text comes from the inner content, the `quote` parameter or a file (in that priority).

{{< quote from="Ada Lovelace" >}}That brain of mine is something more than merely mortal.{{< /quote >}}

## Parameters

| Parameter | Type | Required | Purpose |
|---|---|---|---|
| `quote` | string | no | Quote text (markdownified, overridden by inner content) |
| `from` | string | no | Attribution line (markdownified) |
| `file` | string | no | File whose content becomes the quote (overridden by inner content) |
| `link` | string | no | Wraps the blockquote in `<a href>` |
| `from-link` | string | no | Wraps the attribution in `<a href>` |
| `source-link` | string | no | Adds a separate "source" (i18n) link after the attribution |

## Example

```text
{{</* quote from="Ada Lovelace" */>}}
That brain of mine is something more than merely mortal.
{{</* /quote */>}}
```
