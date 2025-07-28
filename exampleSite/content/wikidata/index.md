---
title: Wikidata
displayinlist: false
metaPage: true
---

# Templates

The most important part of the Wikidata integration is the enhanced link handling in `layouts/_default/_markup/render-link.html`

# Security

```
[security]
  [security.http]
    mediaTypes = ['^application/json$', '^application/json;\s?charset=[uU][tT][fF]-8$', '^application/sparql-results\+json;\s?charset=[uU][tT][fF]-8$']
```

# Example query

```
curl -X GET -H "Accept: application/sparql-results+json" "https://query.wikidata.org/sparql?query=SELECT+%3Fitem+%3FitemLabel+%3FofficialWebsite+%3FofficialBlog+%3FonlineDatabaseURL+WHERE+%7B%0A++++++%3Fitem+wdt%3AP856+%3Chttps%3A%2F%2Fdsgvo-gesetz.de%2Fart-6-dsgvo%2F%3E+.+SERVICE+wikibase%3Alabel+%7B+bd%3AserviceParam+wikibase%3Alanguage+%22%5BAUTO_LANGUAGE%5D%2Cen%22+.+%7D%0A++++++OPTIONAL+%7B+%3Fitem+wdt%3AP856+%3FofficialWebsite+.+%7D+OPTIONAL+%7B+%3Fitem+wdt%3AP1581+%3FofficialBlog+.+%7D+OPTIONAL+%7B+%3Fitem+wdt%3AP1316+%3FonlineDatabaseURL+.+%7D%0A++++%7D"
```
