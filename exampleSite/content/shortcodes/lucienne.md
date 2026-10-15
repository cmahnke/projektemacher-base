---
title: lucienne
displayinlist: false
metaPage: true
---

# lucienne

Embeds the [Lucienne](https://github.com/projektemacher/lucienne) IIIF playground viewer (`div.lucienne-container`), initialized with an IIIF source URL — optionally overridden by a `?url=` query parameter. Lucienne offers a URL input, resizing, download and shift navigation.

## Parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `src` | string | yes | — | Initial IIIF source URL (`errorf` when missing) |
| `class` | string | no | — | Currently read but not emitted |
| `urlinput` / `urlInput` | bool | no | `false` | Show the URL input field |
| `resize` | bool | no | `true` | Allow resizing |
| `download` | bool | no | `true` | Show download option |
| `useLocation` / `uselocation` | bool | no | `false` | Sync with the browser location (note the case sensitivity quirk between the two spellings) |
| `autoLoad` | bool | no | `true` | Load the initial source automatically |
| `shifts` | bool | no | `false` | Enable shift navigation |

## Example

```text
{{</* lucienne src="https://iiif.example.org/manifest.json" urlinput="true" */>}}
```

## Assets

Via the shortcode helper: JS `js/lucienne/lucienne.js`, SCSS `scss/lucienne/lucienne.css`.

## Errors

- `errorf "The %q shortcode requires an (initial) IIIF source"` when `src` is missing or empty
