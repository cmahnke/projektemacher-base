---
title: Single and list templates
displayinlist: false
metaPage: true
---

# Single and list templates

## `_default/single.html`

Renders regular pages. It only fills the `title` and `content` blocks of the [base template](baseof/) and delegates the actual markup to the `page.html` partial, which renders:

- the page title as `h1.post-title`
- the page content, wrapped in a `div.post` with the `type` front matter parameter as additional CSS class
- date and tags footer — unless the page has `metaPage: true`

## `_default/list.html`

Renders section, taxonomy and term pages, as well as the home page. It delegates to the `list.html` partial, which:

- on the home page uses `.Site.RegularPages`, otherwise `.Pages`
- filters out pages with `metaPage: true`
- paginates the remaining pages (only pages with `displayinlist != false`)
- renders each page with a `li.html` partial — a site can override it by providing `layouts/_partials/li.html`, otherwise a warning is emitted and a plain link is rendered
- renders previous/next pagination links if there is more than one page

The home page uses the same template, it just feeds `.Site.RegularPages` into the same partial (see `partials/home.html`).

This documentation site overrides the template: on section pages with `toc: true` it renders the theme's [`toc.html` partial](/templates/partials/structural/#toc) as a sticky table of contents sidebar next to the section content. The theme itself renders no markup for the `toc` parameter — sites control the sidebar in their own layouts.

## `_default/html-body.html` {#html-body}

A standalone body template used to render raw HTML content, e.g. for the [`html/include` shortcode](/shortcodes/html/include/). It renders the site header and footer around:

- a container with a fullscreen button and the rendered HTML (via the `html/html-body.html` partial)
- optionally the page content, using an `article.html` partial (warns if it doesn't exist)

The container gets the classes `container include <section>`, where `<section>` is the page's section name.

## Front matter parameters

| Parameter | Type | Default | Purpose |
| --- | --- | --- | --- |
| `type` | string | — | Extra CSS class on the page wrapper |
| `metaPage` | bool | `false` | Hides the date/tags footer and excludes the page from lists |

## Example

A minimal page that behaves like a documentation page (no date, not listed):

```markdown
---
title: About
type: about
metaPage: true
---
```
