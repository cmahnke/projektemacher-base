---
title: browser-hide-selector
displayinlist: false
metaPage: true
---

# browser-hide-selector

Emits an inline script calling `browserDisableSelector(selector, browsers)`: any DOM element matching `selector` is hidden or disabled for the listed browsers.

## Parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `selector` | string | no | `""` | CSS selector of the elements to hide |
| `browser` | string | no | — | Comma-separated list of browser names |

## Example

```text
{{</* browser-hide-selector selector=".webkit-only" browser="firefox" */>}}
```

## Assets

Via the shortcode helper: JS `js/browser-banner.js`, SCSS `scss/browser-banner.scss` (shared with [browser-banner](../browser-banner/)).
