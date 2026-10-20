---
title: Quality assurance scripts
displayinlist: false
metaPage: true
---

The theme ships a set of quality assurance scripts, used by the [example site](../development/) and by sites built on this theme in their CI workflows.

# Browser check

`scripts/github/check-js-errors.sh` wraps `scripts/check-js-browser-errors.mjs` and is the form used in GitHub Actions. The Node script serves the built site from the `docs` directory on an internal web server (`http://localhost:3000/`), loads every page from `test-urls.json` (or one URL per line from `test-urls.txt`) in headless Chrome and fails the run if a page emits errors:

- a browser console message matching one of the `messages` entries of `test-urls.json`
- an uncaught page error (`pageerror`)
- a request that fails or returns an error for a local resource

| Exit code | Meaning |
|---|---|
| 122 | Browser console message matched a configured `messages` entry |
| 123 | Uncaught page error |
| 124 | Failed or erroring request for a local resource |
| 125 | CSS selector found, but the property value didn't match the expectation |
| 126 | CSS selector not found |
| 127 | Missing IIIF asset (see below) |

Entries in `test-urls.json` can additionally contain `click` sequences and CSS `selector`/`property`/`value` (optionally with `pseudo`) assertions, checked with `getComputedStyle`.

| Flag | Meaning |
|---|---|
| `-f`, `--force` | Exit instead of skipping URLs whose file doesn't exist in `docs` |
| `-g`, `--gpu` | Enable 3D APIs (SwiftShader/ANGLE emulation), required by WebGL/WebGPU pages |
| `-e`, `--experimental` | Enable experimental web platform features |
| `-c`, `--config` | Path to the test configuration (JSON), defaults to `test-urls.json` |
| `-l`, `--log-server` | Log which files the internal web server served |
| `-i`, `--iiif` | Enable [IIIF awareness](#iiif-awareness) |

`scripts/github/puppeteer-chrome.sh` installs the Chrome build used by the check (`npx @puppeteer/browsers install chrome@stable`).

`scripts/github/check-js-errors-example.sh` runs the check against the example site itself. Pages whose JavaScript requires WebGL or WebGPU are deliberately not listed in `test-urls.json`, since the 3D APIs are disabled unless `-g` is passed.

# IIIF awareness

With `-i`/`--iiif` the check understands IIIF documents among the test URLs. A URL ending in `manifest.json`, `info.json` or `collection.json` is fetched from the internal web server and parsed; if the content is a valid IIIF document (Presentation `Manifest` or `Collection`, or Image API `info.json`), it is checked for referenced assets instead of being opened in the browser. Anything else is checked in the browser as usual.

The check only requests assets served by the internal web server, never external hosts, and only actual file references:

| Collected | Skipped |
|---|---|
| `thumbnail`, `rendering`, `logo`, `seeAlso` and annotation `body` ids | Structural identifiers that merely look like URLs: Canvases, Annotations, Ranges, the document's own `id` |
| | `@context`, `homepage`, `provider`, `partOf`, `services`, `profile` |

For `manifest.json` and `collection.json` every referenced asset (deduplicated) is requested once. For `info.json` the check verifies the advertised derivatives: the canonical full image (`/full/max/0/default.jpg`, Image API 2 uses `/full/full/`), one request per advertised `sizes` entry and one representative tile per `tiles` entry and scale factor.

Failures are collected across all test URLs and reported at the end of the run:

```
IIIF check: 3 files, 42 URLs, 2 failures
```

Any failure exits with code 127.

# Accessibility

`scripts/check-a11y.mjs` runs [axe-core](https://github.com/dequelabs/axe-core) in headless Chrome against one or more URLs and reports accessibility violations.

| Flag | Meaning |
|---|---|
| `-u`, `--url` | URL to check (defaults to the `baseURL` from the Hugo configuration) |
| `-f`, `--urls-file` | JSON file with a `urls` array (e.g. `test-urls.json`), checked in addition to `--url` |
| `-o`, `--output` | Additionally write the report as Markdown to this file |
| `-c`, `--config` | Hugo configuration (TOML) to read the `baseURL` from |
| `-w`, `--wait` | Milliseconds to wait for the page to settle after load |
| `-i`, `--include-meta-viewport` | Include the `meta-viewport` rule |

# Lighthouse

`scripts/check-lighthouse.mjs` runs [Lighthouse](https://github.com/GoogleChrome/lighthouse) against one or more URLs and reports the category scores.

| Flag | Meaning |
|---|---|
| `-u`, `--url` | URL to check |
| `-f`, `--urls-file` | JSON file with a `urls` array, checked in addition to `--url` |
| `-o`, `--output` | Additionally write the report as Markdown to this file |
| `-c`, `--config` | Hugo configuration (TOML) to read the `baseURL` from |
| `-k`, `--categories` | Categories to run, from `performance`, `accessibility`, `best-practices`, `seo` |
