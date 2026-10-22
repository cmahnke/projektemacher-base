---
title: Linkset
params:
  displayinlist: false
  metaPage: true
  toc: true
---

# Linkset

The `linkset` output format advertises a [W3C linkset](https://www.w3.org/TR/linkset/)
(`application/linkset+json`) for a page. The theme only **registers** the
format and advertises it in the document head — the content is entirely
site specific and rendered by a site-provided template.

## Output format definition

From the theme's `hugo.toml` (merged into every site using the theme):

```toml
[mediaTypes."application/linkset+json"]
  suffixes = ["json"]

[outputFormats]
  [outputFormats.linkset]
    mediaType = "application/linkset+json"
    baseName = "linkset"
    isPlainText = true
    isHTML = false
    rel = "linkset"
```

The `rel = "linkset"` value is what makes the document head emit
`<link rel="linkset">` instead of the default `rel="alternate"`. The output
file is `linkset.json` next to the page.

## Enabling it

Add the format to the desired page kinds in the site configuration:

```toml
[outputs]
  home = ["html", "linkset"]
  page = ["html", "linkset"]
```

## Providing the template

The theme ships **no template** for the format — provide one following the
[template lookup order](https://gohugo.io/templates/lookup-order/), e.g.
`layouts/home.linkset.json` for the home page or `layouts/single.linkset.json`
for regular pages, rendering the complete
[linkset envelope](https://www.w3.org/TR/linkset/#dfn-linkset):

```go-html-template
{{- $links := slice
      (dict "href" .Permalink "rel" "self" "type" "text/html")
      (dict "href" .Permalink "rel" "describedby" "type" "application/ld+json") -}}
{{- with dict "linkset" (slice (dict "anchor" .Permalink "link" $links)) -}}
{{- jsonify . -}}
{{- end -}}
```

The content is up to the site — anything valid for the W3C linkset format.

## Head advertisement

Once the format is enabled for a page kind, the head advertises it
automatically:

- The theme's `layouts/_partials/html/head/links.html` loops over
  `.AlternativeOutputFormats` and emits
  `<link rel="linkset" type="application/linkset+json" href="…">`
- Sites with their own `.AlternativeOutputFormats` loop in the base template
  emit the same link without any theme involvement — the `rel` value comes
  from the output format definition

Note: when the format is enabled but no template exists, Hugo warns
(`found no layout file for "linkset" …`), skips rendering, and the head
still advertises the link — always provide a template when enabling the
format.

## See also

- [Output formats](/templates/) — the theme's other output formats
- [`robots.txt` / `llms.txt`](404-robots/) — crawler hints
