---
title: color-sample
displayinlist: false
metaPage: true
---

# color-sample

Renders an inline color swatch (`div.color-sample`), optionally showing the color code as text — mainly useful for the print edition.

{{< color-sample color="olive" text="olive" print=true >}}

## Parameters

| Parameter | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `color` | string | yes | — | Any CSS color for the background |
| `text` | string | no | `&nbsp;` | Label inside the swatch (markdownified) |
| `print` | any | no | — | If set, appends `span.color-sample-code` with the raw color value |

## Example

```text
{{</* color-sample color="olive" text="olive" print=true */>}}
```
