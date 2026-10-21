---
title: html/comment
params:
  displayinlist: false
  metaPage: true
---

# html/comment

Outputs the inner content wrapped in an HTML comment (`<!-- … -->`) — useful to keep notes in the published HTML or to disable markup.

## Parameters

None (inner content only).

## Example

```text
{{</* html/comment */>}}This text is only visible in the page source.{{</* /html/comment */>}}
```
