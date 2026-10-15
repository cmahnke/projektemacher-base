---
title: mermaid
displayinlist: false
metaPage: true
---

# mermaid

Renders the inner content into `<pre class="mermaid">` for client-side rendering by [Mermaid.js](https://mermaid.js.org/).

```mermaid
graph LR
    A[Hugo] --> B[Shortcode helper]
    B --> C{Assets needed?}
    C -- yes --> D[Load per page]
    C -- no --> E[Nothing included]
```

## Parameters

| Parameter | Type | Required | Purpose |
|---|---|---|---|
| `class` | string | no | Extra class on the `<pre>` element |

The inner content is the Mermaid diagram definition.

## Example

```text
{{</* mermaid */>}}
graph TD
    A --> B
{{</* /mermaid */>}}
```

## Assets

Via the shortcode helper: JS `js/mermaid.js`.

## Errors

- `errorf "[shortcodes/mermaid/block.html] Empty content for mermaid in <page>"` when the inner content is empty
