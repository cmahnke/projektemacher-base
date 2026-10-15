---
title: Media type partials
displayinlist: false
metaPage: true
---

# Media type partials

The `media/` partials render description blocks for digitized media items (the output of the Projektemacher digitization projects). They are designed to be dispatched by the page's `type` front matter parameter from a site layout, e.g.:

```go-html-template
{{ partial (printf "media/%s.html" .Params.type) . }}
```

## Shared behavior

All media partials render a description block with a translated heading (`aboutTheNeu` + the item type) and the description body:

| Front matter parameter | Purpose |
|---|---|
| `itemDescription` | Item description, preferred |
| `description` | Fallback description |

Both are markdownified.

## `media/book.html`

Adds the `bookTitle` front matter parameter as heading and renders the page's `resources` named `front`, `title` or `cover` as [IIIF image viewers](iiif-partials/).

## `media/postcard.html`

Description block for postcards.

## `media/work.html`

Description block for generic cultural heritage works.

## `media/other.html`

Fallback for items that don't match the other types.
