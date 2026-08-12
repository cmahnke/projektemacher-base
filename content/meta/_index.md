---
title: "Meta"
metaPage: true
displayinlist: false
archive: false
news: false
sectionContent: false
sitemap:
  disable: true
cascade:
  - target:
      kind: '{page,section}'
      lang: de
      path: '**'
    params:
      archive: false
      news: false
      sitemap:
        disable: true
---

Diese Seite bietet einige statistische Auswertungen und Daten über die Beiträge als JSON Dateien

* [Tags](./tags/index.json) des Blogs
* [Wikidata URIs](./wikidata/index.json) für Beiträge im Blog
