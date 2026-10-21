---
title: BibTeX
displayinlist: false
metaPage: true
---

# BibTeX

The `bibtex` output format renders a per-page BibTeX citation file (`citation.bib`).

Reference implementation: `christianmahnke/layouts/_default/single.bib`. The theme ships no `bibtex` page template — copy or adapt that template if the format is needed.

## Output

`citation.bib` contains a single entry, e.g.:

```bibtex
@article{my-key,
  author = {Christian Mahnke},
  title = {My title},
  url = {https://example.org/post/my-page/},
  year = {2024},
}
```

If the page has no `cite: true` front matter, the file only contains:

```text
% Error: BibTex export not enabled: Cannot generate BibTeX entry.
```

## Front matter parameters

| Parameter | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `cite` | bool | yes | — | Set to `true` to enable the export, otherwise only the error comment is rendered |
| `bibtex_key` | string | yes | — | Citation key after `@<type>{` |
| `authors` | list of maps | no | site `author.name` | Maps with `first` and `last`, joined with ` and ` |
| `doi` | string | no | — | Rendered as `doi = {…}` |
| `note` | string | no | — | Rendered as `note = {…}` |
| `description` | string | no | — | Rendered as `abstract = {…}` |
| `keywords` | string list | no | — | Rendered as `keywords = {…}` (space separated) |

The entry type comes from the site parameter `citation.type` and defaults to `article`. `url` is the permalink of the page's `html` output, `year` and `month` come from the page date.

## Enabling

```toml
[mediaTypes]
  [mediaTypes."text/bibtex"]
    suffixes = ["bib"]

[outputFormats]
  [outputFormats.bibtex]
    mediaType = "text/bibtex"
    baseName = "citation"
    isHTML = false
```

Then enable it per page:

```markdown
---
title: My page
outputs: ["HTML", "bibtex"]
cite: true
bibtex_key: my-key
authors:
  - first: Christian
    last: Mahnke
---
```

The generated file is available as `/page/citation.bib`.

## See also

- [Metadata formats](metadata-formats/) — CodeMeta and Linked Art
- [PDF article](pdf-article/) — printable article output, often enabled together with `bibtex`
