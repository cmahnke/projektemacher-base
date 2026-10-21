---
title: Webmentions
description: "Example page demonstrating the webmention/pingback integration"
displayinlist: false
metaPage: true
---

The theme advertises a [webmention](https://www.w3.org/TR/webmention/)
endpoint in the document head when `params.webmentions.endpoint` is
configured:

```toml
[params.webmentions]
  endpoint = 'https://webmentions.example.org/endpoint.php'
  advertisePingback = true
```

Received mentions are collected by the theme's
[PHP collector](https://github.com/cmahnke/projektemacher-base/blob/main/services/webmentions/README.md),
synced to the repository's `webmentions` data branch and fetched into
`data/webmentions/mentions.json` at build time. The list below renders
the entries for this page (sample data for this demo):

{{< webmentions >}}
