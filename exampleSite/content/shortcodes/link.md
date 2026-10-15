---
title: link
displayinlist: false
metaPage: true
---

# link

Renders an `<a>` element around the inner content. External URLs (starting `http` or `//` and not pointing at the site BaseURL) automatically get the class `external` and `target="_blank"`.

An internal link: {{< link link="/shortcodes/" >}}to the shortcode section{{< /link >}}. An external one: {{< link link="https://iiif.io/" >}}IIIF{{< /link >}}.

## Parameters

| Parameter | Type | Required | Purpose |
|---|---|---|---|
| `link` | string | no | Href value (without it the `<a>` has no href) |
| `title` | string | no | Title attribute |
| `class` | string | no | Additional classes (merged with `external`) |

The inner content is the link text.

## Example

```text
See {{</* link link="https://iiif.io/" */>}}the IIIF website{{</* /link */>}}.
```
