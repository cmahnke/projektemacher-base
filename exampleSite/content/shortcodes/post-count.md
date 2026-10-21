---
title: post-count
displayinlist: false
metaPage: true
---

# post-count

Outputs the number of pages in a section, optionally filtered by the front matter `type` parameter.

## Parameters

| Parameter | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `section` | string | yes | — | Section name |
| `type` | string | no | — | Filter on the pages' `type` front matter |

## Example

There are {{< post-count section="shortcodes" >}} pages in this section.
