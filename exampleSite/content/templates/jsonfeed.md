---
title: JSON Feed
params:
  displayinlist: false
  metaPage: true
  toc: true
---

# JSON Feed

The theme registers a `jsonfeed` output format for [JSON Feed 1.1](https://jsonfeed.org/version/1.1) and ships a template for the home page, so a site can publish its posts as `feed.json` alongside the HTML home page.

## Output format definition

From the theme's `hugo.toml` (merged into every site using the theme):

```toml
[mediaTypes."application/feed+json"]
  suffixes = ["json"]

[outputFormats]
  [outputFormats.jsonfeed]
    mediaType = "application/feed+json"
    baseName = "feed"
    isPlainText = true
    isHTML = false
```

The output file is `feed.json` next to the page. Sites can override any of these values in their own config.

## Enabling it

Add the format to the home page in the site configuration:

```toml
[outputs]
  home = ["html", "jsonfeed"]
```

Other page kinds are not wired up by default: the theme only provides `home.jsonfeed.json`. Enable the format for other kinds only after providing a matching template (a `section.jsonfeed.json` or `single.jsonfeed.json`), otherwise Hugo warns about a missing layout and renders nothing.

## Template

`layouts/home.jsonfeed.json` generates a JSON Feed 1.1 document:

- **Items** come from the `post` section, newest first (`.ByDate.Reverse`), limited by `site.Config.Services.RSS.Limit` when that value is at least 1.
- Each item carries `id` and `url` (the permalink), `title`, `content_html` (the summary), and optionally `summary` (plain text), `tags` and `authors`. An author entry is added from `site.Params.author.email` when set.
- The feed envelope has `version`, `title`, `home_page_url` (the home page permalink), `feed_url` (the format's permalink), `description`, `language` (the site locale), `items`, and optionally top-level `authors`.
- `favicon` falls back to `/images/favicon-32.png` and can be set via `site.Params.favicon_32`; `icon` uses `site.Params.favicon_svg` when configured. Both are made absolute with `absURL`.
- A map-valued `site.Params.author` supplies `name` and `email`; a plain string value is used as the name.

Pages marked `metaPage` or with `displayinlist = false` are excluded from `post-list.json`; the feed uses the section's regular pages directly.

## Head advertisement

Once enabled, the format shows up in `.AlternativeOutputFormats`. The theme's `layouts/_partials/html/head/links.html` emits the corresponding `<link rel="alternate" type="application/feed+json" href="…">` — the format defines no `rel`, so the default `alternate` applies. Sites with their own output-format loop in the base template get the same link automatically.

## Caveats

- The feed title and description use the i18n keys `Feed`, `LatestPosts` and `By`. These keys are not currently defined in the theme's translation files, so they render as the literal key names; define them in the site's `i18n/` directory to localize the feed metadata.
- `content_html` uses the page summary, not the full rendered content.
- When the format is enabled but no template exists, Hugo warns (`found no layout file`) and skips rendering while the head still advertises the link.

## See also

- [Output formats](/templates/) — the theme's other output formats
- [Front matter parameters](/templates/#front-matter-parameters) — `metaPage`, `displayinlist` and related switches
