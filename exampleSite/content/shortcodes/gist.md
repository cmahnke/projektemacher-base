---
title: gist
displayinlist: false
metaPage: true
---

# gist

Embeds a [GitHub Gist](https://gist.github.com/) via its embed script.

## Parameters

Positional arguments:

| Position | Type | Required | Purpose |
|---|---|---|---|
| 0 | string | yes | GitHub user name |
| 1 | string | yes | Gist ID |
| 2 | string | no | File name within the gist (`?file=`) |

## Example

```text
{{</* gist cmahnke 1234567890abcdef */>}}
```
