---
title: Print partials
displayinlist: false
metaPage: true
---

# Print partials

The `print/` partials are building blocks for print editions (books, brochures). They are used together with the [`baseof.print.html` template](../baseof/#print-variant), the print stylesheets and the [`print/*` shortcodes](/shortcodes/#print-edition). A consuming site assembles its own print template from them.

## `print/print-pages.html`

The main assembler: renders all pages of the site (via `hugo/site/AllPages`) in weight order as print pages. Requires a dict parameter:

| Parameter | Type | Default | Purpose |
|---|---|---|---|
| `context` | page | — | Current page context |
| `pages` | page list | all pages | Pages to render |
| `op` | string | `lt` | Weight comparison operator |
| `weight` | int | `10000` | Weight threshold — pages with a weight below it are rendered |

## `print/page.html`

Renders a single page as `<article class="singe-page" data-title="…">`. Input: the page.

## `print/blank.html`

Renders a blank page (e.g. as a spacer in a booklet). Requires `class` in the dict parameter, used for the CSS class.

## `print/toc.html`

Renders a table of contents. Optional dict parameter with `entries` (defaults to the current section's pages) and `maxLevels` (default `3`). Each level is rendered through the site provided [`print/toc-level.html` partial](../extension-points/#printtoc-levelhtml-required-for-print-tocs) — without it the build fails.

## `print/footnotes.html`

Renders the footnotes collected on a page (via the page's `footnotes` store key, filled by the [`footnote` shortcodes](/shortcodes/footnote/)). Also validates and rewrites punycode domain names in footnote URLs.

## `print/data-uri.html`

Converts a Hugo resource to a `data:` URI (base64 encoded), e.g. to inline images into print stylesheets. Warns if the input is not a resource.
