# Deprecations and shims

This document tracks everything that is deprecated or only kept alive
through a compatibility shim — in this theme **and** in its known
consumer sites (the top-level sibling repositories; the
`projektemacher/blogs/*` mirrors and `wilmabraeuner-complete` are
tracked separately) — together with the work needed to get rid of it.
Items marked 🔴 are **urgent to fix** — they are scheduled for removal
in an upcoming release and should be resolved before the next one.
Step-by-step instructions for past migrations live in the
[Upgrade.md](Upgrade.md) guide.

## Summary

| Item | State | Priority |
|---|---|---|
| `partials/head.html` | **removed** — baseof.html composes `html/head/meta.html` + `html/head/links.html` instead | done |
| JS shims in `assets/js/` | **removed** — all shims deleted, `assets/ts/` is the only source location | done |
| Legacy `iiifManifest` front matter key | **removed** — fallbacks dropped from `existing-manifest.html`, `iiif/3/collection.json` and `iiif-presentation.html` | done |
| Legacy font formats (`.eot`, `.svg`, `.ttf` fallbacks) | **removed** from the font SCSS | done |
| Legacy font file name copies | **removed** — `copy_legacy_font()` dropped from `scripts/fonts.sh`, `alata-regular.scss` migrated to Fontsource names, tracked `alata-regular-webfont.*` deleted | done |
| Stale Mirador references | fixed — dangling links and docs removed | done |
| Presentation API 2 guards | removed — guard templates (`single.json`, `single.iiif.json`) and legacy-key tripwires (`common.json`, `structures.html`) deleted; no legacy usage remains | done |
| Consumer overrides of deprecated theme parts | cleaned — hptz's forked `collection.json` replaced by the new `place-label.json` label hook, vorsatzpapier's stale `iiif-presentation.html` fork deleted, dead `iiifmanifest` conditions simplified in never-built, labs and wilmabraeuner | done |
| `disableScale` / `paginate` params in site configs | removed from all top-level consumer sites (`params.paginate` was never read; the theme's `disableScale` handling is deleted — unknown params are ignored by Hugo) | done |
| Fonts in `static/fonts/` | generated from npm; documented exceptions only | keep (exceptions stay) |
| SCSS `@import` usage | deprecated by Dart Sass, must become `@use` | medium |
| Outdated Hugo constructs | see the table in [Upgrade.md](Upgrade.md) | medium |
| Hugo < 0.165 compatibility code | removable since Hugo 0.166 | low |
| Third-party scripts loaded from CDNs | A-Frame via npm (`ts/aframe.ts`), Mastodon embed vendored (`assets/js/vendor/mastodon-embed.js`) | done |
| Hugo v0.156 deprecations (`.Sites`, `site.Data`, `site.AllPages`, `site.BuildDrafts`) | `.Sites`/`site.Data`/`site.AllPages` fixed across theme + consumers; `site.BuildDrafts` (5×, 4 repos) and blaufusstoelpel's `hugo.Data.Pages` still open — see the section below | medium |

## JavaScript assets

### `static/` — clean

There are no JavaScript files in `static/` or `exampleSite/static/`:
all scripts ship from `assets/` and go through the asset pipeline.
Nothing to do here.

### `assets/js/` — removed

The `assets/js/` directory has been deleted: every script lives in
`assets/ts/` now (see the "Upgrading shortcode scripts from
`assets/js` to TypeScript" section in [Upgrade.md](Upgrade.md)). Sites
referencing the old `js/` paths get a build error from
`html/head/script.html` and must switch to the `ts/` paths. No known
consumer references the old paths anymore.

Already removed earlier (sites must have migrated): `search.js`,
`timeline.js`, `iiif/mirador.js`, `maps/projektemacher-map.js`,
`fullscreen.js`.

## IIIF Presentation API 2 support (removed)

Generation of Presentation API 2 manifests is no longer supported; the
former guard templates and tripwires have been removed entirely — no
known site ever still used them:

- `layouts/_default/single.json` and `layouts/_default/single.iiif.json`
  (the API-2 guard templates) — deleted. Pages requesting a
  `presentation/2` context produce no manifest output at all
- the `iiifMetadata` / `iiifStructure` tripwires in
  `layouts/partials/iiif/3/common.json` — removed
- the legacy `type:` structure-entry guard in
  `layouts/partials/iiif/3/structures.html` — removed (current input
  validation for label/page/items entries stays)

The migration path is documented in "Upgrading IIIF Presentation API
2 → 3" in [Upgrade.md](Upgrade.md).

### Legacy fallbacks (removed)

The `iiifManifest` fallback in `layouts/partials/iiif/existing-manifest.html`
has been removed — only the `iiif.manifest` front matter key is read now.
The same legacy-key reads in `partials/iiif/3/collection.json` and
`partials/iiif/iiif-presentation.html` are gone as well. No consumer
content ever used the flat key, so this is a no-op for all known sites.

## Mirador viewer (removed)

The Mirador based presentation viewer has been removed; TIFY is the
only presentation viewer (see "Deprecation of the Mirador viewer" in
[Upgrade.md](Upgrade.md)). The former cleanup items (the dangling
`/posts/mirador/` links in `exampleSite/content/shortcodes/iiif/presentation.md`
and `exampleSite/content/iiif/_index.md`, the removed partial's row in
`exampleSite/content/templates/partials/iiif-partials.md` and the
shortcode comment in `layouts/shortcodes/iiif/presentation.html`) have
been fixed.

## Fonts in `static/fonts/`

Everything in `static/fonts/` is generated by `scripts/fonts.sh` from
the Fontsource npm packages listed in `fonts/package.json` and is
gitignored — do not commit or edit those files. The backwards-
compatibility leftovers have been removed:

- ~~**Legacy file name copies**~~: `copy_legacy_font()` is gone from
  `scripts/fonts.sh`; font SCSS uses the Fontsource file names.
- ~~**Legacy formats**~~: the font SCSS no longer declares `.ttf`, `.eot`
  or `.svg` fallbacks — only `.woff2`/`.woff`.
- ~~**Legacy-named tracked files**~~: `static/fonts/alata-regular-webfont.*`
  deleted; `assets/scss/fonts/alata-regular.scss` references the
  Fontsource names now.

### Exceptions — fonts not available on npm (keep)

These git-tracked files have no npm source and stay in `static/fonts/`:

- `static/fonts/DSBehrensschrift.otf` / `.ttf`
- `static/fonts/FuturaRenner-Regular.*` (`.eot`, `.svg`, `.ttf`,
  `.woff`, `.woff2`)

## Other deprecated remainders

- **SCSS `@import`**: the theme still uses `@import` throughout the
  SCSS sources; Dart Sass deprecates it in favour of `@use`. Several
  consumers (`backsteinexpressionismus`, `christianmahnke`,
  `xn--h-zfa.xyz`, `never-built`) import theme partials by path and
  must be migrated in the same pass. See the migration section in
  [Upgrade.md](Upgrade.md). (medium)
- **Outdated Hugo constructs** (medium):
  - *theme*: only `.Scratch` remains (7 partials; the `footer` /
    `iiifPrefix` Scratch keys are consumer-coupled — see below)
  - *consumers*: `.Site.` (6+ sites, e.g. `kleiderbuegel` in 26 files),
    `.Scratch` (8 sites), bare `substr` → `strings.Substr`
    (`kleiderbuegel` 8×, `labs.projektemacher.org`, `never-built`,
    `ric-unknownartist`)
  - *fixed in the 2026-10 cleanup*: `.RSSLink` (vorsatzpapier),
    `.LastChange` (schatten), removed `preserveTaxonomyNames`
    (christianmahnke, never-built, plastikwarenfabrik), `paginate`
    params (all known consumers), `readFile` → `os.ReadFile`
    (theme, labs.projektemacher.org, ric-unknownartist), `.Hugo.*` →
    `hugo.*` (labs.projektemacher.org, wilmabraeuner) — all modern
    `hugo.IsServer` / `hugo.IsMultilingual` now, no legacy config keys
- **Hugo < 0.165 compatibility code**: single-`return` partial
  workarounds in `layouts/partials/iiif/3/structures.html`,
  `functions/iiif/coerce-language-map.html` and
  `functions/iiif/structure-span.html` can be dropped with Hugo 0.166
  as the minimum. (low)
- ~~**Third-party scripts from CDNs**~~: fixed — the `aframe-3d-model`
  shortcode bundles the `aframe`/`aframe-orbit-controls` npm packages via
  `ts/aframe.ts` (the former `aframe.io`/`unpkg.com` URLs are gone), and
  the `mastodon` shortcode serves a pinned copy of the embed script from
  `assets/js/vendor/mastodon-embed.js` instead of `fosstodon.org`. (done)
- ~~**File name typo**~~: `assets/scss/fonts/noto-serif-dispaly.scss` was
  renamed to `noto-serif-display.scss` (no importer of the misspelled
  name existed; imports of the correct name now resolve). (done)

## Hugo v0.156 deprecations

Hugo 0.156 deprecated the site/page `Data`/`Sites` accessors plus
`AllPages`, `BuildDrafts` and `Languages` (info log now, warnings in
~3 months, errors in ~12 months). State across the theme and its known
consumers:

- ~~**`.Sites` (page method)**~~ → `hugo.Sites`: fixed in the theme
  (`footer-content.html`), `labs.projektemacher.org`,
  `wilmabraeuner`, `projektemacher` and `schatten`. (done)
- ~~**`site.Data`**~~ → `hugo.Data`: fixed in `christianmahnke`
  (schema.org partials), `never-built` (scrollify) and `projektemacher`
  (archive). (done)
- ~~**`site.AllPages`**~~: the theme's `hugo/site/AllPages` wrapper
  partial already uses the modern `range hugo.Sites` pattern and serves
  `post-list.json`, `kleiderbuegel` and `never-built`;
  `wilmabraeuner`'s `alias-resolver.html` now calls the wrapper too. (done)
- **`site.BuildDrafts`**: still used in the theme (`menu.html`) and the
  consumers `christianmahnke`, `kleiderbuegel` (2×) and `wilmabraeuner`
  — needs a semantic rework (draft pages don't render in production
  builds anyway). (open)
- **`hugo.Data.Pages` in `blaufusstoelpel`** (`list.html:20`): the site
  has no `data/` directory, so this paginates `nil` — intent unclear
  (probably `site.RegularPages`). (open, investigate)
- **Dead `[privacy.instagram]` blocks** removed from `christianmahnke`,
  `never-built` and `plastikwarenfabrik` — the Instagram shortcode was
  removed from Hugo, the keys were no-ops. (done)
