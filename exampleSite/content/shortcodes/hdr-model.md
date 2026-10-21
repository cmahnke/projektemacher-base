---
title: hdr-model
displayinlist: false
metaPage: true
---

# hdr-model

Renders a glTF/GLB model on a canvas using three.js with a HDR WebGPU renderer (falling back to WebGL) and orbit controls with auto-rotation. For an alternative implementation using A-Frame see [`aframe-3d-model`](../aframe-3d-model/), for the non HDR variant see [`model`](../model/).

On translated pages the model URL is prefixed with the default language's permalink.

## Parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `model` | string | yes | — | URL of the glTF/GLB model |

## Example

```text
{{</* hdr-model model="model/example.glb" */>}}
```

## Assets

Via the shortcode helper: TS `ts/shortcodes/hdr-model.ts` and SCSS `scss/shortcodes/hdr-model.scss`.

## Dependencies

| Package | Required mount |
| --- | --- |
| `three` | – |
| `@projektemacher/hdr-canvas` | – |
