---
title: bibtex
displayinlist: false
metaPage: true
---

# bibtex

Intended to convert a BibTeX file (a page resource) into structured output for citations.

> **Note:** This shortcode is not working yet — it intentionally fails the build with an `errorf` when used, so the site doesn't silently render broken citations.

## Parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `file` | string | yes | — | Path of the BibTeX page resource |

## Example

```text
{{</* bibtex file="references.bib" */>}}
```
