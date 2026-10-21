---
title: browser-banner
params:
  displayinlist: false
  metaPage: true
---

# browser-banner

Renders a hidden banner that the `browserBanner()` JS function shows only when the visitor's browser matches one of the given names. The banner is attached to the element matching `parent` at runtime.

## Parameters

| Parameter | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `browser` | string | no | — | Comma-separated list of browser names (also used as CSS classes) |
| `class` | string | no | — | Additional classes |
| `style` | string | no | — | Additional inline styles |
| `parent` | string | no | `body` | CSS selector the banner is appended to |

The inner content is the banner text (markdownified).

## Example

```html
{{</* browser-banner browser="firefox" */>}}
This site works best in a Chromium based browser.
{{</* /browser-banner */>}}
```

## Live demo

Shows a banner for Firefox users only — visible when this page is opened in Firefox:

{{< browser-banner browser="firefox" >}}
This site works best in a Chromium based browser.
{{< /browser-banner >}}

## Assets

Via the shortcode helper: JS `ts/browser-banner.ts`, SCSS `scss/browser-banner.scss`.

See also [browser-hide-selector](../browser-hide-selector/).
