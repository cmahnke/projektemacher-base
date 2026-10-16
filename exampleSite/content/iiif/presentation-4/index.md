---
title: Presentation 4 (draft)
displayinlist: false
metaPage: true
outputs: [html, iiif-manifest]
iiif:
  presentationVersion: 4
resources:
  - name: page0001
    src: cc.png
    params:
      iiif: tiles/page0001/info.json
---

# Presentation API 4 draft

The theme supports generating [Presentation API 4](https://iiif.io/api/presentation/4.0/) (version 4.0.0-draft) manifests. The draft is structurally compatible with API 3 — the templates in `layouts/partials/iiif/3/` are the single implementation, `layouts/partials/iiif/4/manifest.json` only delegates and serves as the place for future API 4 specific overrides. Currently only the `@context` differs. The same applies to the leaflet layout: `layouts/partials/iiif/4/manifest-leaflet.json` delegates to the shared API 3 implementation, see [Page metadata](../page-metadata/#leaflet-mode).

## Version switch

The version is resolved with the following priority:

1. **Page metadata** — `iiif.presentationVersion` in front matter
2. **Site config** — `[params.iiif] presentationVersion`
3. **Default** — `3`

Site-wide switch:

```toml
[params.iiif]
  presentationVersion = 4
```

Per page (allows mixing API 3 and API 4 manifests in one site):

```yaml
---
title: Example
outputs: [html, iiif-manifest]
iiif:
  presentationVersion: 4
---
```

Any value other than `3` or `4` aborts the build.

## Draft caveats

- The context `http://iiif.io/api/presentation/4/context.json` is served from the draft — expect changes until 4.0.0 is stable
- Collections are still generated as API 3, the version switch only affects manifests
- Viewers (TIFY, Mirador) may not render API 4 manifests yet — verify with each release
- Since the `iiif-manifest` output format is shared, P3 and P4 manifests can't be emitted for the same page simultaneously
