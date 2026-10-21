---
title: Metadata partials
displayinlist: false
metaPage: true
---

# Metadata partials

The `metadata/` partials build the JSON-LD documents for the [metadata output formats](../metadata-formats/). They can also be called from site templates to reuse parts of the metadata generation.

## schema.org

| Partial | Purpose |
| --- | --- |
| `metadata/schema.org/schema.org.html` | Dispatcher — selects the site provided template, see [extension points](extension-points/#schemaorghash-html-per-type-metadata) |
| `schema.org/home.html` | Home page metadata (shipped, overridable) |
| `schema.org/post.html` | Blog post metadata (shipped, overridable) |
| `metadata/schema.org/util/author.html` | Author entity from `author`/`authors` front matter or site parameters |
| `metadata/schema.org/util/about.html` | `about` entities |
| `metadata/schema.org/util/iiif.html` | IIIF related entities |

Author related site parameters: `schemaPerson`, `publisher`, `orcid`, `author`, `authors`.

## CodeMeta

`metadata/codemeta/codemeta.json` builds a [CodeMeta](https://codemeta.github.io/) document for software pages. It supports `CITATION.cff` parsing:

| Front matter parameter | Purpose |
|---|---|
| `cfffile` | Path or URL of the CFF file (default `CITATION.cff`) |

The parsing itself lives in `metadata/codemeta/parse-cff.html` and can be called separately.

## Linked Art

The `metadata/linked-art/` partials build [Linked Art](https://linked.art/) JSON-LD documents — `linked-art.json` (entry point), `actor.json`, `collection.json`, `description.json`, `referenced_by.json`, `style.json` and label lookups:

- `wikidata-label.json` / `getty-label.json` resolve entity labels from [Wikidata](https://www.wikidata.org/) and the Getty thesaurus
- The SPARQL endpoint can be configured with the site parameter `wikidatasparqlendpoint`
- The site parameter `linkedart` carries Linked Art specific configuration

See also the [`linkedart` output format](../metadata-formats/#linkedart) and the [Wikidata helpers](helpers/#wikidata).
