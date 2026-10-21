---
title: flag
params:
  displayinlist: false
  metaPage: true
---

# flag

Renders a language flag image (`/images/lang/<lang>.gif`, provided by the **site**) with the localized language name as `alt` text.

## Parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| *(positional 0)* | string | yes | — | Language code, also used as i18n key for the `alt` text |

## Example

```text
{{</* flag de */>}}
```

## Assets

None.
