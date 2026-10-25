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
  # Absolute font URLs in the compiled CSS are rewritten to stylesheet-
  # relative ones ('url(/fonts/…' → 'url(../fonts/…'), so fonts also load
  # on subpath deployments (e.g. GitHub Pages). Set to false to disable.
  fontURLRewrite = true
```
