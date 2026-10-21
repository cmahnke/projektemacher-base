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

Via the shortcode helper: JS `ts/iiif-image-viewer.ts`, SCSS `scss/iiif.scss`. See [IIIF configuration](/iiif/configuration/) for the site-wide viewer settings.

## Notes

- An `includeSources` parameter mentioned in the file header is currently unused (that js.Build path is commented out)
- The OpenLayers CSS must be available, the header notes it's not loaded by the shortcode itself
