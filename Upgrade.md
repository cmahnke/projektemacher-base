# Outstanding deprecations

What is left is tracked here: deprecated or shimmed
items in this theme and its known consumers (the top-level sibling
repositories; the `projektemacher/blogs/*` mirrors are tracked separately,
and so is `wilmabraeuner-complete` — it still pins Hugo 0.124.1 and carries
legacy constructs like `.Site.` lookups, `substr`, `Scratch`,
`languageCode` and `.Params.description`). All remaining items are optional
or low priority; step-by-step instructions for past migrations are in the
rest of this guide. Upstream per-version fix notes (bep/myhugofixer,
v0.55.0 – v0.169.0) are shipped as the [`hugo-upgrade`
skill](skills/hugo-upgrade/SKILL.md) in `skills/hugo-upgrade/` — its
[fixes.md](skills/hugo-upgrade/fixes.md) carries the per-version notes.

| Item | State | Priority |
| --- | --- | --- |
| SCSS `@import` usage | deprecated by Dart Sass, must become `@use`. Pending consumers: `merch.projektemacher` and `projektemacher` (one `@import` left in each `assets/scss/base.scss` — coder leakage architecture). Kept by decision: `yaapb`'s `_bootstrap-subset.scss` shim and `wilmabraeuner`'s `@import "bootstrap"` (isolated vendor code pending Bootstrap 6 module support). Theme-side open: `assets/scss/services/cookie-consent.scss` still `@use "icons" as *` — schatten's pre-declared `$close-*`/`$color-*` would collide with it on the next submodule raise — see ["Migrate SCSS from `@import` to `@use`"](#migrate-scss-from-import-to-use) | medium |
| Hugo < 0.165 compatibility code | Consumer exception: `schatten` keeps `{{ template "_internal/opengraph.html" }}` in `layouts/baseof.html` in compatibility mode until a verified switch to `{{ partial "opengraph.html" }}` — see ["Remove downward compatibility (Hugo < 0.165.0)"](#remove-downward-compatibility-hugo--01650) | low |
| Reserved front matter `type` field looked up via `.Params` | theme migrated: the reserved shorthand field was renamed to the custom front matter parameter `itemType` (read via `.Params.itemType` inside the `params` section) in `schema-org.json`, `metadata/linked-art/collection.json`, `preview/preview-internal.html`, `_partials/page.html` and `_shortcodes/post-count.html`; consuming sites must rename their front matter keys and any site-side templates that read `type` through `.Params` — see ["Rename the reserved front matter `type` parameter"](#rename-the-reserved-front-matter-type-parameter) | low (consumer adoption) |
| JS bundle format | bundles are classic IIFE scripts; ESM (`type="module"`) is supported as an opt-in, `js.Batch` as the full switch — both optional. Pending: `christianmahnke` (its own `menu.html` already builds ESM, but the site config does not set the param, so main/page bundles stay IIFE), `diapraesentation`, `flohmarktfunde`, `flugzeugbesteck`, `haesslicheplastiktiereundzeugs`, `merch.projektemacher`, `plastikwarenfabrik`, `projektemacher`, `ric-unknownartist`, `vorsatzpapier`, `xn--h-zfa.xyz`, `yaapb` — see ["Switch the JS bundles from IIFE to ESM"](#switch-the-js-bundles-from-iife-to-esm) | low |
| Front matter `alias:` promotion | promoted to the standard `aliases:` in `ric-unknownartist`, `yaapb`, `labs.projektemacher.org`, `kinderbuecher`, `christianmahnke` (2026-10) — Hugo now generates redirect pages for those Tumblr-era IDs/paths (root-level `/<id>/` URLs, per-language scoping); kleiderbuegel's singular `tag:` stays under `params` (live `.Params.tag` term-page title fallback) | informational |
| Fonts in `static/fonts/` | generated from npm; documented exceptions only | keep (exceptions stay) |
| Webmention workflows: single deployment connection | collectors copied from this repository must adopt the one-connection layout (variables `DEPLOY_SERVER`/`DEPLOY_USER`/`DEPLOY_PATH`/`DEPLOY_PASS`, `scripts/webmention/host.sh`, split deploy + harvest workflows - deploy runs on commits only, the reusable harvest workflow chains onto it and also runs on the hourly cron; the collected data is committed as `data/webmentions/mentions.json` to the site's own `main` branch — direct Hugo data, the old `fetch.sh` branch flow is gone) — see [services/webmentions/README.md](services/webmentions/README.md) | low |
| PostCSS CSS deduplication | flows from the theme (`assets/_jsconfig/postcss.config.js` + `scripts/init/package.json.sh`) — no consumer-side config needed — see ["CSS pipeline: PostCSS deduplication added"](#css-pipeline-postcss-deduplication-added) | informational |
| Image shortcodes: configurable output format (`format` parameter / `[params.images]`) | opt-in; defaults keep the historical output, non-processable images (SVG, JXL, …) now pass through unchanged instead of failing the build — see ["Image shortcodes: configurable output formats"](#image-shortcodes-configurable-output-formats) | informational |
| Automated accessibility checks | theme ships no CI gate, only a ready-to-run reference implementation (`npm run check:a11y` / `npm run check:lighthouse`) — sites copy and adapt the setup to their own tooling — see ["Add accessibility checks"](#add-accessibility-checks) | informational |
| Shortcode SCSS metadata: OpenLayers base CSS not declared by `iiif/iiif` and `maps/osm-vector-tiles` | consumers work around the gap with a global `@use "ol-iiif"` in their `assets/scss/base.scss`: `blaufusstoelpel`, `kraehenbeisser`, `backsteinexpressionismus`, `kleiderbuegel` (`as *`) and `never-built` (with a `$icon-fill` variable override); `christianmahnke`'s `base.scss` carries a stale comment claiming the metadata covers it. Documented as site responsibility in the example site; long term cleanup open — see ["Shortcode SCSS metadata: OpenLayers CSS not covered (needs cleanup)"](#shortcode-scss-metadata-openlayers-css-not-covered-needs-cleanup) | low |

# Run the JS runtime check against the example site

The theme's CI now runs the puppeteer based runtime checker
(`scripts/check-js-browser-errors.mjs`) against the built example site:
the `test_js_errors` job in `.github/workflows/test.yml` builds
`exampleSite/` and serves the output (`exampleSite/docs/`) through the
checker's internal webserver — the same mechanism the consumer-side
`scripts/github/check-js-errors.sh` uses. Locally the check runs via
`./scripts/github/check-js-errors-example.sh`.

The URL list lives in `exampleSite/test-urls.json` and covers:

- one page per shortcode that ships JS — `audioplayer`,
  `browser-banner`, `browser-hide-selector`, `chart`, `code`,
  `csv-chart`, `gallery`, `gist`, `html/iframe-consent`, `hdr-canvas`,
  `hdr-canvas-check`, `hdr-check`, `iiif/iiif`, `iiif/presentation`,
  `lucienne`, `maps/osm`, `maps/osm-vector-tiles`, `mastodon`,
  `mermaid`, `pdf`, `pdf-preview` (`tagcloud` ships no JS — its demo
  page is only checked for styling)
- other pages with JS functionality: the search page (Pagefind, see
  below), the IIIF presentation examples, the i18n strings page with
  its client side table filter, the page specific assets post and the
  html-body test page

IIIF document URLs (manifests, collections, image `info.json`) can
additionally be checked for their referenced assets via the optional
IIIF awareness mode — see "Check IIIF documents with the browser check"
under Housekeeping below.

The checker also maps requests to the base URL's **origin root** to its
internal webserver, so root-relative resources like CSS
`url(/fonts/…)` load during the check even when the site is deployed
under a path (GitHub Pages project sites). Sites deployed at the origin
root are unaffected.

## Excluded: WebGL and WebGPU

Pages whose JS requires WebGL or WebGPU are deliberately not listed —
the checker runs with 3D APIs disabled (`--disable-gpu --disable-3d-apis`,
see the `-g` flag for GPU emulation via SwiftShader), so
`shortcodes/aframe-3d-model/`, `shortcodes/model/`,
`shortcodes/hdr-model/` and `posts/3d-model/` would either fail or
test nothing meaningful. Keep WebGL/WebGPU based JS out of the URL list
unless you run the check with `-g`.

## What sites need to do

Consuming sites run the same checker against their own build
(`scripts/github/check-js-errors.sh`) — make sure **one page per
shortcode that includes JS — whether defined by the theme or by the site
itself — and pages containing maps, PDF viewers, search and other JS
functionality are added to the site's `test-urls.json`, if not already
in there**, excluding WebGL/WebGPU (see above). The checker only visits
the URLs it is given, so anything missing from the list is never
runtime-checked. To find candidates:

```bash
# Pages using shortcodes that ship JS (one page per shortcode is enough)
grep -rEl '^{{< ?(maps/|pdf|iiif/|audioplayer|mermaid|lucienne|mastodon|browser-|gist|html/iframe-consent|code|chart|csv-chart|gallery|image-compare|hdr-)' content

# Site defined shortcodes with required includes
# (check the referenced metadata partial for a 'js' entry)
grep -rEl 'define ".*-metadata' layouts/shortcodes/

# Search pages (the theme's 'search' layout)
grep -rEl '^layout: search' content

# Pages loading page specific scripts
grep -rEl '^\s*js:' content
```

Keep the list in sync whenever a new shortcode with JS is added or a
page starts using JS functionality.

> [!NOTE]
> Search pages need the Pagefind index built for the served output
> (`pagefind-indexer`, see the deploy workflow) — without it the page
> renders, but the search bundle fails to load and returns no results.
> Since the failure is caught inside pagefind (console errors only),
> the checker doesn't fail on it, so index the build before running the
> check to test real search behaviour. The example site's runtime check
> builds the index before the check runs.

The same page set is the input for the accessibility checks (see
"Add accessibility checks" below) — run those against the production
site as well.

> [!NOTE]
> Complete — all known consumers now ship a `test-urls.json` (2026-10:
> `flohmarktfunde`, `haesslicheplastiktiereundzeugs`,
> `plastikwarenfabrik` and `kraehenbeisser` were the last ones without
> it). Keep the lists current when adding JS functionality.

# CSS pipeline: PostCSS deduplication added

Production builds now run the concatenated stylesheet through PostCSS
(`css.PostCSS` with `postcss-discard-duplicates`) after `resources.Concat`
and before `minify`. This removes rules duplicated across the individually
compiled SCSS resources and the plain CSS resources (around 20–25% smaller
output for the example site). The theme ships its PostCSS configuration as
`assets/_jsconfig/postcss.config.js`, which Hugo picks up automatically —
sites need no PostCSS configuration of their own.

> [!IMPORTANT]
> Hugo ≥ 0.161 runs Node tools like PostCSS with Node's `--permission` model
> (`security.node.permissions`). If a site overrides
> `security.node.permissions.allowRead`, the value **replaces** Hugo's default
> `['.']` — it is *not* merged. A list that omits the working directory or the
> project root breaks production builds, because Node's CJS resolver and
> Browserslist walk up the directory tree reading `package.json` and config
> candidates (`browserslist` file) and hit a denied path:
>
> ```text
> POSTCSS: failed to transform "/css/….css" (text/css): Error: Access to this
> API has been restricted. Use --allow-fs-read to manage permissions.
> ```
>
> When narrowing `allowRead`, always keep the working directory and the project
> root readable — for a build from a subdirectory (like this theme's
> `exampleSite/`):
>
> ```toml
> [security.node]
>   [security.node.permissions]
>     allowRead = ['.', '..', '../node_modules']
> ```
>
> Note that `hugo server` masks the problem, since the PostCSS dedupe step is
> skipped for the dev server. If a denial persists, the denied `resource` in
> the error's stack trace shows which path to add.

## What sites need to do

Nothing, if the site was set up with the theme's init scripts
(`scripts/init/package.json.sh`): the required packages (`postcss`,
`postcss-cli`, `postcss-discard-duplicates`) are part of the theme's
`package.json` and get merged into the site's `package.json`.

Otherwise install them once in the site root:

```bash
npm install --save-dev postcss postcss-cli postcss-discard-duplicates
```

## Behaviour and opt-out

- The step only runs for production builds — `hugo server` is unaffected.
- Disable it with:

```toml
[params.css]
  dedupe = false
```

- Without `postcss-cli` the build fails with Hugo's "You need to install
  PostCSS" error. If only the `postcss-discard-duplicates` package is
  missing, the build degrades gracefully and the CSS passes through
  unprocessed.
- A site's own `assets/_jsconfig/postcss.config.js` overrides the theme's.
  Note that Hugo resolves the configuration from `assets/_jsconfig/` first,
  so a `postcss.config.js` in the site root is no longer used for this
  pipeline.
- The exampleSite resolves its dependencies via the new
  `exampleSite/node_modules -> ../node_modules` symlink, since the build
  runs from `exampleSite/` with `--themesDir ../..`.

# Dynamic font preloading

`html/head/style.html` now extracts the `@font-face` source URLs from the
compiled page CSS and emits `<link rel="preload" as="font"
type="font/woff2" crossorigin>` tags before the stylesheet link — the same
partial that compiles the SCSS discovers the fonts dynamically, no manual
font list. Only woff2 is preloaded; `crossorigin` is required even for
same-origin fonts (without it the preloaded response is discarded and the
font fetched again).

Sites that don't want the tags can turn the feature off, the optional
pattern restricts the Fontsource subset files (e.g. `latin` also matches
`latin-ext`):

```toml
[params.css]
  fontPreload = false
  # fontPreloadPattern = "latin"
```

Behavioural notes:

- Only absolute path (`/fonts/…`) and absolute URL sources are preloaded —
  relative `@font-face` URLs resolve against the stylesheet URL and cannot
  be preloaded reliably from the page head.
- The preloads reflect the page's own stylesheet mix (page SCSS, shortcode
  CSS, …) — pages using `map.scss` preload EB Garamond, plain pages don't.
- No behaviour change beyond the added `<link>` tags; consumers overriding
  `style.html` keep their current head output until they adopt the change.

# Image shortcodes: configurable output formats

The image outputting shortcodes (`figure`, `gallery`, `image-compare`,
`post-image`) now accept a `format` parameter and can be configured site
wide via `[params.images]` (global `format`, per-shortcode
`[params.images.formats]`, string shorthand `[params] images = 'webp'`).
Defaults are unchanged: `gallery` keeps generating WebP, the other
shortcodes keep the image's source format. See the
[image parameters documentation](exampleSite/content/config/params/index.md)
for the resolution order and accepted values.

Behavioural notes:

- Non-processable image resources (SVG, JXL, HEIC, … — see
  [`reflect.IsImageResourceProcessable`](https://gohugo.io/functions/reflect/isimageresourceprocessable/))
  are passed through unchanged. Previously the shortcodes called
  `.Process`/`.Resize` unconditionally, so such resources failed the build.
- The gallery's processing specifications dropped Hugo's undocumented
  trailing `picture` token (`320x webp picture` → `320x webp`): the
  generated files are identical, but the option hash in their URLs changes.
- The OpenGraph preview (`preview.og.format`) is now also applied to
  prerendered preview images and `ogpreview` resources — but only when the
  site explicitly configures it; the implicit `jpeg` default never
  triggers a conversion.
- `post-image` without a `section` parameter crashed the build (it called
  `.GetPage` on the shortcode context, which doesn't exist) — it now uses
  the page's `.Page.GetPage`.

## What sites need to do

Nothing. Sites wanting WebP output add the configuration, e.g.:

```toml
[params.images]
  format = 'webp'
```

# Housekeeping

The changes in this section are **optional**: no consuming site has to apply
them to keep building against the current theme release. They bundle work that
keeps a site aligned with the theme's direction — finishing half-done
migrations, dropping dead compatibility code and adopting the theme's tooling.
Pick items as time allows; each one stands on its own.

## Switch the JS bundles from IIFE to ESM

Every JS bundle the theme emits is an esbuild IIFE: `js.Build` runs with
Hugo's default `format: "iife"` and produces a self-contained classic
script — no `import`/`export` statements — that `html/head/script.html`
loads with `defer`, fingerprinting and SRI. The same pattern covers the
main bundle and the page/shortcode bundles (`script.html`), the menu
script (`menu.html`, `js/menu.js`) and the print script
(`baseof.print.html`, `js/print.js`).

### Config-driven switch (Path A via site config)

`script.html` reads the bundle format from the site configuration when
the call does not pass its own `opts`:

```toml
[params.js]
  format = "esm"
```

… or the string shorthand `[params] js = 'esm'`. Per-call `opts.format`
still wins over the config; valid values are `esm` and `iife` (the
default). Setting the param makes every `script.html`-delivered bundle —
main, IIIF viewers and page scripts — build as ESM and ship as
`type="module"`. The menu script (`menu.html`, `js/menu.js`) follows the
same param: with the config set its build goes ESM and its tag ships as
`type="module"` (it stays a `defer` classic script otherwise). Sites with
copied `menu.html` builds need the same `"format"` addition in their own
opts — christianmahnke's copy already carries it; its missing piece is the
config param for the main/page bundles.

`script.html` also builds the `js` call parameter centrally:
string entries (asset paths, e.g. the IIIF viewers returned by
`iiif-js.html` after its script-handling refactor) are build entry points —
`js.Build` with the same opts as page scripts, including the `.ts` → `.js`
targetPath rename, so built output never leaks a `.ts` extension.
Resources passed via `js` are appended unbuilt. The partial **never
concatenates ESM bundles**: every bundle is fingerprinted individually and
ships as its own `<script type="module" … crossorigin="anonymous">` tag.
Module tags execute in document order, so the main bundle still runs
before page scripts. `splitBundles` only affects classic (iife) bundles.

There are two ways to switch to ES modules; both are optional — a site
picks one (Path B subsumes Path A's module semantics, see Risks below).

### Path A — opt in per bundle with `format: "esm"`

`html/head/script.html` already supports it:

```html
partial "html/head/script.html" (dict "context" . "opts" (dict "format" "esm"))
```

With `format` set to `esm` the partial emits `<script type="module">`
instead of the `defer` variant — modules are deferred implicitly, so the
timing stays the same. One opts pass covers all bundles built within the
call (main bundle, IIIF viewers, page scripts).

Steps:

1. Pass `"opts" (dict "format" "esm")` to the `script.html` call in the
   site's `baseof.html` (or default the format via the site config above,
   or in a site-side override of the partial).
2. `menu.js` and `print.js` can be switched one at a time by adding
   `"format" "esm"` to their `js.Build` options and changing their script
   tags to `type="module"` (drop `defer`, it is redundant on modules).
   Switch both branches of `baseof.print.html` (the development branch
   emits the tag without `defer` today). The `"target" "es2018"` of
   `print.js` is unrelated to the output format and can stay.

### Path B — switch the bundle pipeline to `js.Batch`

Hugo's `js.Batch` (available since Hugo 0.140.0, well above the theme's
0.165 floor) is the real code splitting path: `format` must be `esm`,
all entry points of a batch are bundled in one esbuild run, and shared
dependencies are extracted into shared chunks. Compared to Path A it
removes the concatenation step completely and deduplicates code that
today is inlined into every bundle (OpenLayers, tify, …). It fits the
theme's architecture: shortcodes can register scripts into batch groups
while their templates run concurrently, and `baseof.html` renders the
group's outputs in a `templates.Defer` block as `<script type="module">`
tags. The current inputs (shortcode metadata `js` entries, page `js:`
front matter, the `iiif-js` partial) map onto that flow.

Restructuring `script.html`/`baseof.html` onto a batch is the bigger
template surgery — sites with their own copy of `script.html` need the
same rework. Consider it when the bundled code grows (maps and viewers
on many pages); for a minimal footprint stay with Path A.

Two extensions become possible with a batch; both need their own design
work and are not part of this migration:

- the Runner/Instance/params mechanism could replace the inline script
  blocks that call `window.initMap(...)` and friends with per-instance
  params (JSON, `@params` namespace) — it would reduce the reliance on
  the `window.*` globals contract described below;
- split output can contain CSS chunks — a possible future home for the
  three deliberate plain-CSS imports (`lucienne.css`, `tify`, `ol`, see
  the SCSS migration section below).

### Risks

Common to both paths (module semantics):

- **Implicit strict mode** — module code always runs in strict mode. The
  bundled TypeScript already compiles to strict-friendly output, but any
  legacy hand-written or vendor JavaScript relying on sloppy mode breaks.
- **`this` at module top level is `undefined`** (not `window`) — a bare
  `this` at the top of an entry file changes meaning.
- **No implicit globals** — module top-level declarations do not leak
  into `window`. Every cross-bundle API must keep using the explicit
  `window.x = …` assignments; the theme's sources already do this
  (`window.initMap`, `window.addTimeline`, …), consumer JS must follow
  the same rule.
- **`file://` preview breaks** — `<script type="module">` fails when the
  built output is opened from disk (CORS, null origin). `hugo server`
  and HTTP deployments (GitHub Pages) are unaffected.
- **Cross-origin asset hosting** — module scripts are always CORS-mode
  requests; serving assets from another domain (CDN) needs the
  `crossorigin` attribute plus CORS headers on the server. The module
  branch of `script.html` currently omits `crossorigin` (the print base
  template already has it); classic `defer` + SRI works without it.
- **Browser floor** — `type="module"` needs 2017+ browsers (IE11 not at
  all); no `nomodule` fallback is shipped. Consistent with the
  "pre-2024 browsers" housekeeping item below.

Path B specific:

- **Import ordering across chunks** — a known esbuild splitting issue
  (documented under `js.Batch` "Known Issues"): the execution order of
  imports between split chunks is undefined or fixed to one order.
  Hugo's workaround is an explicit import-order entry point registered
  early in the batch. Keep entry points ordered and verify.
- **Fingerprinting + SRI needs verification** — the `js.Batch` examples
  render their output without fingerprint. Fingerprinting a resource
  renames the file but does not rewrite the import URLs *inside* the
  other chunks, so per-chunk fingerprinting may break inter-chunk
  imports. Test before adopting: build a batch, fingerprint every
  output, check that all chunks load. If it does not work, batches live
  without SRI until Hugo grows support — decide consciously (the theme
  fingerprints everything else today).
- **Caching structure changes** — per-page entry files multiply while
  shared chunks become stable across pages; purge rules for CDNs or
  service workers that assumed one `js/*.js` blob need review.

### Verification (both paths)

- `hugo` build green; run the runtime browser check
  (`./scripts/github/check-js-errors-example.sh`, or the site's own
  `scripts/github/check-js-errors.sh`) — module load failures and syntax
  errors surface as console errors, same as for classic scripts.
- Check the dev server output (`hugo server`, unminified and source
  mapped) for stray statements in the built bundles:

  ```bash
  grep -nE '^(import|export)[ ({]' docs/js/*.js
  ```

  On minified production files the same grep is best effort (statements
  may not start a line); the browser check above is the real gate.
- Visual smoke check of the affected pages (the same bundle serves all
  of them — one page per shortcode is enough).

## Remove downward compatibility (Hugo < 0.165.0)

The theme declares `min_version = "0.165.0"` in `theme.toml` — that is the
hard floor. Consuming sites:

1. Pin Hugo ≥ 0.165.0 in CI and deployment scripts (the theme's own
   workflows use `hugo-setup.yml` for this).
2. If they have bumped their own floor to Hugo ≥ 0.166, consider removing
   the fallbacks and version guards kept for older Hugo releases — this is
   optional; the bump is not required to build against the current theme
   release.

Consumer exception: `schatten` keeps `{{ template "_internal/opengraph.html" }}`
in `layouts/baseof.html` in compatibility mode until a verified switch to
`{{ partial "opengraph.html" }}`.

Known remaining compatibility code in the theme: three partials keep a
single top-level `return` statement, because Hugo < 0.166 supports only
one value-return per partial — `layouts/partials/iiif/3/structures.html`,
`layouts/partials/functions/iiif/coerce-language-map.html` and
`layouts/partials/functions/iiif/structure-span.html`. The natural
multi-`return` code is unblocked for restoration; the theme keeps
shipping the workarounds until its next release drops them.

## Deduplicate shortcodes and templates against the theme

Sites that started as forks or copied theme files into their own `layouts/`
often carry stale overrides: identical copies that shadow the theme's
version and silently miss every upstream fix. Find them from the site root:

```bash
# Site-local layout files that also exist in the theme
find layouts -type f | while read -r f; do
  theme="themes/projektemacher-base/$f"
  if [ -f "$theme" ]; then
    if diff -q "$f" "$theme" > /dev/null; then
      echo "IDENTICAL (delete): $f"
    else
      echo "DRIFTED (review):   $f"
    fi
  fi
done
```

Delete the identical copies. For drifted ones, check whether the local
change is still needed — if not, delete the override so the theme's version
applies again; if yes, re-sync everything else from the theme version to
minimize the diff.

## Remove legacy browser support (pre-2024 browsers)

Browsers released before 2024 are history — sites can drop the accumulated
hacks for them from their own assets. The theme's own SCSS ships no such
code (no vendor prefixes, no `@supports` fallbacks), so this applies to site
assets and to copied theme overrides — the deduplication guide above covers
the latter.

Find the candidates from the site root:

```bash
# 1. CSS hacks and prefixes in site SCSS/CSS
grep -rnE '\-(ms|webkit|moz|o)-|@supports|progid:|expression\(|@-moz-document|fill-available' assets/ layouts/

# 2. Browser detection in scripts, shortcodes and layouts
grep -rnE 'userAgent|documentMode|Trident|detect-browser' assets/ layouts/
grep -rn 'browser-banner\|browser-hide-selector' content/ layouts/
```

Remove:

- vendor prefixes and fallback rules for engines that no longer need them —
  every removal must be justified by the new browser floor, not done blindly
- `@supports` guards that only paper over pre-2024 browsers (guards
  enabling *new* features stay)
- UA sniffing blocks and IE guards (`documentMode`, conditional comments)
- `browser-banner` / `browser-hide-selector` calls configured for browsers
  that are gone — both shortcodes match browsers by name via
  `detect-browser` (see `assets/ts/browser-banner.ts`)

Tighten the browser floor itself while at it: the theme ships a
`browserslist` file (`> 0.5%`, `last 2 versions`, `Firefox ESR`, `not dead`)
that already prunes dead browsers — sites can narrow it further (e.g. add
`since 2024`), which also shrinks the output of any prefixing tool.

Candidates from the scan (small, scattered `-webkit-` prefixes only —
review each hit: most are still-required prefixed properties like
`-webkit-scrollbar` or `-webkit-tap-highlight-color`, not pre-2024
fallbacks): blaufusstoelpel (`assets/site-css/style.css`,
`assets/scss/parsa-style.scss`), christianmahnke
(`assets/scss/base.scss`, `assets/scss/syntax.scss`,
`layouts/_shortcodes/insta.html`), kraehenbeisser
(`assets/scss/aether.scss`), schatten (`assets/scss/main.scss`),
yaapb (`assets/scss/base.scss`). Vendored files stay as they are:
kinderbuecher's `assets/scss/_normalize7.scss` (normalize.css) and
backsteinexpressionismus' `assets/vendor/vis-timeline-graph2d.min.css`.

Verify: `hugo` builds green, the affected pages render unchanged in current
Chrome, Firefox and Safari, and `npm run lint` passes.

## Migrate SCSS from `@import` to `@use`

Dart Sass has deprecated `@import` (removal is planned for Dart Sass 3.0),
and the Hugo `dartsass` transpiler surfaces the deprecation warnings during
the build. The theme itself is migrated (`@use` throughout; only the
three deliberate plain-CSS imports remain, see "Still open" below) —
existing builds keep working, so
migrating the remaining consumer entry points is optional, but
new SCSS should use the module system (`@use`/`@forward`) from the start.

`@use` changes evaluation semantics (modules are evaluated once, members are
namespaced, configuration happens via `@use … with (…)`), so a plain "build
still succeeds" is not enough. Verify the migration by direct comparison:

1. Build with the current (old) implementation and keep the compiled CSS:

   ```bash
   hugo --destination /tmp/css-old
   ```

2. Apply the migration: `@import` → `@use`, shared partials → `@forward`,
   entry-point variable overrides → `@use … with (…)`.
3. Rebuild and compare:

   ```bash
   hugo --destination /tmp/css-new
   diff -r /tmp/css-old/css /tmp/css-new/css
   ```

   The compiled stylesheets land in the `css/` directory of the publish
   directory (see `layouts/partials/html/head/style.html` and
   `layouts/partials/fonts/css.html`). Diff only the CSS — the HTML embeds
   build timestamps.
4. Acceptable differences: rule order changes caused by import
   reorganization, comments and sourcemap paths. Anything else — missing
   rules, changed selectors or values — means the migration changed
   behaviour; fix it before committing.

Typical pitfalls:

- `@use`/`@forward` statements must come before any other rules in a file.
- **Never `@use … as *` a module that exports variables from inside a
  partial** — files loaded via `@import` (consumer entry points, copied
  templates) dump those members into the *global* scope, where they
  collide with the consumer's own pre-declarations (`This module and
  the new module both define a variable named …`). Partials import
  namespaced (`@use "icons";` → `icons.$link-light`); `as *` and
  `… with (…)` belong in entry points (`base.scss`, `lint_dummy.scss`)
  only. This bit `media-info.scss`/`services/cookie-consent.scss`
  (both `as *`-ing `icons`) and broke `backsteinexpressionismus`'s
  build via its `$color-light` pre-declaration.
- Variables overridden *before* an `@import` become module configuration —
  e.g. `@use "theme" with ($font-body-font: …)`. A module can be configured
  only once per compilation, so configure it in the entry point.
- Members no longer leak between modules: every file must `@use` its own
  dependencies (`menu.scss` and `audioplayer.scss` each import
  `functions/color` themselves).
- Plain-CSS imports stay plain CSS statements — `@import "lucienne.css"`
  and the `ol` include (see the comment in `assets/scss/openlayers.scss`)
  are deliberately kept as plain CSS imports by dart-sass. `@use` with the
  same load paths (configured via `includePaths` in `style.html`) resolves
  modules instead — decide per case and let the comparison confirm the
  effect.
- Keep `assets/scss/lint_dummy.scss` importing every component, so
  `npm run lint-scss` still covers the whole tree.

Verify afterwards: `npm run lint` passes and a visual smoke check of the
affected pages shows no styling changes.

Still open:

- The theme keeps three deliberate plain-CSS imports (`lucienne.css`,
  `tify`, `ol` — dart-sass warns on them, but inlining would change
  output semantics).
- `services/cookie-consent.scss` still `as *`-imports `icons` (pending
  conversion — schatten's pre-declared `$close-*`/`$color-*` would
  collide with it on the next submodule raise).
- **Deferred** consumers: merch.projektemacher + projektemacher (coder
  leakage architecture; one `@import` left in each `base.scss`).
- **Kept by decision**: yaapb's `_bootstrap-subset.scss` shim and
  wilmabraeuner's `@import "bootstrap"` (isolated vendor code pending
  Bootstrap 6 module support).

## Shortcode SCSS metadata: OpenLayers CSS not covered (needs cleanup)

The shortcode helper metadata (`*-metadata` partials — see the example
site's [shortcode helper documentation](exampleSite/content/shortcodes/shortcode-helper.md))
only covers the assets a shortcode ships itself. Two shortcodes
additionally depend on the OpenLayers base CSS, which their metadata does
not declare:

- `iiif/iiif` declares `scss/iiif.scss` only. The viewer is built on
  OpenLayers controls (`Zoom`, `FullScreen`, `Rotate`), so `ol/ol.css`
  must come from the site — the shortcode loads no CSS itself (see the
  header note in `layouts/_shortcodes/iiif/iiif.html`).
- `maps/osm-vector-tiles` declares `scss/map.scss` only — unlike
  `maps/osm`, whose metadata also ships `scss/openlayers.scss`. `map.scss`
  styles only the wrapper and popup markup, so OpenLayers controls render
  unstyled unless the site adds the base CSS.

The example site documentation states the requirement and the two include
patterns (page front matter `scss:` parameter, `@use` in the site's
`base.scss`) — see the "SCSS not provided by metadata" section of the
shortcode helper docs and the per-shortcode pages (`iiif/iiif`,
`maps/osm-vector-tiles`). What remains is cleanup:

- Decide the long term home of the OpenLayers base CSS: either declare
  `scss/openlayers.scss` (or the icon bundling `scss/ol-iiif.scss`) in the
  two shortcodes' metadata and drop the site side imports, or keep it a
  documented site responsibility. With metadata inclusion the duplicated
  rules collapse in production builds — the theme's PostCSS
  deduplication step removes rules duplicated across the individually
  compiled resources during the transition.
- Consumers currently work around the gap with a global import in their
  `assets/scss/base.scss`: `@use "ol-iiif";` in blaufusstoelpel,
  kraehenbeisser, backsteinexpressionismus and kleiderbuegel (`as *`),
  never-built with a variable override
  (`@use "ol-iiif" as * with ($icon-fill: #000)`). These become redundant
  once the metadata carries the styles (the `projektemacher/blogs/*`
  mirrors are tracked separately).
- christianmahnke's `assets/scss/base.scss` carries a stale comment ("The
  IIIF/OpenLayers styles (iiif, ol, ol-iiif, map) are attached per page
  via the iiif/iiif and maps/osm shortcode metadata") — the metadata of
  `iiif/iiif` does not include `ol`/`ol-iiif`, so either fix the comment
  or make it true via the metadata change above.
- Related open items in the theme: the TODOs in
  `layouts/_shortcodes/iiif/iiif.html` ("The logic of this is flawed",
  "Add shortcode metadata to get rid of global IIIF viewer") and the no-op
  `skipShortcodeAssets` guard in
  `layouts/_partials/shortcodes/shortcode-helper.html` (documented in the
  shortcode helper docs).

# Pagination fixes (open)

An accessibility fix that changes shipped markup. The pagination labels
remain open for sites with drifted `list.html` / `pagination.html` copies
— see the deduplication guide above:

- `layouts/partials/list.html` had the pagination labels swapped: the
  "previous page" link was labelled `next_page` and vice versa. The
  labels are fixed, and the `◀`/`▶` arrows are wrapped in
  `<span aria-hidden="true">` so screen readers announce the label
  only. The visible text of list pagination changes accordingly.
- `layouts/partials/pagination.html` additionally: the `<nav>` is
  labelled (`aria-label`, new i18n key `paginationNavigation`) and the
  redundant `role="navigation"` was dropped, the current page link
  carries `aria-current="page"`, and every page number link gets a
  visually hidden "page N" prefix (new `.visually-hidden` utility in
  `assets/scss/theme.scss`), so screen readers announce context, not
  just a bare number.

Open for sites with drifted copies:

- christianmahnke — `layouts/year/term.html` still swaps the labels
  (`next_page` on the previous-page link).
- yaapb — `layouts/_partials/list.html` carries own markup: labels
  correct but no `aria-current` / visually-hidden prefixes.
- kleiderbuegel — `layouts/_partials/pagination.html` has `aria-label`
  but no `aria-current` / page-N prefixes.

Sites overriding the pagination styles: the links now contain an
additional `.visually-hidden` span before the number - selector based
styling like `a { text-transform: uppercase }` is unaffected, but
selectors such as `.nav-links a:first-child` or CSS that applies to all
inline content of a link may now also hit the hidden span. Sites with a
copied `pagination.html` keep the unlabeled version until they adopt
the theme's.

## Verification

- Check a paginated list: both links point in the direction their
  labels announce.

# Rename the reserved front matter `type` parameter

Hugo 0.169.0 deprecated looking up reserved front matter fields
(`title`, `date`, `description`, `draft`, `keywords`, `slug`, `summary`,
`type`, `weight`, …) through `.Params`, `where … "Params.…"`,
`isset … "…"` and `.Param` — the build warns for every lookup. The
theme previously read the page's own `type` shorthand field through
`.Params.type` (e.g. the CSS class on the page wrapper, the blog
`@type` for schema.org, the media type dispatch for digitized items).

Instead of switching to the `.Type` method (which defaults to the
section/kind type and therefore cannot express "unset" for pages in a
`post` section), the theme now expects the value as a custom parameter
named `itemType` inside the `params` section of the front matter.
Hugo stores `params` keys case-insensitively: the front matter may use
any casing (`itemType:`, `itemtype:`, `ITEMTYPE:`), dot-chained lookups
(`.Params.itemType`) and `where`-collections (`where site.Pages
"Params.itemType" "book"`) resolve it regardless of case. Only `isset`
requires the all-lowercase form: `isset .Params "itemtype"`.

## What changed in the theme

- `layouts/_partials/page.html`: the page wrapper CSS class now reads
  `.Params.itemType`.
- `layouts/schema-org.json`: the blog `@type` override now reads
  `.Params.itemType` (guarded by `isset .Params "itemtype"`).
- `layouts/_partials/metadata/linked-art/collection.json`: same
  pattern for the Linked Art `@type`.
- `layouts/_partials/preview/preview-internal.html`: the "no preview
  image" heuristics now check `isset … "itemtype"` /
  `eq .Params.itemType "other"`.
- `layouts/_shortcodes/post-count.html`: the `type` *shortcode argument*
  is unchanged, but the pages are now filtered with
  `where … "Params.itemType"`.

## What sites need to do

1. Rename the front matter key on every page that used it, keeping the
   value and moving the key into the `params` section if it was set at
   the top level (`type: book` becomes `params.itemType: book`).
2. Update site-side templates that read the field through `.Params`
   (dispatch partials, section templates, print layouts), e.g.:

   ```go-html-template
   {{ partial (printf "media/%s.html" .Params.itemType) . }}
   ```

3. Mind the case handling rules: dot access and `where` are
   case-insensitive, `isset` needs the lowercase key
   (`isset .Params "itemtype"`).

## Verification

```sh
# No remaining reserved-field lookups in templates:
rg -n 'Params\.type|Params "type"|"\bParams\.type\b"' layouts/
# No remaining top-level `type` keys in front matter:
rg -n '^\s*type\s*:' content/
```

A successful build must not log the Hugo 0.169.0 deprecation warning
about reserved fields anymore.

# Mandatory post-upgrade checks

The checks in this section are **mandatory**: every consuming site should
apply them with each theme upgrade. They are not tied to a single release —
they keep site-owned templates aligned with the theme's Hugo baseline and
the site's documentation in sync with what it actually ships.

## 1. Required steps for all consuming sites

### Fix outdated Hugo constructs

Sites that copied theme templates in earlier days (or started as forks)
often carry older Hugo template style. Nothing below has been removed, but
it should be modernized — the theme's own templates follow the right-hand
column (the exceptions are listed below), and newer Hugo features expect it:

| Outdated | Replacement |
| --- | --- |
| `.Site.Params.…`, `$.Site.Title`, … | Global `site.` function: `site.Params.…`, `site.Title`, … |
| `paginate = …` site config key | `pagination.pagerSize = …` (the `paginate` key was deprecated in Hugo 0.128.0) |
| `Pager.PageSize` method | `Pager.PagerSize` (renamed in Hugo 0.128.0) |
| `.Language.LanguageCode` method | `.Language.Locale` (deprecated in Hugo 0.158.0) |
| `languageCode` / `languages.<lang>.languageCode` config keys | `locale` / `languages.<lang>.locale` (deprecated in Hugo 0.158.0) |
| `languages.<lang>.languageName` config key | `languages.<lang>.label` (deprecated in Hugo 0.158.0) |
| `languages.<lang>.languageDirection` config key | `languages.<lang>.direction` (deprecated in Hugo 0.158.0) |
| `.Language.LanguageName` method | `.Language.Label` (deprecated in Hugo 0.158.0) |
| `.Language.LanguageDirection` method | `.Language.Direction` (deprecated in Hugo 0.158.0) |
| `.Site.LanguageCode` method | `.Site.Language.Locale` (deprecated in Hugo 0.158.0) |
| top-level `imaging.quality` config key | per-format: `imaging.jpeg.quality`, `imaging.webp.quality`, `imaging.avif.quality` (deprecated in Hugo 0.163.0) |
| top-level `imaging.compression` / `imaging.hint` config keys | format-specific under `[imaging.avif]` / `[imaging.webp]` (deprecated in Hugo 0.163.0) |
| `.Params.description` front matter lookup on pages | `.Description` (deprecated in Hugo 0.169.0; the theme usages in `html/head/description.html` and the `media/{book,work,postcard,other}.html` partials are migrated) |
| `.Params.keywords` front matter lookup on pages | `.Keywords` (deprecated in Hugo 0.169.0; `html/head/keywords.html` is migrated) |
| `.Params.slug` front matter lookup on pages | `.Slug` (deprecated in Hugo 0.169.0; the example site's `_partials/page.html` is migrated) |
| `$.Scratch.Set` / `.Get` / `.Delete` | Plain variables with reassignment (`$x = …` inside `with` blocks, partial return values) |
| bare `substr` | `strings.Substr` — same function, namespaced form (`substr` is just its alias) |

> [!NOTE]
> There is no global `pagination.` function — `.Paginate` remains the
> documented `Page` method for creating pagers. Only the `paginate`
> *configuration key* and the `PageSize` *method* were deprecated in
> Hugo 0.128.0.

A related, separate change:

> [!NOTE]
> Hugo 0.169.0 deprecated looking up reserved front matter fields
> (`title`, `date`, `description`, `draft`, `keywords`, `slug`, `summary`,
> `type`, `weight`, …) through `.Params`, `where … "Params.…"` and
> `.Param`. Fields set in the `params` section of front matter are
> unaffected, and `site.Params.…` (site configuration) lookups stay
> correct — only page-front-matter shorthand keys need the method
> forms above. The deprecation covers **Page** lookups only: page
> resources (`.Params` populated from `[[resources]]` front matter
> metadata) and menu entries (`MenuEntry.Params`) are different APIs —
> not deprecated, with no `.Description`/`.Draft`-style equivalents,
> so their `.Params.…` reads must stay. The `type` lookups were
> migrated to the custom `itemType` parameter inside the `params`
> section — see ["Rename the reserved front matter `type` parameter"](#rename-the-reserved-front-matter-type-parameter).

Not deprecated, despite common claims to the contrary: `.Language.Lang`.
`.Language.Name` is just a plain alias for it (no deprecation call in
Hugo's source, and the theme's own `baseof.html` uses
`site.Language.Lang`). Only the `LanguageCode`/`LanguageName`/
`LanguageDirection` method renames in the table above are real.

Deliberate exceptions in the theme's own templates — not outdated code:

- `layouts/partials/preview/prerendered.html` compares
  `hugo.Sites.Default` against `.context.Site` — a site *identity* check
  (multilingual awareness) that the `site.` global cannot express.
- `layouts/partials/html/head/iiif-js.html` reads the page Scratch key
  `iiifPrefix`. Nothing in the theme sets it — it is a consumer-facing
  extension point, so it cannot become a plain variable. (The former
  `footer` Scratch key was retired: `footer.html` now passes the
  footer string as a partial argument.) Local `newScratch` objects
  (e.g. in `kenburns.html`) are fine as-is; the rule targets
  page/`$`-Scratch state.
- `layouts/partials/pagination.html` still reads `$.Paginator` — as the
  *fallback* branch when the partial is called with a page context; the
  preferred input is the pager object returned by `.Paginate`.
- `layouts/redirect/single.html` calls *and* redefines
  `_internal/alias.html` on purpose: the local alias page carries
  additional meta tags (`noindex`, canonical, charset).

Minor cleanups for the same pass:

- Canonical camelCase for configuration keys: `canonifyURLs`, not
  `canonifyurls` — Hugo matches keys case-insensitively, but the
  documentation and tooling use the camelCase form.

Find the candidates from the site root — site-owned layouts first; for
copied theme files run the deduplication scan under "Housekeeping" first:

```bash
# 1. .Site. / $.Site. → site.
grep -rnE '\$?\.Site\.' layouts/

# 2. paginate config key / Pager.PageSize (deprecated in 0.128.0)
grep -rnE '^\s*paginate\s*=' config*/ hugo.toml config.toml 2>/dev/null
grep -rn '\.PageSize' layouts/

# 3. Scratch → plain variables (extension-point reads are fine, see above)
grep -rn 'Scratch' layouts/

# 4. bare substr → strings.Substr (exclude JS substring() calls; strings.Substr doesn't match)
grep -rn 'substr' layouts/ | grep -v 'substring'

# 5. internal alias template shadowing
grep -rn '_internal/alias' layouts/

# 6. Language methods (deprecated in 0.158.0):
#    .Language.LanguageCode → .Language.Locale
#    .Language.LanguageName → .Language.Label
#    .Language.LanguageDirection → .Language.Direction
grep -rnE 'Language(Code|Name|Direction)' layouts/

# 7. language config keys → locale / label / direction (deprecated in 0.158.0)
grep -rnE '^\s*language(Code|Name|Direction)\s*=' config*/ hugo.toml config.toml 2>/dev/null

# 8. top-level imaging quality/compression/hint → per-format sub-tables
#    (deprecated in 0.163.0) — review matches under the [imaging] section
grep -rnE '^\s*(quality|compression|hint)\s*=' config*/ hugo.toml config.toml 2>/dev/null
```

### Migrate JS sources to TypeScript

The recurring audit below is the check.

Consumer-specific JavaScript sources are TypeScript — plain-JS sources in
the site's `assets/` and `.js` references in front matter `js:` entries or
layouts predate the theme's TS migration and miss every upstream fix. Find
the candidates from the site root:

```bash
# 1. front matter js: entries pointing at .js sources
grep -rE "^\s*(js:|-)\s*[\"']?(js/)?[^\"']*\.js" content

# 2. plain-JS sources in the site's assets
find assets/js -maxdepth 1 -name "*.js" 2>/dev/null

# 3. .js source references in layouts (built targets are fine)
grep -rn 'resources.Get "js/' layouts/
```

Port plain-JS sources to TypeScript — the theme's `ts/` modules cover the
shared functionality (menu, viewers, search) — reference them from front
matter and layouts, then delete the `.js` originals. Deliberate plain-JS
entries are exceptions when ESM-built (yaapb's `js/main.js`): document
them and keep the ESM build.

### Review the About page dependency list

If the site documents the software it uses (typically on the About page),
review that list after every upgrade against what the site actually loads:
remove entries for libraries that are no longer in use and add newly
introduced ones.

Only **user-facing** libraries and fonts belong on such a list — everything
a visitor can see or hear: viewer frameworks (three.js, tify, A-Frame),
map libraries (OpenLayers), players (howler, PDFObject),
search (Pagefind), diagram/timeline rendering (mermaid, vis-timeline) and
the font families in use. Build tooling and internal helpers (linters,
bundlers, consent plumbing) don't belong there.

Reference: the theme's current user-facing stack (see the `assets/ts/`
imports and `package.json`) is:

| Library | Used for |
| --- | --- |
| tify | IIIF presentation viewer |
| OpenLayers, ol-mapbox-style | Maps and the IIIF image viewer |
| @projektemacher/hdr-canvas | HDR rendering in the IIIF image viewer |
| mermaid | Diagrams (`mermaid` shortcode) |
| howler | Audio player |
| pdfobject | PDF viewer and preview |
| vis-timeline | Timeline |
| Pagefind | Search |
| A-Frame | 3D models (`aframe-3d-model` shortcode, bundled via `ts/aframe.ts`) |
| @projektemacher/lucienne | Generative art (`lucienne` shortcode) |
| three.js | 3D models (`model` / `hdr-model` shortcodes) |

The theme does not use **OpenSeadragon** directly anymore — it ships only
as tify's internal dependency (and the theme's `package.json` pins a
different major version than tify requires). Remove it if it is listed
standalone. Three.js, by contrast, is used directly by the `model` /
`hdr-model` shortcodes (`assets/ts/shortcodes/model.ts`). Fonts come from
the Fontsource npm packages via `scripts/init/get-fonts.sh` — the About
page should list the families actually imported by the site's SCSS.

The OpenSeadragon mention in christianmahnke's wallpaper-generator
post documents that third-party project, not the site's stack.

Check what a site really bundles against its About page:

```bash
# 1. TypeScript/JS module imports in the site's (and theme's) assets
grep -rhoE "from '[^']+'" assets/ts | sort -u

# 2. External scripts loaded from layouts (CDN includes)
grep -rhoE 'src="https?://[^"]+"' layouts/ | sort -u
```

## 2. Verification

1. `hugo` builds without errors, `npm run typecheck` and `npm run lint`
   pass.
2. Optional, but recommended: run a Lighthouse scan —
   `npm run check:lighthouse` (`scripts/check-lighthouse.mjs`). The script
   defaults to the site's `baseURL` (read from the Hugo configuration,
   `http://localhost:1313/` as fallback) and accepts `--url` for another
   URL, `--urls-file` for a JSON page list (e.g. `test-urls.json`),
   `--output` to write the markdown report to a file and `--categories`
   to restrict the scan (`performance`, `accessibility`,
   `best-practices`, `seo`). The companion accessibility scan is
   `npm run check:a11y` — both scripts ship in this repository
   (`scripts/check-a11y.mjs`, `scripts/check-lighthouse.mjs`) and can be
   copied into a site's own tooling (the a11y script excludes the
   `meta-viewport` rule by default, opt back in with
   `--include-meta-viewport`). Run them against the production site as
   well, not only the local build.
