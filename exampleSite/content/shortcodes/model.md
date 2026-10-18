---
title: model
displayinlist: false
metaPage: true
---

# model

Renders a glTF/GLB model on a canvas using three.js with orbit controls, auto-rotation and an optional halftone postprocessing effect. For the HDR/WebGPU variant see [`hdr-model`](../hdr-model/), for the A-Frame variant see [`aframe-3d-model`](../aframe-3d-model/).

The canvas is exposed to assistive technology with `role="img"` and a localized `aria-label`.

## Parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `model` | string | yes | — | URL of the glTF/GLB model |

## Example

```text
{{</* model model="model/example.glb" */>}}
```

## Assets

Via the shortcode helper: TS `ts/shortcodes/model.ts`, SCSS `scss/shortcodes/model.scss`.

## Dependencies

| Package | Required mount |
|---|---|
| `three` | – |
