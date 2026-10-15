---
title: dates/lastmod
displayinlist: false
metaPage: true
---

# dates/lastmod

Renders the current page's `Lastmod` date as `<date class="lastmod">` using the `:date_medium` layout.

Last modified: {{< dates/lastmod >}}

## Parameters

None.

## Example

```text
Last modified: {{</* dates/lastmod */>}}
```

## Note

Results may be misleading with `enableGitInfo` — `Lastmod` then reflects the last Git commit of the page.
