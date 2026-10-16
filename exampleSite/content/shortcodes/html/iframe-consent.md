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

## Live demo

Wraps the embed of a [public Mastodon post](https://openbiblio.social/@cmahnke/116855467937850503) — the content only loads after accepting:

{{< html/iframe-consent >}}
<iframe src="https://openbiblio.social/@cmahnke/116855467937850503/embed" class="mastodon-embed" style="max-width: 100%; border: 0" width="400" title="Mastodon post"></iframe>
{{< /html/iframe-consent >}}

## Notes

The consent JavaScript and styles are loaded globally (`assets/ts/iframe-consent.ts`), not via shortcode metadata.
