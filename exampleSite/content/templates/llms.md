---
title: LLMS
displayinlist: false
metaPage: true
---

# LLMS

The `llms` output format (`llms.json`, `text/plain`) is a placeholder defined in the reference configuration. Neither the theme nor the reference site ships a page template for it — do not confuse it with the `llms.txt` crawler hint described below.

## Output format definition

From `christianmahnke/config.toml`:

```toml
[outputFormats]
  [outputFormats.llms]
    mediaType = "text/plain"
    baseName = "llms"
    isPlainText = true
    notAlternative = true
```

There is no `single.llms.*`, `list.llms.*` or similar template in `layouts/`. Enabling the format without providing such a template renders nothing useful; add a custom template first if the file is needed.

## `llms.txt` (crawler hint, not an output format)

The theme generates an `llms.txt` hint from the `robots.txt` template instead:

- Source: `assets/llms.go.txt` rendered with `resources.ExecuteAsTemplate "llms.txt"`.
- It lists the home page, sections and sub-sections (honoring `sitemap_exclude` and `Sitemap.Disable`) with titles, permalinks and descriptions.
- It is referenced with an `llms-txt:` line in `robots.txt` when the site parameter `robots.llmsTXT` is set:

```toml
[params.robots]
  llmsTXT = true
```

This follows the [LLMS crawler hints proposal](https://discourse.gohugo.io/t/support-for-llms-txt-standard-for-ai-crawlers/53782/3).

## See also

- [404 and robots.txt](404-robots/) — `robots.txt`, `sitemap.xml` and the `llms-txt:` line
- [Data lists](data-lists/) — the JSON search and tag indexes
