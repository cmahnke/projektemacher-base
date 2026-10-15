---
title: html/include
displayinlist: false
metaPage: true
---

# html/include

Includes the content of an external HTML file — everything between its `<body>…</body>` — inside a `div.included-html`. The path is resolved relative to the page's file directory via the partial `html/html-body.html`, see [shortcode helper: file includes](../shortcode-helper/#file-includes-from-shortcodes).

## Parameters

| Parameter | Type | Required | Purpose |
|---|---|---|---|
| `file` | string | yes | Path relative to the page directory |

## Example

```text
{{</* html/include file="extra.html" */>}}
```

## Errors

Inherited from `html/html-body.html`:

- `errorf "Can't find <file>!"` — file doesn't exist
- `errorf "…Contents of <file> is nil…"` / `errorf "<file> is either empty!"` — unusable content
- `errorf "Cant find context or src in…"` — called with unusable arguments
