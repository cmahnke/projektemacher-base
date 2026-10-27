---
title: Site parameters
description: "Reference of all site wide configuration options ([params]) understood by the theme's templates"
date: 2026-10-17
---

# Site parameters

All options are set in the site's `hugo.toml` under `[params]` (or `[params.<group>]` for grouped settings). Defaults are shown where the templates define one.

## General and metadata

| Parameter | Default | Purpose |
| --- | --- | --- |
| `description` | — | Site description, used for the `<meta name="description">` and OpenGraph tags |
| `keywords` | — | Comma separated keywords, rendered as `dc.subject` meta tags |
| `slogan` | — | Appended to the `<title>` on the home page |
| `author.name` / `author.email` / `author.uri` / `author.orcid` | — | Site author, used for metadata (schema.org, codemeta, RSS) |
| `publisher` | — | Publisher name for Linked Art / schema.org metadata |
| `useragent` | — | User agent string reported to external services (e.g. Wikidata SPARQL) |
| `robots.llmsTXT` | `false` | Generate a `llms.txt` file listing the site's content and author (see `robots.txt`) |
| `debug` | `false` | Enable the theme's debug warnings (extra build time output) |
| `env` | — | Environment name (e.g. `production`), used e.g. by the cookie consent service |
| `stylesheets` | — | List of external stylesheets to include in `<head>` |
| `disableOpenGraph` | `false` | Set to `true` to skip the OpenGraph meta tags in `<head>` |

## Header and footer

| Parameter | Default | Purpose |
| --- | --- | --- |
| `headerimage` | `/images/header.svg` | Logo image in the header; set to `false` to disable the image |
| `footer.privacy` | `false` | Show a privacy policy link (`footer.privacyUrl` overrides the default `/privacy` target) |
| `copyright` | — | Copyright line, rendered in the footer (set to `false` to hide) |
| `copyrightYears` | — | Year range prefixed to the copyright line |
| `cc` | `false` | Add a Creative Commons note to the footer |

## Assets and styles

| Parameter | Default | Purpose |
| --- | --- | --- |
| `js.format` | `iife` | Bundle format for all script bundles: `esm` ships each bundle as its own fingerprinted `<script type="module" crossorigin="anonymous">` tag (never concatenated), `iife` builds classic scripts and ships them concatenated with `defer`. Set via `[params.js]` or the string shorthand `[params] js = 'esm'` |
| `css.includeDirs` | built in set | Additional include paths (Sass `includePaths`) for the SCSS pipeline, see the [shortcode helper](/shortcodes/shortcode-helper/) |
| `skipShortcodeAssets` | `false` | Disable automatic loading of shortcode specific JS/CSS |
| `favicon_16` / `favicon_32` | — | Favicon PNGs |
| `favicon_svg` | — | Favicon SVG (modern browsers prefer it over the PNGs) |
| `favicon` | — | Fallback favicon (a single URL or a list of `rel`/`sizes`/`href` maps), only used when `favicon_16`/`favicon_32` are unset |
| `colorscheme` | — | `auto` or `dark` enables the theme's dark stylesheet |
| `custom_css` | — | List of stylesheet URLs to include in `<head>` |
| `custom_scss` | — | List of SCSS assets (below `assets/`) compiled to CSS |

## Images

The theme's image outputting shortcodes (`figure`, `gallery`,
`image-compare` and `post-image`) can emit images in a different format,
e.g. WebP. Each shortcode accepts a `format` parameter, sites can also
configure the output format globally or per shortcode:

```toml
[params.images]
  # format = 'webp' # global default for all image shortcodes

  [params.images.formats]
    gallery = 'webp'
    image-compare = 'webp'
    post-image = 'webp'
    figure = 'webp'
```

The global format can also be set as a string shorthand via
`[params] images = 'webp'`.

Resolution order (highest priority first):

1. The shortcode's `format` parameter
2. `images.formats.<shortcode name>`
3. `images.format` (global)
4. The shortcode's historical default (`gallery` keeps generating WebP, the others keep the image's source format)

The special value `original` (and an empty value) keeps the source format —
also per shortcode when a global format is configured. Accepted values are
Hugo's output formats `webp`, `avif`, `bmp`, `gif`, `jpeg`, `png` and
`tiff` (see [image processing](https://gohugo.io/content-management/image-processing/)).

Notes:

- Images Hugo can't process (e.g. SVG, JXL or HEIC sources) are passed
  through unchanged.
- `figure` can only convert page bundle resources — external URLs and
  static files keep their original format.
- Without `width`, `post-image` emits the unprocessed source resource; a
  configured format converts it even then.

## IIIF and viewers

All IIIF viewer settings live in `[params.iiif]` — see the [IIIF configuration](/iiif/configuration/) page for details:

| Parameter | Default | Purpose |
| --- | --- | --- |
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
| --- | --- | --- |
| `preview.source` | — | Site wide preview image source (OpenGraph/social cards) |
| `preview.size.width` / `preview.size.height` | — | Preview image dimensions |
| `preview.outputPrefix` / `preview.outputSuffix` | — | Output file naming for generated previews |
| `preview.background` | — | Background color for generated previews |
| `preview.og.format` | `jpeg` | Output format of the generated OpenGraph image (`webp` supported). When explicitly configured it is also applied to prerendered preview images and `ogpreview` resources — the implicit `jpeg` default leaves those untouched. Images Hugo can't process (e.g. SVG or JXL) pass through unchanged |

A site can further customize preview resolution via the `preview/image.html` partial, see [extension points](/templates/partials/extension-points/).

## Metadata integrations

| Parameter | Default | Purpose |
| --- | --- | --- |
| `wikidata` | `false` | Enable Wikidata metadata handling |
| `wikidatasparqlendpoint` | — | SPARQL endpoint for Wikidata queries |
| `schemaPerson` | — | URL to a JSON-LD person document for schema.org metadata |
| `orcid` | — | Author ORCID, used for the `rel="me"` link and metadata output; alternatively set as `author.orcid` |
| `logo` | — | Logo URL, also used for the error page image (`errorimg`) |

The `linkedart` parameter is a page level (front matter) switch that adds a
Linked Art output format to a page, see the [metadata formats](/templates/metadata-formats/) documentation.

## Print

| Parameter | Default | Purpose |
|---|---|---|
| `print.relative` | `false` | Use relative links in print editions |
