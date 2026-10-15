---
title: tagcloud
displayinlist: false
metaPage: true
---

# tagcloud

Renders a `div.tagcloud` of links for the site's `tags` taxonomy, sorted by count with a logarithmic font size between 12 and 48 px. Only tags used at least three times are shown; the terms `hugo`, `tags` and `rss` are excluded. Labels are `humanize`d with a count badge.

> This page documents the shortcode; see the [tag cloud demo](demo/tagcloud/) for a live example.

## Parameters

None.

## Example

```text
{{</* tagcloud */>}}
```

## Variants

[tags/cloud](tags-cloud/) is the customizable variant of this shortcode, rendering each label through partials.
