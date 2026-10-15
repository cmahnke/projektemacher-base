---
title: html/link-if-exists
displayinlist: false
metaPage: true
---

# html/link-if-exists

Renders a download link (`div.download-link` with `a.link`, `target="_blank"`) to a file relative to the page permalink — but only if the file actually exists on disk. Otherwise nothing is rendered.

See [html/link](../link/) for the variant without the existence check.

## Parameters

| Parameter | Type | Required | Purpose |
|---|---|---|---|
| `file` | string | yes | Path relative to the page |
| `content` | string | no | Link text, defaults to the `file` value |

## Example

```text
{{</* html/link-if-exists file="attachment.pdf" content="Download (PDF)" */>}}
```

## Warnings

- `warnf "File <absolute path> doesn't exist!"` — logged when the file is missing (nothing rendered)
