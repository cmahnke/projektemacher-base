---
title: image-compare
params:
  displayinlist: false
  metaPage: true
---

# image-compare

Renders a before/after image comparison slider based on the [`img-comparison-slider`](https://img-comparison-slider.storyular.com/) Web Component. Both images are loaded as page bundle resources and resized to a 1280 px width.

## Parameters

| Parameter | Type | Required | Purpose |
| --- | --- | --- | --- |
| `image1` | string | yes | Page resource path of the first (before) image |
| `image2` | string | yes | Page resource path of the second (after) image |
| `caption1` | string | no | Caption and alt text for the first image |
| `caption2` | string | no | Caption and alt text for the second image |
| `format` | string | no | Output format of both images (e.g. `webp`), the source format is kept by default. Can also be configured site wide, see [image parameters](/config/params/#images) |

## Assets

Via the shortcode helper: JS `ts/image-compare.ts` (bundles the `img-comparison-slider` npm package), SCSS `scss/image-compare.scss`.
