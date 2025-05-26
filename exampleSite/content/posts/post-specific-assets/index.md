---
title:
displayinlist: false
metaPage: true
---

Make sure the `assets` directory is mounted (in `hugo.toml` or `config.toml`)

```
[module]
  [[module.mounts]]
      source = "assets/scss"
      target = "assets/scss"

  [[module.mounts]]
      source = "assets/js"
      target = "assets/js"

  [[module.mounts]]
      source = "assets/ts"
      target = "assets/ts"
```


Add a reference to the front matter
```
scss: scss/tag-ring/tag-ring.scss
js:
  - ts/tag-ring/tag-ring.ts
```
