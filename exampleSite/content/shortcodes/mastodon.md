---
title: mastodon
displayinlist: false
metaPage: true
---

# mastodon

Embeds a Mastodon post as an `<iframe class="mastodon-embed" src="<url>/embed">` (400 px wide). The official `embed.js` is loaded via the shortcode metadata.

## Parameters

Positional arguments:

| Position | Type | Required | Purpose |
|---|---|---|---|
| 0 | string | yes | URL of the Mastodon post |

## Example

```text
{{</* mastodon "https://mastodon.social/@user/1234567890" */>}}
```

## Errors

- `errorf "The %q shortcode requires a positional parameter: the url of the post…"` when the argument is missing
