---
title: browser-hide-selector
params:
  displayinlist: false
  metaPage: true
---

# browser-hide-selector

Emits an inline script calling `browserDisableSelector(selector, browsers)`: any DOM element matching `selector` is hidden or disabled for the listed browsers.

## Parameters

| Parameter | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `selector` | string | no | `""` | CSS selector of the elements to hide |
| `browser` | string | no | — | Comma-separated list of browser names |

## Example

```text
{{</* browser-hide-selector selector=".webkit-only" browser="firefox" */>}}
```

## Live demo

The second paragraph below is hidden in Firefox (and shown elsewhere) via the `webkit-only` selector:

<div class="webkit-only">This paragraph is hidden when visiting with Firefox.</div>

{{< browser-hide-selector selector=".webkit-only" browser="firefox" >}}

## Assets

Via the shortcode helper: JS `ts/browser-banner.ts`, SCSS `scss/browser-banner.scss` (shared with [browser-banner](../browser-banner/)).
