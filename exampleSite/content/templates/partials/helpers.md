---
title: Helper partials
params:
  displayinlist: false
  metaPage: true
---

# Helper partials

Utility partials — most of them return a value and are used like functions. They can be called from site layouts, too.

## Functions (`functions/`)

| Partial | Purpose |
| --- | --- |
| `functions/arrays/filter-nil.html` | Removes `nil` entries from a slice (input: `slice`) |
| `functions/arrays/join.html` | Joins a string slice (input: `slice`, optional `separator`) |
| `functions/arrays/reverse-slice.html` | Reverses a slice |
| `functions/files/slice-filter-non-existing.html` | Filters missing resources out of a file list (input: `files`, `context`) |
| `functions/inline-svg.html` | Inlines an SVG file (`svg` = path) as HTML, errors if the file is missing |
| `functions/debug/enabled.html` {#debug} | Returns the debug flag from the site parameter `debug` (memoized via `partialCached`) — used to guard extra build warnings |
| `functions/debug/var.html` | Debug dumps a variable with `printf "%#v"` |
| `functions/i18n/default-lang` | Returns the default site language name |
| `functions/i18n/page-for-lang.html` | Returns a page's translation for a language (input: `context`, `lang`) |
| `functions/i18n/site-langs` | Returns all configured site languages |
| `functions/tags/tag2str` | Normalizes tag input (string, `Term` or taxonomy entry) to a string |
| `functions/iiif/presentation-version.html` | Resolves the [IIIF Presentation version](../iiif-templates/#presentation-api-version) for a page |
| `hugo/site/AllPages` | All pages of all sites, multilingual aware — workaround for Hugo's `.Site.AllPages` behavior |

## Data lookups {#wikidata}

- `data/wikidata.html` — renders a "Wikidata entries" summary block for a page: reads the `wikidata` front matter (string, list or map with relations), resolves the entity labels through `data/functions/wikidata-label.html` and links them. The label lookup uses the Wikidata EntityData JSON API, not SPARQL

## Services {#services}

- `services/cookie-consent.html` — renders a cookie consent notice with accept/deny buttons (i18n labels, optional privacy policy `link` in the dict input). Currently not wired into the theme — a site includes it and pairs it with the `html/head/dnt-cookie.html` partial and its analytics scripts

## Preview images {#preview}

- `preview/prerendered.html` — finds a prerendered preview image for a page using the site parameter `preview` (`outputPrefix`, `outputSuffix`, language specific variants)
- `preview/preview-internal.html` — internal preview rendering (image processing), input: `context`, `fit`, optional `postProcess`
- `preview/image.html` — optional [site extension point](extension-points/)

## Shortcode assets {#shortcode-helper}

- `shortcodes/shortcode-helper.html` — the core of the [shortcode helper system](/shortcodes/shortcode-helper/): checks which shortcodes a page uses and returns a JSON map of the JS/CSS/SCSS assets they need. The site parameter `skipShortcodeAssets: true` disables it
- `shortcodes/shortcode-helper-cache.html` / `-extract-matches.html` — build the include cache from the asset manifests
- `shortcodes/mermaid/block.html` — renders a Mermaid diagram block for the [`mermaid` shortcode](/shortcodes/mermaid/)

## Miscellaneous

- `html/comment.html` — renders a string as an HTML comment
- `macros/strip-links.html` — returns a page's content as plain text
- `macros/remove-shortcodes.txt` — strips shortcode markers from raw content (used by the GeoJSON popups)
- `fonts/css.html` — publishes font CSS resources (`assets/css/fonts/*.css`); currently emits a build warning, work in progress — see the [font infrastructure note](https://github.com/cmahnke/projektemacher-base#todo) in the README
- `pdf-viewer.html` — renders a PDF viewer for a page resource named `pdf-viewer` (used by the [`pdf` shortcodes](/shortcodes/pdf/)) plus a download link
- `geojson/feature.geojson`, `featureCollection.geojson` — GeoJSON assembly, see [GeoJSON template](../geojson/)
