---
title: Site parameters
description: "Reference of all site wide configuration options ([params]) understood by the theme's templates"
date: 2026-10-17
---

# Site parameters

All options are set in the site's `hugo.toml` under `[params]` (or `[params.<group>]` for grouped settings). Defaults are shown where the templates define one.

## General and metadata

| Parameter | Default | Purpose |
|---|---|---|
| `description` | — | Site description, used for the `<meta name="description">` and OpenGraph tags |
| `keywords` | — | Comma separated keywords, rendered as `dc.subject` meta tags |
| `slogan` | — | Appended to the `<title>` on the home page |
| `author.name` / `author.email` / `author.uri` | — | Site author, used for metadata (schema.org, codemeta, RSS) |
| `publisher` | — | Publisher name for Linked Art / schema.org metadata |
| `useragent` | — | User agent string reported to external services (e.g. Wikidata SPARQL) |
| `robots.llmsTXT` | `false` | Generate a `llms.txt` file listing the site's content (see `robots.txt`) |
| `debug` | `false` | Enable the theme's debug warnings (extra build time output) |
| `env` | — | Environment name (e.g. `production`), used e.g. by the cookie consent service |
| `stylesheets` | — | List of external stylesheets to include in `<head>` |

## Header and footer

| Parameter | Default | Purpose |
|---|---|---|
| `headerimage` | `/images/header.svg` | Logo image in the header; set to `false` to disable the image |
| `footer.privacy` | `false` | Show a privacy policy link (`footer.privacyUrl` overrides the default `/privacy` target) |
| `copyright` | — | Copyright line, rendered in the footer (set to `false` to hide) |
| `copyrightYears` | — | Year range prefixed to the copyright line |
| `cc` | `false` | Add a Creative Commons note to the footer |

## Assets and styles

| Parameter | Default | Purpose |
|---|---|---|
| `css.includeDirs` | built in set | Additional include paths (Sass `includePaths`) for the SCSS pipeline, see the [shortcode helper](/shortcodes/shortcode-helper/) |
| `skipShortcodeAssets` | `false` | Disable automatic loading of shortcode specific JS/CSS |
| `favicon_16` / `favicon_32` | — | Favicon PNGs |
| `favicon_svg` | — | Favicon SVG (modern browsers prefer it over the PNGs) |

## IIIF and viewers

All IIIF viewer settings live in `[params.iiif]` — see the [IIIF configuration](/iiif/configuration/) page for details:

| Parameter | Default | Purpose |
|---|---|---|
| `iiif.presentationViewer` | `ts/iiif/tify.ts` | Presentation API viewer script (TIFY) |
| `iiif.imageViewer` | — | Image API viewer script (OpenLayers based) |
| `minimalUI` | `false` | Minimal viewer UI |
| `pdfDownload` | `false` | Add a PDF download link to the presentation viewer |
| `productionIIIFURLPrefix` | — | URL prefix for IIIF images in production builds |

The former `disableScale` parameter has been removed and has no effect:
pinch zoom-in must stay allowed for accessibility (WCAG 2.5.5), only
zoom-out is blocked via the viewport's `minimum-scale=1.0`. Setting it
is a silent no-op (Hugo ignores unknown params).

## Previews

| Parameter | Default | Purpose |
|---|---|---|
| `preview.source` | — | Site wide preview image source (OpenGraph/social cards) |
| `preview.size.width` / `preview.size.height` | — | Preview image dimensions |
| `preview.outputPrefix` / `preview.outputSuffix` | — | Output file naming for generated previews |
| `preview.background` | — | Background color for generated previews |

A site can further customize preview resolution via the `preview/image.html` partial, see [extension points](/templates/partials/extension-points/).

## Metadata integrations

| Parameter | Default | Purpose |
|---|---|---|
| `wikidata` | `false` | Enable Wikidata metadata handling |
| `wikidatasparqlendpoint` | — | SPARQL endpoint for Wikidata queries |
| `schemaPerson` | — | URL to a JSON-LD person document for schema.org metadata |
| `orcid` | — | Author ORCID, used in metadata output |
| `logo` | — | Logo URL, also used for the error page image (`errorimg`) |

The `linkedart` parameter is a page level (front matter) switch that adds a
Linked Art output format to a page, see the [metadata formats](/templates/metadata-formats/) documentation.

## Print

| Parameter | Default | Purpose |
|---|---|---|
| `print.relative` | `false` | Use relative links in print editions |
