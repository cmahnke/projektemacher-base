---
title: Metadata formats
params:
  displayinlist: false
  metaPage: true
---

# Metadata output formats

The theme can generate machine readable metadata descriptions of a site or page: schema.org JSON-LD, CodeMeta for software and Linked Art for cultural heritage objects.

## `schemaorg`

Template: `_default/schema-org.json`, typically applied to the home page or a section. It renders a `WebSite` with a `Blog` (`hasPart`) containing all `BlogPosting` entries of the section's pages.

### Parameters

| Parameter | Type | Default | Purpose |
| --- | --- | --- | --- |
| `section` | string | `post` | Section the blog posts are taken from |
| `type` | string | `Blog` | `@type` of the blog node |

The author information comes from the `author`/`authors` front matter or site parameters, additional `about` entities are collected from the page metadata partials (`metadata/schema.org/`).

### Enabling

```toml
[outputs]
    home = ["HTML", "schemaorg"]
```

## `codemeta`

Template: `_default/single.codemeta.json`. Renders [CodeMeta](https://codemeta.github.io/) JSON for software pages. The metadata is built by the `metadata/codemeta/` partials, which can also parse `CITATION.cff` files (via `parse-cff.html`). The `@id` is set to the permalink of the `codemeta` output format itself.

### Enabling

```toml
[outputs]
    page = ["HTML", "codemeta"]
```

## `linkedart`

Templates: `_default/single.linkedart.json` and `_default/linked-art-collection.json`. Render [Linked Art](https://linked.art/) JSON-LD via the `metadata/linked-art/` partials — for single objects (e.g. postcards or works, see the `media/` partials) and for collections. Entity labels are resolved from Wikidata with the `wikidata-label.html` partial.

### Enabling

```toml
[outputFormats]
    [outputFormats.linkedart]
        mediaType = "application/ld+json"
[outputs]
    page = ["HTML", "linkedart"]
```

## See also

- [IIIF templates](iiif-templates/) — the other JSON-LD output formats
- [Data lists](data-lists/) — internal JSON indexes
