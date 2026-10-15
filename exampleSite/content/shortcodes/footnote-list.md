---
title: footnote-list
displayinlist: false
metaPage: true
---

# footnote-list

Renders the footnotes collected by [footnote](../footnote/) (stored in the page's store) as a `div.footnotes` with an ordered list, each entry carrying a back-reference (`↩︎`). Deletes the store afterwards — use it once per page, after the footnotes.

Renders nothing when no footnotes were collected.

## Parameters

None.

## Example

```text
Text with a note{{</* footnote 1 "The footnote text." */>}}.

…

{{</* footnote-list */>}}
```
