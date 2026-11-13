---
title: Metadata formats
params:
  displayinlist: false
  metaPage: true
---

# Metadata output formats

The theme can generate machine readable metadata descriptions of a site or page: schema.org JSON-LD, CodeMeta for software and Linked Art for cultural heritage objects.

## `schemaorg`

Template: `schema-org.json`, typically applied to the home page or a section. It renders a `WebSite` with a `Blog` (`hasPart`) containing all `BlogPosting` entries of the section's pages.

### Parameters

| Parameter | Type | Default | Purpose |
| --- | --- | --- | --- |
| `section` | string | `post` | Section the blog posts are taken from |
| `itemType` | string | `Blog` | `@type` of the blog node |

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

Templates: `single.linkedart.json` and `linked-art-collection.json`. Render [Linked Art](https://linked.art/) JSON-LD via the `metadata/linked-art/` partials — for single objects (e.g. postcards or works, see the `media/` partials) and for collections. Entity labels are resolved from Wikidata with the `wikidata-label.html` partial.

### Enabling

```toml
[outputFormats]
    [outputFormats.linkedart]
        mediaType = "application/ld+json"
[outputs]
    page = ["HTML", "linkedart"]
```

## Validation

The theme ships scripts to validate the generated IIIF and Linked Art documents, they are typically run against the build output after `hugo`:

```shell
./themes/projektemacher-base/scripts/validate-iiif.sh docs
./themes/projektemacher-base/scripts/validate-linked-art.py docs
```

- `validate-iiif.sh` uses the [official Presentation API validator](https://github.com/IIIF/presentation-validator) and validates all `manifest.json` and `collection.json` files. The API version is detected from the `@context`, versions 2.0, 2.1, 3.0 and 4.0 (draft) are supported. The validator command can be overridden with `IIIF_VALIDATOR`, the validated versions with `IIIF_VERSIONS`.
- `validate-linked-art.py` validates single object documents (files named `linkedart.json`) against the official [JSON schemas](https://linked.art/api/1.0/schema_docs/). Collections (type `Set`) are skipped, as the schemas don't cover them. The schema source defaults to the [linked.art repository](https://github.com/linked-art/linked.art/tree/master/docs/api/1.0/schema) and can be changed with `LA_SCHEMA_BASE` or `--schema-base`, e.g. to pin a specific revision. Downloaded schemas can be cached with `LA_SCHEMA_CACHE` or `--cache`.

Both scripts expect the Python dependencies from the theme's `requirements.txt` (`iiif-validator` needs to be installed via `pip install git+https://github.com/IIIF/presentation-validator`).

## See also

- [IIIF templates](iiif-templates/) — the other JSON-LD output formats
- [Data lists](data-lists/) — internal JSON indexes
