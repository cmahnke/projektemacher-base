---
title: PDF article
params:
  displayinlist: false
  metaPage: true
---

# PDF article

The `pdf-article` output format renders a per-page printable article variant (`article.html`) used as input for PDF generation.

Reference implementation: `christianmahnke/layouts/_default/single.pdf-article.html` with `christianmahnke/layouts/_default/baseof.pdf-article.html`. The theme ships no `pdf-article` page template — only the shared `baseof.print.html` base variant and the `print/` partials and shortcodes — copy or adapt those templates if the format is needed.

## Behavior

- `single.pdf-article.html` fills the `title` and `content` blocks with the page header and the `article/page.html` partial.
- `baseof.pdf-article.html` is a standalone skeleton: it sets `author`, `subject` and `date` meta tags, compiles `scss/article-pdf.scss` to `css/article.css` and loads `js/print.js`. Asset URLs honor the site parameter `print.relative`.
- Shortcodes can provide `*.pdf-article.html` overrides (e.g. `figure.pdf-article.html`, `footnote.pdf-article.html`, `gallery.pdf-article.html`), the reference site uses them to produce PDF friendly markup.

The `print` output format is intentionally not documented here.

## Site parameters

| Parameter | Type | Default | Purpose |
|---|---|---|---|
| `print.relative` | int | `0` | Characters stripped from asset URLs to make them relative |

## Enabling

```toml
[outputFormats]
  [outputFormats.pdf-article]
    mediaType = "text/html"
    isPlainText = false
    isHTML = true
    baseName = "article"
    notAlternative = true
    permalinkable = true
```

Then enable it per page:

```markdown
---
title: My page
outputs: ["HTML", "pdf-article"]
---
```

The generated file is available as `/page/article.html`. The reference site scopes PDF builds with `[segments.print]` includes/excludes, see `christianmahnke/config.toml`.

## See also

- [Base template](baseof/#print-variant) — the `baseof.print.html` variant
- [Print partials](partials/print-partials/) — building blocks for print editions
- [BibTeX](bibtex/) — citation export, often enabled together with `pdf-article`
