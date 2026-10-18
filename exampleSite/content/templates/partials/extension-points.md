---
title: Extension points
displayinlist: false
metaPage: true
---

# Extension points

These partials are **not shipped with the theme** — the theme's templates call them, but each site is expected to provide them in its own `layouts/partials/`. The theme checks their existence and warns (or errors) if they are missing where required.

This example site implements all of them — see the [`_partials`](https://github.com/cmahnke/projektemacher-base/tree/main/exampleSite/layouts/_partials) and [`partials`](https://github.com/cmahnke/projektemacher-base/tree/main/exampleSite/layouts/partials) directories for a working reference.

## `li.html` (required for list pages)

Called for every page in [list templates](../single-list/) — it renders a single list entry. Place it in `layouts/_partials/li.html`.

- Input: the page
- If missing, the build emits `Missing li.html template` warnings and falls back to a plain `<a>` link
- See the example site's [`_partials/li.html`](https://github.com/cmahnke/projektemacher-base/blob/main/exampleSite/layouts/_partials/li.html)

## `article.html` (for the `html-body` template)

Called by the [`html-body` template](../single-list/#html-body) if a page has markdown content. A site provides it to render the content area of included HTML documents. Missing templates produce a warning.

Note: the theme checks the template with `templates.Exists "article.html"`, so the site needs both a marker template at `layouts/article.html` and the actual partial at `layouts/_partials/article.html` — see the example site.

## `print/toc-level.html` (required for print TOCs)

Called by the theme's `print/toc.html` partial to render a single level of the table of contents. Unlike the other extension points it is **not optional** — building a print edition with a TOC fails without it.

- Input: a dict with `entries` (list of pages), optional `level` and `maxLevels`

## `schema.org/*.html` (per type metadata)

The dispatcher `metadata/schema.org/schema.org.html` looks up a site partial for the current page in this order:

1. `schema.org/<schema>.html` — if the page has a `schema` front matter parameter
2. `schema.org/home.html` — on the home page
3. `schema.org/<section>.html` — for section pages
4. `schema.org/<kind>.html` — page kind (`page`, `section`, `term`, …) as fallback, then the section again

The theme ships `schema.org/home.html` and `schema.org/post.html`, a site can override them. Missing templates emit warnings only when [debug mode](helpers/#debug) is enabled. See [metadata partials](metadata-partials/).

## Optional partials (checked with `templates.Exists`)

| Partial | Called by | Purpose |
|---|---|---|
| `preview/image.html` | [preview rendering](helpers/#preview) | Site specific preview image resolution |
| `html/head/og-image-background.html` | `html/head/og-image.html` | Site specific OpenGraph background image |

## Overriding theme partials

Like any Hugo partial, all theme partials can be overridden by placing a file with the same path in the site's `layouts/partials/` directory — for example replacing `footer-content.html` with a site specific footer. The documented input/output contracts on the [category pages](.) apply.
