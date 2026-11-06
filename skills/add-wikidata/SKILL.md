---
name: add-wikidata
description: Add Wikidata entity references to posts, pages and tags in Hugo sites using the projektemacher-base theme. Use when the user asks to add wikidata front matter to posts, find Wikidata QIDs for content subjects, or map tags to Wikidata entities.
---

# add-wikidata

Add `wikidata` front matter parameters to content of a site using the
`projektemacher-base` Hugo theme, so entities are exposed as structured
metadata (HTML summary block, schema.org, Linked Art, JSON indexes).

## What the theme does with the parameter

| Location | Consumption |
| --- | --- |
| Post/page front matter (`wikidata`) | Summary block (`layouts/_partials/data/wikidata.html`), `wikidata-list.json`, schema.org `about`/`sameAs` (`layouts/_partials/metadata/schema.org/util/about.html`), Linked Art output |
| Tag term page front matter (`params.wikidata`) | Tag `sameAs` in `layouts/tag-list.json`, tag entities in `layouts/wikidata-list.json` |

Additionally the theme's link render hook (`layouts/_markup/render-link.html`)
resolves external URLs in content to Wikidata entities via SPARQL and adds
`data-wikidata-entity` attributes automatically. This happens without front
matter — the explicit `wikidata` parameter is still required to make the
relation complete and queryable in the JSON indexes.

## Front matter formats

`wikidata` accepts a string, a list of strings, or a map of URI to relation
(e.g. `subject`, `related`). Prefer string or list — the map form is only
rendered by the summary block and schema.org output, the `wikidata-list.json`
index expects plain URIs.

YAML (used by most sites):

```yaml
---
title: Example post
tags:
  - Lithography
wikidata:
  - https://www.wikidata.org/wiki/Q188675
  - https://www.wikidata.org/wiki/Q564783
---
```

TOML:

```toml
+++
title = "Example post"
wikidata = [
  "https://www.wikidata.org/wiki/Q188675",
  "https://www.wikidata.org/wiki/Q564783",
]
+++
```

Always use the full `https://www.wikidata.org/wiki/Q…` URI form.

## Finding the right QID

Only add entities for well-defined subjects: people, organisations, works,
events, technologies, places, concepts behind tags. Never invent QIDs, and ask
the user when candidates are ambiguous.

1. **Collect candidates** from the post title, existing tags and external
   URLs mentioned in the content.

2. **Search** via the Wikidata Action API:

   ```bash
   curl -A "site-builder/1.0 (https://example.org; mail@example.org)" \
     "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=Lithography&language=en&format=json&limit=10"
   ```

   Set a descriptive `User-Agent` (project URL + contact) — Wikimedia rejects
   requests without one with 403.

3. **Verify** each candidate with the EntityData dump before writing it:

   ```bash
   curl -A "site-builder/1.0 (https://example.org; mail@example.org)" \
     "https://www.wikidata.org/wiki/Special:EntityData/Q1020352.json"
   ```

   Check:

   - `labels` exist in the site languages (the theme resolves labels per
     language, falling back to the QID when missing)
   - `descriptions` match the intended meaning
   - `claims/P31` (instance of) is plausible for the subject type
   - for website-related posts, match `claims/P856` (official website) or
     `claims/P1581` (official blog) against URLs in the content — this is the
     same lookup the theme's link hook performs:

     ```sparql
     SELECT ?item WHERE { ?item wdt:P856 <https://example.org> . }
     ```

     (Run against `https://query.wikidata.org/sparql` with
     `Accept: application/sparql-results+json`; on 403 responses, e.g. from CI
     runners, use the QLever endpoint `https://qlever.cs.uni-freiburg.de/api/wikidata`
     instead, see the theme's `sparql-qlever.html` partial.)

4. **Deduplicate**: one entity per distinct subject; entities already present
   on the tag term pages of the post's tags are picked up automatically by
   `wikidata-list.json`, so only add page-level entities that add new subjects.

## Applying changes

### Posts and pages

- Add/extend the `wikidata` list in the **root front matter** of the page
  (not under `params:` — though Hugo merges both, the established convention
  in this theme's sites is root level for posts, `params:` for tags).
- Update **all language variants** of the page (`index.md`, `index.en.md`, …)
  with the same list — translations are rendered per language but must carry
  the same entity references.
- Preserve the file's existing front matter style (quote style, indentation,
  key order).

### Tags

Tag term pages live at `content/tags/<Term>/_index.md` (folder name is the
urlized tag name), with one file per language (`_index.md`, `_index.en.md`).

```yaml
---
title: 'Spende'
description: ''
params:
  wikidata: https://www.wikidata.org/wiki/Q1124860
---

Short description of the tag.
```

- Set `params.wikidata` to the primary entity URI (string, or list when a tag
  needs several; `tag-list.json` uses the first entry as `sameAs`).
- If a term page is missing, create it for **every** site language with a
  localized `title` and a one-sentence `description` — `tag-list.json` flags
  missing term pages as `definitionMissing`.
- Only map tags that denote a identifiable entity; generic tags (e.g.
  "Software", "DIY") may stay unmapped — prefer the most specific concept.
- Keep the wikidata lists of the language variants consistent.

## Validation

1. Build the site (`hugo` or the site's build command). Build errors in
   `wikidata-label.html` mean an unreachable/invalid entity URI.
2. If the site exposes the JSON index (a page with `layout: wikidata-list`,
   typically `content/meta/wikidata/index.md` → `public/meta/wikidata/index.json`):

   ```bash
   jq '.pages[] | select(.url | contains("example-post"))' public/meta/wikidata/index.json
   jq '.tags.unmapped' public/meta/wikidata/index.json
   ```

   - edited posts must appear with their full URI list
   - `tags.unmapped` lists tags still lacking a `wikidata` parameter — the
     remaining work queue
3. Check the rendered post HTML for the `wikidata-summary` block and the
   schema.org JSON-LD (`about` entries with `http://www.wikidata.org/entity/…`
   `@id`s).
4. Sites without the JSON index pages can enable them via home `outputs`
   (see the theme docs on data lists) or validate from the HTML output only.

## Reference

- Theme docs (exampleSite): `exampleSite/content/wikidata/` (SPARQL backend,
  security config), `exampleSite/content/templates/data-lists.md` (JSON index
  shapes and enabling), `exampleSite/content/templates/partials/helpers.md`
  (`data/wikidata.html` partial)
- Label resolution: `layouts/_partials/data/functions/wikidata-label.html`
  (Wikidata EntityData JSON API, per-language with fallback)
