---
title: aframe-3d-model
displayinlist: false
metaPage: true
---

# aframe-3d-model

Embeds an [A-Frame](https://aframe.io/) `<a-scene>` (WebXR enabled) that loads a glTF/GLB model with orbit controls, auto-rotation and damping.

## Parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `src` | string | yes | — | URL of the glTF/GLB model |
| `class` | string | no | `aframe-3d-model` | Custom class on the wrapper |
| `style` | string | no | — | Inline CSS for the wrapper |
| `autorotate` | bool | no | `true` | Auto-rotate the model |
| `minDistance` | int | no | `2` | Orbit controls minimum distance |
| `maxDistance` | int | no | `10` | Orbit controls maximum distance |
| `initialPosition` | string | no | `0 0.5 4` | Initial camera position |
| `xrMode` | bool | no | `true` | Enable the WebXR mode UI |

## Example

```text
{{</* aframe-3d-model src="/models/example.glb" maxDistance="20" */>}}
```

## Live demo

Loads the example model from the [3D model manifest post](/posts/3d-model/):

{{< aframe-3d-model src="/posts/3d-model/model/example.glb" maxDistance="20" >}}

## Assets

Via the shortcode helper: JS `ts/aframe.ts` (bundles the `aframe` ^1.8.0 and `aframe-orbit-controls` ^1.3.2 npm packages), SCSS `scss/3d/3d-model.scss`.
