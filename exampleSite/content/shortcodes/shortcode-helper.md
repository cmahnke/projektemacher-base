---
title: Shortcode helper system
displayinlist: false
metaPage: true
---

# Shortcode helper system

Shortcodes often need page specific JavaScript and styles. This theme ships a helper system that detects which shortcodes a page uses and includes only the required assets for that page — no global asset bloat.

## Declaring shortcode assets

A shortcode declares its requirements with an inline partial named `_partials/shortcodes/<name>-metadata.html`, returning a JSON object with `css`, `js` and/or `scss` lists:

```html
{{- define "_partials/shortcodes/code-metadata.html" -}}
  {{- (dict "css" slice "js" (slice "ts/shortcodes/code.ts") "scss" (slice "scss/shortcodes/code.scss")) | jsonify -}}
{{- end -}}
```

Paths starting with `http` are treated as external resources, everything else is resolved from `assets/`.

## How it works

1. **Cache** — `partials/shortcodes/shortcode-helper-cache.html` (rendered once per build via `partialCached`) scans the raw content of all site pages with a regular expression to find every used shortcode name. For each name it reads `layouts/shortcodes/<name>.html` from disk, extracts the inline `-metadata` partial, executes it and normalizes `js`/`scss`/`css` to slices. The result is returned as JSON: shortcode name → asset lists. In debug mode every entry is sanity checked — local files missing from `assets/` abort the build with an `errorf`.
2. **Per page filter** — `partials/shortcodes/shortcode-helper.html` unmarshals the cache and checks `$.Page.HasShortcode <name>` for every entry, returning the merged `{"js": […], "scss": […], "css": […]}` requirements for the current page only.
3. **Consumers**:
   - `partials/html/head/script.html` — bundles the `js` entries (local files via `resources.Get` + `js.Build`, external ones via `resources.GetRemote`) into a single fingerprinted `<script>`
   - `partials/html/head/style.html` — compiles the `scss` entries together with the page's own SCSS (Dart SASS) and appends the `css` entries, producing a single fingerprinted `<link>`

## Parameters

| Level | Key | Purpose |
| --- | --- | --- |
| Site | `skipShortcodeAssets` | Intended to disable shortcode asset processing. Note: the current guard in `shortcode-helper.html` evaluates to true in every case, so the setting has no effect yet |
| Page | `ignoreincludes` | Drops page level js/scss/css includes from `html/head/script.html` / `html/head/style.html` |

## File includes from shortcodes

Shortcodes that read files use the `partials/html/html-body.html` partial, which has two calling conventions:

- **Shortcode context** (`*hugolib.ShortcodeWithPage`, e.g. [html/include](../html/include/)): the file is taken from the shortcode's `file` parameter, resolved relative to the page's directory
- **Page context** (`*hugolib.pageState`): the file comes from the page params, joined with the page directory

The partial extracts the content between `<body>…</body>` and errors (`errorf`) when the file is missing, empty or the arguments are unusable.
