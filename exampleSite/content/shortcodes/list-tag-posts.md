---
title: list-tag-posts
params:
  displayinlist: false
  metaPage: true
---

# list-tag-posts

Renders a `ul.tagged-posts` list of pages from a section carrying the given tag(s). When multiple tags are given (via `tags`), all of them must match. The current page is excluded.

## Parameters

| Parameter | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `tag` | string | no | — | Single tag to match |
| `tags` | string | no | — | Comma-separated tag list, overrides `tag` |
| `section` | string | no | `post` | Section to search |

## Example

```text
{{</* list-tag-posts tag="iiif" section="post" */>}}
```

See also the [tag cloud demo](../demo/tagcloud/) for tag related demos.
