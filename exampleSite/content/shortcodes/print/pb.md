---
title: print/pb
params:
  displayinlist: false
  metaPage: true
---

# print/pb

Page break for the print edition: emits `</div><div class="page">` to close the current page div and open the next one. Optionally renders the page's collected footnotes (partial `print/footnotes.html`) before the break.

## Parameters

| Parameter | Type | Required | Purpose |
|---|---|---|---|
| `footnotes` | any | no | If set, render the page's footnotes at this break |

## Example

```text
…end of the printed page.

{{</* print/pb footnotes="true" */>}}
