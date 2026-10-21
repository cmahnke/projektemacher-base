---
title: html/link
params:
  displayinlist: false
  metaPage: true
---

# html/link

Renders a download link (`div.download-link` with `a.<class>`, `target="_blank"`) to a file relative to the page permalink — without any existence check (see [html/link-if-exists](../link-if-exists/) for the checked variant).

## Parameters

| Parameter | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `file` | string | yes | — | Path relative to the page |
| `content` | string | no | the `file` value | Link text |
| `class` | string | no | `link` | Class on the `<a>` |

## Example

```text
{{</* html/link file="attachment.pdf" content="Download (PDF)" */>}}
```
