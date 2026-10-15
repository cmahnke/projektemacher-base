---
title: Structural partials
displayinlist: false
metaPage: true
---

# Structural partials

These partials render the common page chrome. They are used by the theme's templates and can be called (or overridden) by sites — the consuming sites `projektemacher.org` and `labs.projektemacher.org` call most of them from their own layouts.

## `head.html` {#head}

Renders the complete `<head>` content: title, meta description, the main JavaScript bundle (with the IIIF viewer concatenated if the page has an `iiifcontext`), external `stylesheets`, the compiled SCSS, favicons and `<link>` alternates for the RSS and `iiif-collection` output formats.

> **Warning:** this partial emits a build warning — it makes page specific scripts and styles impossible. Use the `html/head/*` partials individually instead.

| Site parameter | Purpose |
|---|---|
| `slogan` | Appended to the title on the home page |
| `description` | Fallback meta description |
| `stylesheets` | List of external stylesheet URLs |
| `favicon_16`, `favicon_32`, `favicon_svg` | Favicons |

It also inspects the page parameter `iiifcontext` to decide which viewer script to bundle.

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

## `html/html-body.html` {#html-body}

Renders the body of a standalone HTML page, used by the [`html-body` template](../single-list/#html-body) and the [`html/include` shortcode](/shortcodes/html/include/).

## `meta/tags.html` and `meta/i18n-tags.html` {#tags}

Both render the tag list of a page as links to the `tags/` terms:

- `meta/tags.html` renders each tag through the [tag cloud plug-ins](../plugin-dispatch/#tag-cloud) — the page parameter `render` selects the variant (default `tag`)
- `meta/i18n-tags.html` renders the tags through `i18n` translations instead

## `post-relations.html` {#post-relations}

Renders contextual navigation for a page: on section pages a list of the section's pages, on regular pages a link to the parent section. Skipped for `metaPage` pages.
