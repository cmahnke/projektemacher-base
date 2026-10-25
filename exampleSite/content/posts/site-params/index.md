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
  # Dynamic font preloading: the @font-face sources of the compiled CSS are
  # emitted as <link rel="preload" as="font"> tags before the stylesheet.
  # 'fontPreloadPattern' is an optional Go regexp include filter - without it
  # every Fontsource subset referenced by the page's SCSS gets preloaded.
  fontPreload = true
  fontPreloadPattern = "latin"
```
