---
title: Base template
params:
  displayinlist: false
  metaPage: true
---

# Base template

The base template `_default/baseof.html` defines the common page skeleton: `<head>` (via the `html/head/meta.html`, `links.html`, `style.html` and `script.html` partials), the site header with top navigation, the `<main>` element and the footer.

## Blocks

Custom templates override the following blocks:

| Block | Purpose |
| --- | --- |
| `title` | `<title>` content, defaults to the page title (plus the `slogan` on the home page) — the `html/head/title.html` partial renders it |
| `body` | Attributes and content at the start of `<body>` |
| `main` | Content before the `content` block inside `<main>` |
| `content` | The actual page content |

The shipped `single.html` only defines `title` and `content`, for example:

```go-html-template
{{ define "title" }}
  {{ .Title }} · {{ .Site.Title }}
{{ end }}
{{ define "content" }}
  {{ partial "page.html" . }}
{{ end }}
```

## Body classes

The `<body>` element gets the classes `home blog` plus:

- `about` — for pages whose file path starts with `about`
- `meta` — for pages with `metaPage: true`

## Styles and scripts

The base template includes the main stylesheet (`css/style.css`) and the script bundle via the `html/head/style.html` and `html/head/script.html` partials. Which scripts are loaded can be influenced per page, see the `iiif-js.html` partial.

The script bundle format follows the site configuration:

```toml
[params.js]
  format = "esm"
```

… or the string shorthand `[params] js = 'esm'`. With `format = "esm"` every bundle — main, IIIF viewers, page/shortcode scripts and the menu — is fingerprinted individually and ships as its own `<script type="module" … crossorigin="anonymous">` tag. ESM bundles are never concatenated: separately minified bundles reuse the same mangled top level identifiers, so concatenating them into one module scope causes `SyntaxError: Identifier 'Pe' has already been declared`-style collisions. Module tags execute in document order, so the main bundle still runs before page scripts. Without the parameter (or with `format = "iife"`) the bundles build as classic IIFE scripts and ship concatenated with `defer` — `splitBundles` only affects that classic path.

## Print variant

`_default/baseof.print.html` is the base template for print output. It compiles `scss/print.scss` and `js/print.js` and adds meta tags for author and build date. It honors the site parameter `print.relative` to make asset URLs relative. It is selected by the print related output formats and renders the partials from `layouts/partials/print/`.
