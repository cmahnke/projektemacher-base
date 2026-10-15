---
title: print/status
displayinlist: false
metaPage: true
---

# print/status

Renders a `div.print-status` block with a "generated" timestamp (i18n `generated`, long date + short time). In non-print environments it additionally shows the Git revision (abbreviated hash via `.Page.GitInfo`, i18n `revision`) and optional notes.

## Parameters

| Parameter | Type | Required | Purpose |
|---|---|---|---|
| `notes` | string | no | Extra notes (markdownified), only rendered outside the `print` environment |

## Example

```text
{{</* print/status notes="Generated from the working tree" */>}}
```

## Requirements

GitInfo must be enabled for the revision display (`enableGitInfo = true`).
