---
title: 404 and robots
params:
  displayinlist: false
  metaPage: true
---

# 404 and robots.txt

## `404.html`

The `404.html` template fills the `content` block of the [base template](baseof/) with the `404.html` partial. The content is provided by the `404-content.html` partial and contains:

- the translated "page not found" heading and back link
- optionally an error image, if the site parameter `errorimg` is set — the image source is the site parameter `logo`

### Site parameters

| Parameter | Type | Default | Purpose |
| --- | --- | --- | --- |
| `errorimg` | bool | `false` | Show the error image |
| `logo` | string | — | Image URL used for the error image |

## `robots.txt`

The `robots.txt` template is enabled with `enableRobotsTXT = true` in the site configuration. It renders:

1. `Disallow:` entries for all pages with `robotsdisallow: true` or `sitemap_exclude: true`
2. a `Sitemap:` line pointing to the language specific sitemap
3. an optional `llms-txt:` line (see below)

### Front matter parameters

| Parameter | Type | Default | Purpose |
| --- | --- | --- | --- |
| `robotsdisallow` | bool | `false` | Adds `Disallow: <RelPermalink>` |
| `sitemap_exclude` | bool | `false` | Adds `Disallow: <RelPermalink>` as well |

### `llms.txt`

If the site provides an `assets/llms.go.txt` resource and the site parameter `robots.llmsTXT` is set, the resource is rendered as a template to `llms.txt` and referenced with an `llms-txt:` line — this follows the proposal for [LLMS crawler hints](https://discourse.gohugo.io/t/support-for-llms-txt-standard-for-ai-crawlers/53782/3).

| Parameter | Type | Default | Purpose |
|---|---|---|---|
| `robots.llmsTXT` | bool | `false` | Enable the `llms-txt:` line |

## `sitemap.xml`

The custom sitemap template skips tag pages and pages with `news: false` or `archive: false`, honors Hugo's built in `Sitemap.Disable`, `Sitemap.ChangeFreq` and `Sitemap.Priority` settings, and adds `xhtml:link` hreflang alternates for translated pages.

| Parameter | Type | Default | Purpose |
| --- | --- | --- | --- |
| `news` | bool | `true` | Set to `false` to remove the page from the sitemap |
| `archive` | bool | `true` | Set to `false` to remove the page from the sitemap |

## Example

```markdown
---
title: Internal page
robotsdisallow: true
news: false
---
```
