---
title: Site parameters
description: "Example page demonstrating site wide parameter usage"
params:
  displayinlist: false
  metaPage: true
---

```toml
[params]
  js = "esm"

[params.iiif]
  presentationViewer = "ts/iiif/tify.ts"

[params.css]
  includeDirs = ["node_modules/tify/dist/"]
```
