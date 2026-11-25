---
title: insta
params:
  displayinlist: false
  metaPage: true
---

# insta

Embeds an Instagram post via Instagram's official embed markup. The result is rendered through the [`html/iframe-consent`](html/iframe-consent/) wrapper, so the post and its `embeds.js` script are inserted only after the visitor accepts the external content notice.

## Parameters

| Parameter | Type | Required | Purpose |
|---|---|---|---|
| 0 (positional) | string | yes | Instagram post ID or a full URL starting with `http` |
| `caption` | named string | no | Replaces the caption Instagram extracts from the post; rendered with `class="instagram-caption"` |

An argument starting with `http` is used as-is; any other value is turned into `https://www.instagram.com/p/<id>/`. The resulting permalink gets the `utm_source=ig_embed&utm_campaign=loading` query parameters and is used both for `data-instgrm-permalink` and the fallback link.

Pass `caption` to replace the post's own caption with your own text. In that case Instagram's `data-instgrm-captioned` embedding is suppressed and the text is rendered next to the embed with `class="instagram-caption"`. Without a `caption`, the fallback link text is the hardcoded English `A post shared on Instagram`. Unlike the [`mastodon`](../mastodon/) shortcode, a missing positional argument does not abort the build — it produces a broken `https://www.instagram.com/p//` permalink instead.

## Examples

By post ID:

```text
{{</* insta "BsOGulcndj-" */>}}
```

By full URL, with a custom caption:

```text
{{</* insta "https://www.instagram.com/p/BsOGulcndj-/" caption="A post on Instagram" */>}}
```

## Live demo

Wraps a [public Instagram post](https://www.instagram.com/p/BsOGulcndj-/); accept the external content notice to load it:

{{< insta "BsOGulcndj-" >}}

## Notes

The consent overlay and toggle come from [`html/iframe-consent`](html/iframe-consent/). The required `ts/iframe-consent.ts` and `scss/iframe-consent.scss` assets are loaded automatically through the [shortcode helper system](shortcode-helper/).

For print/PDF output the caption is read from Instagram's embed HTML at build time and used as the figure caption. That extracted text is wrapped in `<span class="instagram-caption instagram-caption-extracted">`, so it can be styled independently of a caption supplied via the `caption` attribute.
