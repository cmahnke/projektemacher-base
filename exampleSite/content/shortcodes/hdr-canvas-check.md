---
title: hdr-canvas-check
displayinlist: false
metaPage: true
---

# hdr-canvas-check

Checks if the browser's canvas element supports HDR and renders the result in a `<details>` element (collapsed by default, so it doesn't distract readers).

## Parameters

None.

## Example

```text
{{</* hdr-canvas-check */>}}
```

## Assets

Via the shortcode helper: TS `ts/shortcodes/hdr-check.ts` and SCSS `scss/shortcodes/hdr-check.scss`.

## Dependencies

| Package | Required mount |
|---|---|
| `@projektemacher/hdr-canvas` | – |
