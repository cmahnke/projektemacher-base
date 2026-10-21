---
title: ActivityPub actor
displayinlist: false
metaPage: true
---

# ActivityPub actor

The `activity-pub-actor` output format renders an ActivityStreams `Person` object (`actor.json`) describing the site owner for static ActivityPub discovery.

Reference implementation: `christianmahnke/layouts/_default/single.activity-pub-actor.json`. The theme ships no ActivityPub templates — copy or adapt that template if the format is needed.

## Output

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Person",
  "url": "https://example.org/",
  "discoverable": true,
  "name": "Example site"
}
```

Depending on the `[params.activitypub]` configuration, `id`/`preferredUsername`, `outbox`, `icon`, `image` and an `attachment` list of `PropertyValue` link entries are added.

## Site parameters

| Parameter | Type | Default | Purpose |
| --- | --- | --- | --- |
| `params.activitypub.author` | string | — | Username used for `id` (`<baseURL>@<author>`) and `preferredUsername` |
| `params.activitypub.outbox` | string | — | Outbox filename appended to the base URL, e.g. `outbox.json` |
| `params.activitypub.icon` | string | — | Asset path resolved with `resources.Get` for the `icon` image |
| `params.activitypub.image` | string | — | Asset path resolved with `resources.Get` for the `image` |
| `params.activitypub.links` | map | — | Name to HTML link mapping rendered as `attachment` |
| `params.Description` | string | — | Rendered as `summary` if set |

## Enabling

```toml
[mediaTypes]
  [mediaTypes."application/activity+json"]
    suffixes = ["json"]

[outputFormats]
  [outputFormats.activity-pub-actor]
    mediaType = "application/activity+json"
    isPlainText = true
    isHTML = false
    baseName = "actor"
    notAlternative = true
```

```toml
[params.activitypub]
  author = "example"
  icon = "images/logo.png"
  image = "images/background.jpg"
  outbox = "outbox.json"
```

Enable it per page via `outputs`, the generated file is available as `/page/actor.json`.

## See also

- [ActivityPub outbox](activity-pub-outbox/) — the `OrderedCollection` counterpart
