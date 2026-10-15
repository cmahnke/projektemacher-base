---
title: IIIF
displayinlist: false
metaPage: true
---

# IIIF support

This theme generates [IIIF](https://iiif.io/) resources at three levels:

- **Manifests** ([Presentation API](https://iiif.io/api/presentation/3.0/)) — one manifest per page opt-in, rendering the page's `resources` as canvases. Selected via the `iiif-manifest` output format.
- **Collections** ([Presentation API](https://iiif.io/api/presentation/3.0/)) — aggregations of manifests on home and term pages. Selected via the `iiif-collection` output format.
- **Images** ([Image API](https://iiif.io/api/image/3.0/)) — tile generation is handled outside of Hugo, see `scripts/iiif.sh`.

## Presentation API versions

| Version | Status | Context |
|---|---|---|
| 3 | Default, stable | `http://iiif.io/api/presentation/3/context.json` |
| 4 | Draft (4.0.0-draft) | `http://iiif.io/api/presentation/4/context.json` |

The version is selected per page or globally, see [Presentation 4](presentation-4/).

## Presentation API 2 is no longer supported

Generation of Presentation API 2 manifests (the former `iiif` output format with `sc:Manifest`/`sc:Sequence` vocabulary, templates `_default/single.json` and `_default/single.iiif.json`) has been phased out. Building a page still using `iiifContext` with a `presentation/2` context aborts the build with an error.

**Migration path:**

1. Set `outputs` to include `iiif-manifest` instead of `iiif`
2. Move manifest front matter to the `iiif.` namespace, see [Page metadata](page-metadata/). Notably `iiifMetadata` → `iiif.metadata` and `iiifStructure` → `iiif.structure`
3. `iiifAttribution` is replaced by `iiif.requiredStatement`, `iiifLogo` by `iiif.logo`

## Pages in this section

- [Configuration](configuration/) — site level `hugo.toml` settings
- [Page metadata](page-metadata/) — front matter reference for manifests and viewers
- [Presentation 3](presentation-3/) — working example generating an API 3 manifest
- [Presentation 4](presentation-4/) — the version switch, draft caveats and an API 4 manifest example
- [IIIF shortcodes](/shortcodes/iiif/iiif/) and [iiif/presentation](/shortcodes/iiif/presentation/) — embedding viewers in markdown (part of the [shortcodes section](/shortcodes/))

## See also

- Site params overview: [Site params](/posts/site-params/)
- Mirador viewer build requirements: [Mirador](/posts/mirador/)
