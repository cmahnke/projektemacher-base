---
title: gist
params:
  displayinlist: false
  metaPage: true
---

# gist

Embeds a [GitHub Gist](https://gist.github.com/) via its embed script.

## Parameters

Positional arguments:

| Position | Type | Required | Purpose |
| --- | --- | --- | --- |
| 0 | string | yes | GitHub user name |
| 1 | string | yes | Gist ID |
| 2 | string | no | File name within the gist (`?file=`) |

## Example

```text
{{</* gist cmahnke 1234567890abcdef */>}}
```

## Live demo

Embeds a [real gist](https://gist.github.com/cmahnke/5049d42cd6dabc19cfd6c85161947fa2):

{{< gist cmahnke 5049d42cd6dabc19cfd6c85161947fa2 >}}

The same gist, restricted to a single file:

{{< gist cmahnke 5049d42cd6dabc19cfd6c85161947fa2 indexer.py >}}
