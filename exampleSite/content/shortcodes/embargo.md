---
title: embargo
params:
  displayinlist: false
  metaPage: true
---

# embargo

Time-gated content: the inner content is rendered only when the build time is at or after the `until` timestamp. "Now" is corrected to the newest post's date if any post is dated in the future (so scheduled posts don't leak embargoed content early).

## Parameters

| Parameter | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `until` | date | no | build time | Timestamp the content is released at (`time.AsTime` syntax) |

## Warnings

- `warnf "Future detected!"` — the newest page date lies in the future
- `warnf "Embargo broken for <path>"` — an embargo has expired and its content is shown

## Example

```text
{{</* embargo until="2026-12-24" */>}}
Secret content, revealed on Christmas.
{{</* /embargo */>}}
```
