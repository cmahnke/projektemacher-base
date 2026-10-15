---
title: print/ref
displayinlist: false
metaPage: true
---

# print/ref

Cross-reference for the print edition: renders `<a class="page-ref" href="#_-<section>-<slug>">` pointing to the anchor of another page printed in the same document. The link text is the referenced page's title (or its description as fallback), a custom string, or just the page abbreviation (i18n `pageAbbr`), suffixed with the page abbreviation.

## Parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `slug` | string | yes | — | Slug of the target page below `section` |
| `section` | string | no | `post` | Section of the target page |
| `title` | bool/string | no | — | `true` uses the target's title/description; a string is used verbatim; omitted → only the page abbreviation |

## Example

```text
See {{</* print/ref slug="introduction" title="true" */>}} for details.
```

## Errors

- `errorf "[print-ref.html] No argument given in <page>"` when `slug` is empty
