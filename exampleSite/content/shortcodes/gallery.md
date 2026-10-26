---
title: gallery
params:
  displayinlist: false
  metaPage: true
---

# gallery

Renders an image gallery with a [PhotoSwipe](https://photoswipe.com/) lightbox. The shortcode body is a JSON array of image definitions; images are loaded as page resources. A small WebP preview is generated (`scalePreview` can turn this off), captions are hidden visually and shown in the lightbox.

Images with `.hdr.` in their filename link to the HDR image on the default language's page instead of opening the lightbox.

## Parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `class` | string | no | — | Extra class on the gallery `<div>` |
| `format` | string | no | `webp` | Output format of the full image and the previews (e.g. `webp`, `avif`, `jpeg`), `original` keeps the source format. Can also be configured site wide, see [image parameters](/config/params/#images) |

## Body (JSON array)

| Property | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `src` | string | yes | — | Page resource path of the image |
| `alt` | string | no | `""` | Image alt text and lightbox caption (also used for `aria-label`) |
| `scalePreview` | bool | no | `true` | Generate a resized WebP preview |

## Example

```text
{{</* gallery >}}
[
  { "src": "image-1.jpg", "alt": "First image" },
  { "src": "image-2.jpg", "alt": "Second image", "scalePreview": false }
]
{{< /gallery */>}}
```

## Assets

Via the shortcode helper: JS `ts/shortcodes/gallery.ts`, SCSS `scss/shortcodes/gallery.scss` and the PhotoSwipe stylesheet.

## Dependencies

| Package | Required mount |
|---|---|
| `photoswipe` | `source = "node_modules/photoswipe/dist"`, `target = "assets/css/photoswipe"` |
