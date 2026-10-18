---
title: Search page
displayinlist: false
metaPage: true
---

# Search

The `search.html` template renders the search page: a text input, a filter container and a result container. All actual searching happens client side with [Pagefind](https://pagefind.app/) — the index is built after Hugo runs (see `pagefind-index.yaml` in the theme root).

## Usage

Create a page using the template via its `layout` front matter:

```markdown
---
title: Search
layout: search
---
```

The page also needs the search script, either via its front matter (as
the [example page](/search/) does) or imported by the site's own
`main.ts`:

```markdown
js:
  - ts/search.ts
```

If the page has no title, the `<title>` falls back to the site title.

The page is typically excluded from listings the same way as other meta pages (`metaPage: true`, `displayinlist: false`).

## Behavior

- The button and placeholder labels use the `Search` i18n key
- Results are rendered into `#search-results`, filters into `#search-filter`
- The search box and button can also be placed into the menu directly, see [menu configuration](/config/menu/) for an HTML menu entry example

## Requirements

- The Pagefind index must be generated for the deployed site (`pagefind` post processing), without it the page renders but returns no results
