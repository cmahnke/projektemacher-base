---
title: Templates
params:
  displayinlist: false
  metaPage: true
  toc: true
---

# Templates

This theme ships a set of Hugo templates in `layouts/`. This section documents the page templates and the templates for custom [output formats](https://gohugo.io/configuration/output-formats/) — JSON metadata, IIIF, QR codes, GeoJSON and more.

Not covered here:

- **Shortcodes** have their own section, see [Shortcodes](/shortcodes/)
- **Partials** have their own subsection — a mix of [extension points for sites](partials/extension-points/), [reusable building blocks](partials/) and internal helpers, see the [partials overview](partials/)

## Base and page templates

| Template | Purpose |
| --- | --- |
| [`_default/baseof.html`](baseof/) | Base template with header, navigation and footer, defines the `title`, `body`, `main` and `content` blocks |
| `_default/baseof.print.html` | Base template for the print output, pulls in `print.scss`/`print.js` |
| [`_default/single.html`](single-list/) | Regular pages, delegates to the `page.html` partial |
| [`_default/list.html`](single-list/) | Section, term and home pages with pagination |
| [`_default/html-body.html`](single-list/#html-body) | Standalone HTML body rendering (used by the [`html/include` shortcode](/shortcodes/html/include/)) |
| [`search.html`](search/) | Search page (Pagefind) |
| [`404.html`](404-robots/) | Error page |

## Output formats

These templates are selected via the `outputs` front matter or the site `outputs` configuration:

| Output format | Template | Purpose |
| --- | --- | --- |
| HTML (default) | `single.html`, `list.html`, … | Regular pages |
| [`qrcode`](qrcode/) | `single.qrcode.json`, `section.qrcode.json` | QR code generation data |
| [`iiif-manifest`](iiif-templates/) | `single.iiif-manifest.json`, `section.iiif-manifest.json` | IIIF Presentation manifests |
| [`iiif-collection`](iiif-templates/) | `home.iiif-collection.json`, `term.iiif-collection.json` | IIIF Presentation collections |
| [`geojson`](geojson/) | `section.geojson` | GeoJSON feature collections |
| [`codemeta`](metadata-formats/) | `single.codemeta.json` | CodeMeta software metadata |
| [`linkedart`](metadata-formats/) | `single.linkedart.json`, `linked-art-collection.json` | Linked Art metadata |
| `schemaorg` | [`schema-org.json`](metadata-formats/#schemaorg) | schema.org JSON-LD |
| [`bibtex`](bibtex/) | `single.bib` (reference site only) | BibTeX citation export |
| [`pdf-article`](pdf-article/) | `single.pdf-article.html`, `baseof.pdf-article.html` (reference site only) | Printable article variant for PDF generation |
| [`activity-pub-actor`](activity-pub-actor/) | `single.activity-pub-actor.json` (reference site only) | ActivityStreams actor |
| [`activity-pub-outbox`](activity-pub-outbox/) | `home.activity-pub-outbox.json` (reference site only) | ActivityStreams outbox collection |
| [`llms`](llms/) | no page template — see `llms.txt` note | Placeholder plain-text format |
| [`redirect`](redirect/) | `redirect/single.html` | Meta refresh redirects |

## Data templates

The theme generates additional data files for client side search and indexing:

- [`post-list.json`, `tag-list.json`, `wikidata-list.json`](data-lists/) — page and tag indexes used by the search and relation features
- [`robots.txt`](404-robots/) — with `Disallow` rules and optional `llms.txt` reference
- [`sitemap.xml`](404-robots/) — with hreflang alternates

## Front matter parameters

The templates rely on the following page parameters. Most of them control in- or exclusion from listings, so they default to including a page:

| Parameter | Type | Default | Purpose |
| --- | --- | --- | --- |
| `metaPage` | bool | `false` | Marks documentation/meta pages: hides date and tags, adds the `meta` CSS class and excludes the page from lists, RSS and `post-list.json` |
| `displayinlist` | bool | `true` | Set to `false` to exclude a page from list pagination, `post-list.json`, `tag-list.json`, `wikidata-list.json`, RSS, schema.org output and IIIF collections |
| `type` | string | — | CSS class for the page wrapper (`page.html`); on the section used with the `schemaorg` output format it sets the blog `@type` |
| `robotsdisallow` | bool | `false` | Adds a `Disallow` entry to `robots.txt` |
| `sitemap_exclude` | bool | `false` | Adds a `Disallow` entry to `robots.txt` |
| `aliases` | string list | — | Additional URLs (QR codes render them as an array) |
| `outputs` | string list | `["HTML"]` | Output formats for the page, see the table above |
| `wikidata` | string or list | — | Wikidata entity URI(s), used by the Wikidata index |
| `news` | bool | `true` | Set to `false` to remove a page from `sitemap.xml` |
| `archive` | bool | `true` | Set to `false` to remove a page from `sitemap.xml` |

The example site additionally uses the `toc` parameter to enable the [table of contents sidebar](/templates/partials/structural/#toc) on section pages.

## See also

- [Shortcodes](/shortcodes/) — markdown level building blocks
- [IIIF](/iiif/) — IIIF configuration and front matter reference
- [Site params](/posts/site-params/) — site configuration overview
- [Menu configuration](/config/menu/)
