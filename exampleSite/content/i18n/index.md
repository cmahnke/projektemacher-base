---
title: i18n strings
description: "All translated strings shipped with the theme, generated dynamically from the i18n files"
js:
  - js/i18n-search.js
scss:
  - scss/i18n.scss
---

# i18n strings

This page lists all strings from the theme's `i18n/` directory in a single table with one column per language. It is generated at build time from the theme's translation files — when a new translation or language is added, a column or new rows show up automatically, no page changes needed.

## How the theme's i18n files work

Translations live in the theme's `i18n/` directory. Hugo loads files named `<lang>.toml` as the translation catalog for that language. For larger translation sets the strings can be split into fragments named `<id>.<lang>.toml` (for example `tags.de.toml` or `iiif.en.toml`), which get merged into the main `<lang>.toml` files by the [`scripts/init/i18n.sh`](https://github.com/cmahnke/projektemacher-base/blob/main/scripts/init/i18n.sh) script. Note that the merged files are generated (gitignored), while the fragments are tracked in git.

The data for the table below comes from the same files: the example site mounts the theme's `i18n/` directory as a [data directory](https://gohugo.io/configuration/module/) in its `hugo.toml`

```toml
[module]
  [[module.mounts]]
    source = '../i18n'
    target = 'data/i18n'
```

so every `<id>.<lang>.toml` and `<lang>.toml` file is available as `site.Data.i18n.*` at build time. The [`i18n-strings` shortcode](https://github.com/cmahnke/projektemacher-base/blob/main/exampleSite/layouts/shortcodes/i18n-strings.html) groups the files by their language suffix and renders the table. Each language column has a search box in its header — the filter matches the key or the column's value, and multiple filters are combined. Missing translations are shown as greyed out cells — CI enforces completeness with the [`scripts/check_i18n.py`](https://github.com/cmahnke/projektemacher-base/blob/main/scripts/check_i18n.py) script.

{{< i18n-strings >}}
