---
title: tags/cloud
params:
  displayinlist: false
  metaPage: true
---

# tags/cloud

The customizable variant of [tagcloud](../tagcloud/): same tag cloud logic, but each term label is rendered through a partial — `tagcloud/tag.html` by default, or `tagcloud/tag-<tag>.html` when the `tag` parameter is given. Available label partials include `tag-humanize.html`, `tag-i18n.html`, `tag-page.html` and `tag-replace-hyphen.html`.

Like `tagcloud`, only terms with a count ≥ 3 are shown (excluding `hugo`, `tags`, `rss`), with a logarithmic font size between 12 and 48 px.

## Parameters

| Parameter | Type | Required | Purpose |
|---|---|---|---|
| `tag` | string | no | Selects the label partial `tagcloud/tag-<tag>.html` |

## Example

```text
{{</* tags/cloud tag="i18n" */>}}
```
