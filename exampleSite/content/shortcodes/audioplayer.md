---
title: audioplayer
displayinlist: false
metaPage: true
---

# audioplayer

Renders an audio player placeholder (`div.audioplayer` with a play button) initialized by the `audioplayer()` JS function.

> Note: this shortcode is marked *untested* — the build logs a `warnf` whenever it is used.

## Parameters

| Parameter | Type | Required | Purpose |
|---|---|---|---|
| `src` | string | yes | Audio file URL, passed to the JS player |
| `autoplay` | bool | no | Read but currently unused by the template |

## Example

```text
{{</* audioplayer src="audio/recording.mp3" */>}}
```

## Assets

Via the shortcode helper: JS `js/audioplayer.js`, SCSS `scss/audioplayer.scss`.
