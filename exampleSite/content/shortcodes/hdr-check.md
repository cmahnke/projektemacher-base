---
title: hdr-check
displayinlist: false
metaPage: true
---

# hdr-check

Checks if the browser supports HDR and renders the result in a `<details>` element (collapsed by default, so it doesn't distract readers). For a canvas specific check see [`hdr-canvas-check`](../hdr-canvas-check/).

## Parameters

None.

## Example

```text
{{</* hdr-check */>}}
```

## Assets

Via the shortcode helper: TS `ts/shortcodes/hdr-check.ts` and SCSS `scss/shortcodes/hdr-check.scss`.

## Dependencies

| Package | Required mount |
|---|---|
| `@projektemacher/hdr-canvas` | – |
