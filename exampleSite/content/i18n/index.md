---
title: i18n strings
description: "All translated strings shipped with the theme, generated dynamically from the i18n files"
js:
  - js/i18n-search.js
scss:
  - scss/i18n.scss
---

# i18n strings

This page lists all strings from the theme's `i18n/` directory, grouped by language. It is generated at build time from the theme's translation files — when a new translation or language is added, it shows up here automatically, no page changes needed.

## How the theme's i18n files work

Translations live in the theme's `i18n/` directory. Hugo loads files named `<lang>.toml` as the translation catalog for that language. For larger translation sets the strings can be split into fragments named `<id>.<lang>.toml` (for example `tags.de.toml` or `iiif.en.toml`), which get merged into the main `<lang>.toml` files by the [`scripts/init/i18n.sh`](https://github.com/cmahnke/projektemacher-base/blob/main/scripts/init/i18n.sh) script. Note that the merged files are generated (gitignored), while the fragments are tracked in git.

The data for the tables below comes from the same files: the example site mounts the theme's `i18n/` directory as a [data directory](https://gohugo.io/configuration/module/) in its `hugo.toml`

```toml
[module]
  [[module.mounts]]
    source = '../i18n'
    target = 'data/i18n'
```

so every `<id>.<lang>.toml` and `<lang>.toml` file is available as `site.Data.i18n.*` at build time. The [`i18n-strings` shortcode](https://github.com/cmahnke/projektemacher-base/blob/main/exampleSite/layouts/shortcodes/i18n-strings.html) groups the files by their language suffix and renders the tables. The search box below each table filters by key and value using [assets/js/i18n-search.js](https://github.com/cmahnke/projektemacher-base/blob/main/exampleSite/assets/js/i18n-search.js).

{{< i18n-strings >}}
