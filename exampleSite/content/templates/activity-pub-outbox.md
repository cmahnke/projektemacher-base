---
title: ActivityPub outbox
displayinlist: false
metaPage: true
---

# ActivityPub outbox

The `activity-pub-outbox` output format renders an ActivityStreams `OrderedCollection` (`outbox.json`) listing recent posts as `Create`/`Note` objects.

Reference implementation: `christianmahnke/layouts/_default/home.activity-pub-outbox.json`. The theme ships no ActivityPub templates — copy or adapt that template if the format is needed.

## Output

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "OrderedCollection",
  "totalItems": 2,
  "orderedItems": [
    {
      "type": "Create",
      "actor": "https://example.org@example",
      "object": {
        "type": "Note",
        "content": "<a href=\"https://example.org/post/my-page/\">My page</a>",
        "to": "https://www.w3.org/ns/activitystreams#Public",
        "published": "2024-04-15T13:58:44+02:00"
      }
    }
  ]
}
```

Pages come from section `post` and exclude pages with `displayinlist: false`. The `actor`/`attributedTo` fields are only rendered if `[params.activitypub] author` is set.

## Site parameters

| Parameter | Type | Default | Purpose |
| --- | --- | --- | --- |
| `params.activitypub.author` | string | — | Username used to build the `actor` URL (`<baseURL><author>`) |
| `params.activitypub.outbox` | string | — | Outbox filename appended to the base URL |
| `params.Description` | string | — | Rendered as collection `summary` if set |

## Enabling

```toml
[mediaTypes]
  [mediaTypes."application/activity+json"]
    suffixes = ["json"]

[outputFormats]
  [outputFormats.activity-pub-outbox]
    mediaType = "application/activity+json"
    isPlainText = true
    isHTML = false
    baseName = "outbox"
    notAlternative = true
```

```toml
[params.activitypub]
  author = "example"
  outbox = "outbox.json"
```

Typically enabled on the home page via `[outputs] home = ["HTML", "activity-pub-outbox"]`. The generated file is available as `/outbox.json`.

## See also

- [ActivityPub actor](activity-pub-actor/) — the `Person` counterpart
