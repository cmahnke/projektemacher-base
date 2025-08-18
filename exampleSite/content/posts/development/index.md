---
title: Developing shortcodes
displayinlist: false
metaPage: true
---

# Seting up

To use the example site locally you need to set up the language files:

```
./scripts/setup.sh
```

# Running the example site

```
hugo --themesDir ../.. --printI18nWarnings --printUnusedTemplates
```

Afterwards the example site can be generated or `serve`'d.

# Cleaning up

Before commiting changes one can clean up the language files:

```
./scripts/cleanup.sh
```
