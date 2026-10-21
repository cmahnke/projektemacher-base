---
title: QR codes
params:
  displayinlist: false
  metaPage: true
---

# QR code templates

The `qrcode` output format generates a small JSON file per page describing the data to encode as a QR code — the actual image generation happens client side. Templates: `_default/single.qrcode.json` (pages) and `_default/section.qrcode.json` (sections).

## Output

```json
{
  "url": "https://example.org/page/",
  "color": "#000000",
  "icon": "…",
  "iconColor": "…"
}
```

- `url` is the permalink of the page's HTML output. If the page defines `aliases`, `url` becomes an array containing the permalink plus all alias URLs
- the remaining fields are optional and only rendered if the corresponding front matter parameters are set

## Front matter parameters

| Parameter | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `aliases` | string list | no | — | Additional URLs to encode |
| `qr-color` | string | no | — | QR code color |
| `qr-icon` | string | no | — | Icon (image) overlaid on the code |
| `qr-icon-color` | string | no | — | Color of the overlaid icon |

## Enabling

The output format is defined in the site configuration (see the [example site](https://github.com/cmahnke/projektemacher-base/blob/main/exampleSite/hugo.toml)):

```toml
[mediaTypes]
  [mediaTypes."application/x-qrcode-template"]
    suffixes = ["json"]

[outputFormats]
  [outputFormats.qrcode]
    mediaType = "application/x-qrcode-template"
    isPlainText = true
    isHTML = false
    baseName = "qrcode"
    notAlternative = true
```

Then enable it per page:

```markdown
---
title: Flyer
outputs: ["HTML", "qrcode"]
qr-color: "#000000"
---
```

The generated file is available as `/page/qrcode.json`.
