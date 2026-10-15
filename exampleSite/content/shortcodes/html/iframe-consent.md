---
title: html/iframe-consent
displayinlist: false
metaPage: true
---

# html/iframe-consent

GDPR consent wrapper for embedded iframes: renders an overlay ("external content" notice via i18n `externalContent`/`externalContentDescription`) with a toggle switch (i18n `accept`). Accepting stores a consent cookie (30 days, keyed by an md5 of the iframe markup) and loads the iframe — until then only the optional preview is shown.

## Parameters

| Parameter | Type | Required | Purpose |
|---|---|---|---|
| `preview` | string | no | HTML (e.g. an image) shown on the overlay before consent |

The inner content is the `<iframe>` markup (passed through `safeHTML`).

## Example

```html
{{</* html/iframe-consent */>}}
<iframe src="https://www.youtube-nocookie.com/embed/xyz" allowfullscreen></iframe>
{{</* /html/iframe-consent */>}}
```

## Notes

The consent JavaScript and styles are loaded globally (`assets/js/iframe-consent.js`), not via shortcode metadata.
