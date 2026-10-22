---
title: Search page
params:
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

## WebMCP / AI agents

The theme can expose the search as a tool to AI agents via
[WebMCP](https://webmachinelearning.github.io/webmcp/) — browsers with
WebMCP support let in-page agents (and the browser's own agent) invoke
site functionality through `document.modelContext`. The binding lives
in `assets/ts/webmcp-search.ts` and registers one tool, `search`, with
no dependency on the search UI: it loads the Pagefind runtime directly
from the search index bundle.

It is opt-in, site-wide via the site parameters:

```toml
[params.webMcpSearch]
  enabled = true
```

Without `bundlePath` the search bundle is read from
`site.BaseURL + index/`, which works for domain root deployments as
well as subpath deployments (e.g. the [example site](/) under
`/projektemacher-base/`). The script resolves the path with the same
precedence as the search page:

- `data-bundle-path` on the search box container (search page, page
  front matter `searchBundlePath`, see [behavior snippets above](#usage))
- `<meta name="webmcp-search-bundle-path">`, emitted by the theme
  itself — for explicit overrides set `bundlePath` (site or page level,
  absolute path) together with `enabled`
- fallback `/index/`

Individual pages can opt in/out or override the path by putting the
same params into their front matter (`webMcpSearch.enabled = false`
disables the tool on that page).

The tool's input schema accepts `query` (required), optional `filters`
(a map of filter name to string values, matching the filters indexed
via [pagefind-index.yaml](https://pagefind.app/docs/filters/), e.g.
`section`, `tag`, `type` on this site) and an optional `limit` (1–25,
default 10). It returns the matching pages as `url`, `title`, `meta`
and a highlighted `excerpt`, plus the result totals:

```javascript
const [tool] = await document.modelContext.getTools();
const result = JSON.parse(await document.modelContext.executeTool(tool, {
    query: "hugo",
    filters: {section: ["post"]},
    limit: 5
}));
```

The tool is registered as read-only (`readOnlyHint`) — searching never
mutates state — and its output is marked as untrusted content, since
excerpts are built from indexed page content. Engine support is still
rolling out: pages run the binding only where `document.modelContext`
exposes `registerTool`, and registration failures (for example when
the [Permissions Policy](https://developer.mozilla.org/docs/Web/HTTP/Reference/Headers/Permissions-Policy)
disallows the `tools` feature) are logged as console warnings only.
The feature is a secure context, so `http://localhost` servers and
HTTPS deployments are fine.

## Requirements

- The Pagefind index must be generated for the deployed site (`pagefind` post processing), without it the page renders but returns no results
