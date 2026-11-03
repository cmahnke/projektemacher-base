---
title: iiif/iiif
params:
  displayinlist: false
  metaPage: true
---

# iiif/iiif

Embeds a single image via the [IIIF Image API](https://iiif.io/api/image/3.0/) using the OpenLayers based viewer: a uniquely named map div loading the `info.json`, with an optional share bar (download/manifest/page links).

## Parameters

| Parameter | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `src` | string | yes | — | URL of the image's `info.json` |
| `share` | any | no | `false` | Show share/download links |
| `hdr` | any | no | `false` | Enable HDR support in the viewer |
| `downloadURL` | string | no | — | Link target for the full-resolution download |

## Example

```text
{{</* iiif/iiif src="https://iiif.example.org/page0001/info.json" share="true" */>}}
```

## Live demo

Loads an [Image API 2 info.json](https://static.projektemacher.org/blaufusstoelpel/post/praline-18-1961/front/info.json) from the Blaufußtölpel blog with the share bar enabled:

{{< iiif/iiif src="<https://static.projektemacher.org/blaufusstoelpel/post/praline-18-1961/front/info.json>" share="true" >}}

## Assets

Provided by the shortcode metadata (loaded automatically via the [shortcode helper](/shortcodes/shortcode-helper/)): JS `ts/iiif-image-viewer.ts`, SCSS `scss/iiif.scss`. See [IIIF configuration](/iiif/configuration/) for the site-wide viewer settings.

**Not** provided by the metadata: the OpenLayers base CSS. The viewer is built on OpenLayers controls (`Zoom`, `FullScreen`, `Rotate`) and needs `ol/ol.css`, but the shortcode loads no CSS itself (see the header note in the shortcode file) — the site must include it. Two patterns (see ["SCSS not provided by metadata"](/shortcodes/shortcode-helper/#scss-not-provided-by-metadata) for details):

- Per page, via the front matter `scss` parameter:

  ```yaml
  scss:
    - scss/ol-iiif.scss
  ```

  `scss/ol-iiif.scss` bundles the OpenLayers base CSS plus the viewer's rotate/undo icons.
- Site wide, from the site's `assets/scss/base.scss`:

  ```scss
  @use "ol-iiif";
  ```

  … or with a variable override:

  ```scss
  @use "ol-iiif" as * with (
    $icon-fill: #000
  );
  ```

## Notes

- An `includeSources` parameter mentioned in the file header is currently unused (that js.Build path is commented out)
- The OpenLayers CSS requirement above reflects a metadata gap that is tracked as cleanup work in the theme's [upgrade guide](https://github.com/cmahnke/projektemacher-base/blob/main/Upgrade.md#shortcode-scss-metadata-openlayers-css-not-covered-needs-cleanup)
