---
title: Structural partials
displayinlist: false
metaPage: true
---

# Structural partials

These partials render the common page chrome. They are used by the theme's templates and can be called (or overridden) by sites — the consuming sites `projektemacher.org` and `labs.projektemacher.org` call most of them from their own layouts.

## ~~`head.html`~~ {#head}

The legacy `head.html` partial has been removed. It rendered only meta tags, favicons and `<link>` alternates — everything it did is now covered by the `html/head/meta.html` and `html/head/links.html` partials (see below), which `baseof.html` calls directly. Sites that still keep a copy of `head.html` are unaffected (their copy shadows the theme), but should migrate to the `html/head/*` partials.

## `html/head/title.html` {#html-head-title}

Renders the `<title>` element: the page title, appended with the [`slogan`](../#site-parameters-used-by-partials) on the home page. The `title` block inside can be overridden by site templates (see [base template](../../baseof/#blocks)) — `single.html`, `list.html` and `search.html` use this to render `Title · site.Title`. Pages without a title render no `<title>` element.

## `html/head/links.html` {#html-head-links}

Emits the `<head>` link tags that are not meta data: external `stylesheets`, the font CSS (see [fonts](/posts/)), and the `<link>` alternates for the RSS and `iiif-collection` output formats. Called by `baseof.html` after `html/head/meta.html`.

The `<title>` (with the `slogan` site parameter appended on the home page) is emitted by the [`html/head/title.html`](#html-head-title) partial.

## `html/head/viewport.html` {#html-head-viewport}

Emits the `<meta name="viewport">` tag: `width=device-width, initial-scale=1.0, minimum-scale=1.0` — pinch zoom-in stays allowed (accessibility), only zoom-out is blocked. The `minimalUI` site parameter appends `minimal-ui`.

## `html/head/script.html` {#html-head-script}

Builds and links the site's JavaScript. The entry point is the page parameter `defaultScriptEntrypoint` if set; otherwise a `ts/main.ts` resource is used when present, falling back to the legacy `js/main.js` name. If neither exists the build fails with an `errorf` — create the file in the site's assets directory, an empty file will do (the example site ships an empty `assets/ts/main.ts`). Additional per page scripts come from the page's `js:` front matter and from the shortcode helper metadata; they are bundled separately from the main bundle.

## `header.html` {#header}

Renders the site header: the [menu](#menu), the header image and the page title (with the `subtitle` page parameter as `h2`).

| Site parameter | Purpose |
|---|---|
| `headerimage` | Header image path, defaults to `/images/header.svg`, `false` disables the image |

## `menu.html` {#menu}

Renders the main navigation: all `.Site.Menus.main` entries (with `draft` menu params honored, HTML menu entries via `params.html = true`, see [menu configuration](/config/menu/)) plus the language switcher for multilingual sites (`label` from the language configuration). Entries pointing to the current section get a `current` CSS class; the current page link carries `aria-current="page"`.

The toggle ships as a keyboard-operable checkbox-hack fallback and is progressively enhanced by `ts/menu.ts` (loaded by the partial): once the script runs, the toggle is a real `<button>` with `aria-expanded`/`aria-controls`, the closed list is `inert`, and the menu closes on Escape, outside clicks or focus leaving it.

## `topnavigation.html` {#topnavigation}

Placeholder container above the header, empty by default — a site can override it.

## `footer.html` and `footer-content.html` {#footer}

`footer.html` renders the main menu as footer navigation plus the footer content. `footer-content.html` renders the copyright block:

| Site parameter (default site) | Purpose |
| --- | --- |
| `copyright` | Custom copyright text |
| `copyrightYears` | Custom year range, prepends `©` |
| `copyright: "false"` | Renders an empty copyright |
| `cc: true` | Adds the Creative Commons note |
| `footer.privacy: true` | Adds a privacy policy link |
| `footer.privacyUrl` | Alternative privacy URL (default `/privacy`) |

`footer-content.html` is called with a `dict` of `page` (the current page) and `footer` — an HTML string that is appended after the copyright block. The theme itself passes an empty string; a site overriding `footer.html` supplies its own footer content:

```html
{{- partial "footer-content.html" (dict "page" . "footer" $footerStr) -}}
```

## `404.html` and `404-content.html` {#404}

`404.html` wraps the base template, `404-content.html` renders the error text and — with the site parameters `errorimg: true` and `logo` — an error image.

## `list.html` and `home.html` {#list}

`list.html` renders a paginated page list: filters `metaPage` pages, keeps pages with `displayinlist != false`, renders each with the site's [`li.html`](extension-points/#lihtml-required-for-list-pages) partial, then previous/next pagination links if there is more than one page. `home.html` is a thin wrapper feeding `.Site.RegularPages` into the same markup.

## `pagination.html` {#pagination}

Renders the numbered pagination: previous/next links with i18n labels plus the page number list — the current page carries `aria-current="page"`, every page number link gets a visually hidden "page N" label.

## `page.html` {#page}

Renders a single page: title, content and — unless `metaPage: true` — the date and [tags](#tags) footer. The `type` front matter parameter becomes an additional CSS class.

## `toc.html` {#toc}

Renders a table of contents for a section page — a list of the section's child pages. The example site places it as a sticky sidebar next to the section content (via its `list.html` override), but it can be called from any layout:

```go-html-template
{{ partial "toc.html" (dict "entries" . "maxLevels" 2) }}
```

| Parameter | Purpose |
| --- | --- |
| `entries` | A section page — its children are rendered; a page slice is rendered as a flat list without grouping |
| `maxLevels` | Number of levels to render, counting the top level (default `2`; `3` also renders the children of nested sections, child sections are always rendered without their children once the level is exhausted) |
| `title` | Heading above the list (defaults to the `inThisSection` i18n string) |

Pages with the front matter parameter `tocExclude: true` are skipped. Pages stored directly in the section root and child sections are top level entries; pages in subdirectories without their own `_index.md` are grouped under the directory name — e.g. the `shortcodes/html/` pages become an `html` group on the `/shortcodes/` section. A subdirectory holding only one page is promoted to a top level entry. The partial emits an `<aside class="section-toc">` with a `<nav class="toc">` inside; it renders nothing when no entries remain after filtering. A site can ship its own version through `layouts/partials/toc.html`.

## `html/iframe-consent.html` {#html-iframe-consent}

Renders the consent overlay for embedded iframes: notice text (i18n), an optional `preview` and the consent toggle. The toggle ships as a keyboard-operable checkbox-hack fallback and is progressively enhanced to a `<button role="switch" aria-checked>` (see the [`html/iframe-consent` shortcode](/shortcodes/html/iframe-consent/)).

## `html/html-body.html` {#html-body}

Renders the body of a standalone HTML page, used by the [`html-body` template](../single-list/#html-body) and the [`html/include` shortcode](/shortcodes/html/include/).

## `meta/tags.html` and `meta/i18n-tags.html` {#tags}

Both render the tag list of a page as links to the `tags/` terms:

- `meta/tags.html` renders each tag through the [tag cloud plug-ins](../plugin-dispatch/#tag-cloud) — the page parameter `render` selects the variant (default `tag`)
- `meta/i18n-tags.html` renders the tags through `i18n` translations instead

## `post-relations.html` {#post-relations}

Renders contextual navigation for a page: on section pages a list of the section's pages, on regular pages a link to the parent section. Skipped for `metaPage` pages.
