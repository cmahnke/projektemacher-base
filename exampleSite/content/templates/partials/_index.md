---
title: Partials
displayinlist: false
metaPage: true
toc: true
---

# Partials

The theme ships around 90 partials in `layouts/partials/`. They fall into three categories:

1. **Extension points** — partials the *site* is expected to provide, the theme only calls them (with a warning fallback), see [extension points](extension-points/)
2. **Reusable building blocks** — complete blocks (header, footer, viewers, …) that can be called from site layouts, several of them are already in use by sites built on this theme, see the [categorized pages](#pages) below
3. **Internal helpers** — small utilities used by the templates of this theme; they are listed below for completeness, but are not considered a public API

## Calling convention

Partials are referenced by their path below `partials/`, e.g. `{{ partial "header.html" . }}`. Some partials are **dispatched dynamically** by name — those double as a plug-in mechanism, see [plug-in dispatch](plugin-dispatch/).

The pages of this section are listed in the table of contents.

## Site parameters used by partials

| Parameter | Used by | Purpose |
|---|---|---|
| `headerimage` | [header.html](structural/#header) | Header logo image, `false` disables it |
| `slogan` | head.html | Appended to the `<title>` on the home page |
| `description`, `keywords` | html/head partials | Meta tags |
| `favicon`, `favicon_16`, `favicon_32`, `favicon_svg` | html/head/favicon.html | Favicons |
| `stylesheets` | head.html | External stylesheets |
| `css` | html/head/style.html | Additional stylesheet |
| `logo` | [404-content.html](structural/#404) | Error image |
| `errorimg` | [404-content.html](structural/#404) | Enable the error image |
| `preview` | [preview partials](helpers/#preview) | Prerendered preview images (`outputPrefix`, `outputSuffix`) |
| `iiif` | IIIF partials | IIIF configuration, e.g. `presentationVersion` |
| `productionIIIFURLPrefix` | [IIIF viewers](iiif-partials/) | URL prefix for manifests in production |
| `pdfDownload` | [IIIF presentation](iiif-partials/) | PDF download link |
| `minimalUI`, `disableScale` | [IIIF viewers](iiif-partials/) | Viewer behavior |
| `disableOpenGraph` | html/head/og-meta.html | Disable OpenGraph tags |
| `schemaPerson`, `publisher`, `orcid`, `author`, `authors` | [metadata partials](metadata-partials/) | Author and publisher data |
| `linkedart` | [Linked Art](metadata-partials/) | Linked Art configuration |
| `wikidatasparqlendpoint` | [data/wikidata.html](helpers/#wikidata) | SPARQL endpoint for label lookups |
| `debug` | [debug helpers](helpers/#debug) | Enable build warnings (`debug.enabled`) |
| `env` | [print partials](print-partials/) | Print edition environment |
| `skipShortcodeAssets` | [shortcode helper](helpers/#shortcode-helper) | Skip automatic asset loading |
| `copyright`, `copyrightYears`, `cc`, `footer.privacy`, `footer.privacyUrl` | [footer-content.html](structural/#footer) | Footer content |
| `robots.llmsTXT` | robots.txt | `llms.txt` reference, see [404 and robots](../404-robots/) |
| `print.relative` | baseof.print.html | Relative asset URLs for print output |

## Internal helpers (reference only)

These are used internally and not documented in detail: `functions/arrays/*`, `functions/debug/*`, `functions/files/*`, `functions/i18n/*`, `functions/tags/tag2str`, `functions/iiif/presentation-version.html`, `hugo/site/AllPages`, `metadata/linked-art/getty-label.json`, `metadata/linked-art/wikidata-label.json`, `geojson/feature*.geojson`, `iiif/3/*.json`, `iiif/4/manifest.json`, `html/head/*`, `js/type.html`, `macros/remove-shortcodes.txt`. Several of them are still usable from site layouts, see [helper partials](helpers/).

## See also

- [Templates](../) — page templates and output formats
- [Shortcodes](/shortcodes/) — markdown level building blocks
