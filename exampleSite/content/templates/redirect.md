---
title: Redirects
params:
  displayinlist: false
  metaPage: true
---

# Redirect template

Template: `redirect/single.html`. Renders a page as an immediate client side redirect using a `<meta http-equiv="refresh">` tag and a canonical link, following [Dan North's approach to Hugo redirects](https://dannorth.net/hugo-redirects/).

The page is marked with `<meta name="robots" content="noindex">` so search engines ignore it.

## Front matter parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `target` | string | yes | — | URL to redirect to |

## Usage

```markdown
---
title: Old page
target: https://example.org/new-page/
---
```

To use it as the page layout:

```markdown
---
title: Old page
layout: single
target: https://example.org/new-page/
---
```

with the `redirect` output format configured for the page, e.g. via a custom `outputFormats` entry using the `redirect` template.

Hugo's own `url`/`aliases` based redirects are usually the better choice — this template is for cases where a real page is needed, e.g. to redirect from a URL that must serve a full HTML document.
