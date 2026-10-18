---
title: hdr-canvas
displayinlist: false
metaPage: true
---

# hdr-canvas

Renders an image on a HDR capable canvas with red/green/blue channel sliders for colour manipulation. Requires a browser with HDR canvas support; on unsupported browsers a hidden fallback message is shown to screen readers and the image is displayed as SDR.

## Parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `image` | string | yes | — | URL of the image to load |

## Example

```text
{{</* hdr-canvas image="image.avif" */>}}
```

## Assets

Via the shortcode helper: TS `ts/shortcodes/image-slider.ts` and SCSS `scss/shortcodes/slider-canvas.scss`.

## Dependencies

| Package | Required mount |
|---|---|
| `@projektemacher/hdr-canvas` | – |
