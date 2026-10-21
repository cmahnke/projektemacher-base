---
title: post-image
displayinlist: false
metaPage: true
---

# post-image

Renders the first image from another post's front matter `resources` array as a `<figure>`. Useful for teaser images that should stay in sync with the original post.

## Parameters

| Parameter | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `post` | string | yes | — | Path of the post (relative to `section` if given) |
| `section` | string | no | — | Section to look up the post in |
| `width` | string | no | — | Resize the image to the given width |
| `link` | string | no | — | Wrap the image in `<a href>` |
| `caption` | string | no | — | Figure caption, also used as image `alt` (falls back to the post title) |
| `class` | string | no | — | Class on the `<figure>` |

## Example

```text
{{</* post-image section="posts" post="my-post" caption="Teaser image" width="320" */>}}
```

## Assets

None.
