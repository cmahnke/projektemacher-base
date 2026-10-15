---
title: print/env
displayinlist: false
metaPage: true
---

# print/env

Renders the inner content (through `$.Page.RenderString`) only when the Hugo environment is `print` — used to add content that appears exclusively in the print edition.

See the [print edition shortcodes](../) (`print/*`) for related shortcodes.

## Parameters

None (inner content only).

## Example

```text
{{</* print/env */>}}This paragraph only appears in the print build.{{</* /print/env */>}}
```
