---
title: Structural partials
displayinlist: false
metaPage: true
---

# Structural partials

These partials render the common page chrome. They are used by the theme's templates and can be called (or overridden) by sites — the consuming sites `projektemacher.org` and `labs.projektemacher.org` call most of them from their own layouts.

## `head.html` {#head}

Renders parts of the `<head>` content: title, meta description, external `stylesheets`, favicons and `<link>` alternates for the RSS and `iiif-collection` output formats. It no longer renders stylesheets or the JavaScript bundle — those come from the `html/head/style.html` and `html/head/script.html` partials (see below), which `baseof.html` calls directly.

> **Warning:** this partial emits a build warning — it is incomplete compared to the `html/head/*` partials. Use those individually instead.

| Site parameter | Purpose |
|---|---|
| `slogan` | Appended to the title on the home page |
| `description` | Fallback meta description |
| `stylesheets` | List of external stylesheet URLs |
| `favicon_16`, `favicon_32`, `favicon_svg` | Favicons |

## `html/head/script.html` {#html-head-script}

Builds and links the site's JavaScript. The entry point is the page parameter `defaultScriptEntrypoint` if set; otherwise a `ts/main.ts` resource is used when present, falling back to the legacy `js/main.js` name. If neither exists the build fails with an `errorf` — create the file in the site's assets directory, an empty file will do (the example site ships an empty `assets/ts/main.ts`). Additional per page scripts come from the page's `js:` front matter and from the shortcode helper metadata; they are bundled separately from the main bundle.

## `header.html` {#header}

Renders the site header: the [menu](#menu), the header image and the page title (with the `subtitle` page parameter as `h2`).

| Site parameter | Purpose |
|---|---|
| `headerimage` | Header image path, defaults to `/images/header.svg`, `false` disables the image |

## `menu.html` {#menu}

Renders the main navigation: all `.Site.Menus.main` entries (with `draft` menu params honored, HTML menu entries via `params.html = true`, see [menu configuration](/config/menu/)) plus the language switcher for multilingual sites (`label` from the language configuration). Entries pointing to the current section get a `current` CSS class.

## `topnavigation.html` {#topnavigation}

Placeholder container above the header, empty by default — a site can override it.

## `footer.html` and `footer-content.html` {#footer}

`footer.html` renders the main menu as footer navigation plus the footer content. `footer-content.html` renders the copyright block:

| Site parameter (default site) | Purpose |
|---|---|
| `copyright` | Custom copyright text |
| `copyrightYears` | Custom year range, prepends `©` |
| `copyright: "false"` | Renders an empty copyright |
| `cc: true` | Adds the Creative Commons note |
| `footer.privacy: true` | Adds a privacy policy link |
| `footer.privacyUrl` | Alternative privacy URL (default `/privacy`) |

The page Scratch key `footer` can hold HTML that is appended to the footer.

## `404.html` and `404-content.html` {#404}

`404.html` wraps the base template, `404-content.html` renders the error text and — with the site parameters `errorimg: true` and `logo` — an error image.

## `list.html` and `home.html` {#list}

`list.html` renders a paginated page list: filters `metaPage` pages, keeps pages with `displayinlist != false`, renders each with the site's [`li.html`](extension-points/#lihtml-required-for-list-pages) partial, then pagination links via `pagination.html`. `home.html` is a thin wrapper feeding `.Site.RegularPages` into the same markup.

## `pagination.html` {#pagination}

Renders previous/next pagination links with i18n labels.

## `page.html` {#page}

Renders a single page: title, content and — unless `metaPage: true` — the date and [tags](#tags) footer. The `type` front matter parameter becomes an additional CSS class.

## `toc.html` {#toc}

Renders a table of contents for a section page — a list of the section's child pages. The example site places it as a sticky sidebar next to the section content (via its `list.html` override), but it can be called from any layout:

```go-html-template
{{ partial "toc.html" (dict "entries" . "maxLevels" 2) }}
```

| Parameter | Purpose |
|---|---|
| `entries` | A section page — its children are rendered; a page slice is rendered as a flat list without grouping |
| `maxLevels` | Number of levels to render, counting the top level (default `2`; `3` also renders the children of nested sections, child sections are always rendered without their children once the level is exhausted) |
| `title` | Heading above the list (defaults to the `inThisSection` i18n string) |

Pages with the front matter parameter `tocExclude: true` are skipped. Pages stored directly in the section root and child sections are top level entries; pages in subdirectories without their own `_index.md` are grouped under the directory name — e.g. the `shortcodes/html/` pages become an `html` group on the `/shortcodes/` section. A subdirectory holding only one page is promoted to a top level entry. The partial emits an `<aside class="section-toc">` with a `<nav class="toc">` inside; it renders nothing when no entries remain after filtering. A site can ship its own version through `layouts/partials/toc.html`.

## `html/html-body.html` {#html-body}

Renders the body of a standalone HTML page, used by the [`html-body` template](../single-list/#html-body) and the [`html/include` shortcode](/shortcodes/html/include/).

## `meta/tags.html` and `meta/i18n-tags.html` {#tags}

Both render the tag list of a page as links to the `tags/` terms:

- `meta/tags.html` renders each tag through the [tag cloud plug-ins](../plugin-dispatch/#tag-cloud) — the page parameter `render` selects the variant (default `tag`)
- `meta/i18n-tags.html` renders the tags through `i18n` translations instead

## `post-relations.html` {#post-relations}

Renders contextual navigation for a page: on section pages a list of the section's pages, on regular pages a link to the parent section. Skipped for `metaPage` pages.
