---
title: Data lists
displayinlist: false
metaPage: true
---

# Data list templates

The theme generates several JSON files used for client side search, tag relations and Wikidata integration. All of them filter out pages with `displayinlist: false` and — where noted — `metaPage: true`.

## `post-list.json`

An index of all pages of the current language, used by client side search. Each entry contains:

| Field | Source |
| --- | --- |
| `url` | HTML output permalink |
| `title` | Page title |
| `section` | Paths of all ancestor sections |
| `path` | Page path |
| `lang` | Language code |
| `summary` | Page summary |
| `tags` | Page tags, if set |
| `date` | Page date, if set |
| `outputs` | All output formats of the page with `name` and `url` |

Pages with `metaPage: true` are excluded.

## `tag-list.json`

A dictionary of all tags used on pages, keyed by tag name. Each entry contains:

| Field | Source |
| --- | --- |
| `url` | Term page URL |
| `posts` | Rel permalinks of all pages with the tag |
| `count` | Number of pages |
| `translations` | Translated tag names per language (via the theme i18n files) |
| `termTitle` | Title of the term page |
| `sameAs` | First `wikidata` entry of the term page, if set |
| `definitionMissing` | Present if the term page (`content/tags/<tag>/_index.md`) doesn't exist |
| `tagPath` | Present if the URL and the file path of the term differ |

This template warns about missing term pages when [debug mode](/posts/site-params/) is enabled.

## `wikidata-list.json`

Collects Wikidata entity links for all regular pages. Entities are gathered from three sources:

1. the `wikidata` front matter parameter of the page (string or list)
2. the `wikidata` front matter parameter of the tag term pages a page is tagged with
3. `data-wikidata-entity="Q…"` attributes found in the rendered content of the page and its translations

The output has the shape:

```json
{
  "pages": [{ "url": "…", "title": "…", "wikidata": ["…"] }],
  "tags": { "sameAs": { "…": ["…"] }, "unmapped": ["…"] }
}
```

`unmapped` lists tags whose term pages have no `wikidata` parameter.

Only pages with at least one entity are included.

## Enabling

The JSON templates are tied to output formats — add them to the page or site `outputs` configuration:

```toml
[outputs]
    home = ["HTML", "post-list", "tag-list", "wikidata-list"]
```

The exact format names depend on the `outputFormats` configuration of the site, see the [example site configuration](https://github.com/cmahnke/projektemacher-base/blob/main/exampleSite/hugo.toml).
