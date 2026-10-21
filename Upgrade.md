# Outstanding deprecations

Everything urgent has been resolved — no 🔴 entries remain. What is
left is tracked here: deprecated or shimmed items in this theme and
its known consumers (the top-level sibling repositories; the
`projektemacher/blogs/*` mirrors and `wilmabraeuner-complete` are
tracked separately). All remaining items are optional or low priority;
step-by-step instructions for past migrations are in the rest of this
guide.

| Item | State | Priority |
| --- | --- | --- |
| SCSS `@import` usage | deprecated by Dart Sass, must become `@use` — see ["Migrate SCSS from `@import` to `@use`"](#migrate-scss-from-import-to-use) | medium |
| Hugo < 0.165 compatibility code | unblocked: all known consumers now pin Hugo ≥ 0.166 (0.168.0) — see ["Remove downward compatibility (Hugo < 0.165.0)"](#remove-downward-compatibility-hugo--01650) | low |
| JS bundle format | bundles are classic IIFE scripts; ESM (`type="module"`) is supported as an opt-in, `js.Batch` as the full switch — both optional — see ["Switch the JS bundles from IIFE to ESM"](#switch-the-js-bundles-from-iife-to-esm) | low |
| Custom site parameters outside `params` | audit corrected: root `description` (kraehenbeisser, diapraesentation), language-level `description`/`decription` typo (christianmahnke), `lanbel`/`lable` typos (flugzeugbesteck, ric-unknownartist) — see ["Move custom site configuration parameters into the `params` namespace"](#move-custom-site-configuration-parameters-into-the-params-namespace) | medium |
| Front matter `params` usage | optional: move custom front matter fields under the `params` key — recipe plus reserved-field caveat (esp. `description` precedence); the exampleSite is converted (2026-10) — see ["Custom front matter parameters go under the `params` key"](#custom-front-matter-parameters-go-under-the-params-key) | optional |
| Hugo layouts (`_default/`, `partials/`, `shortcodes/`) | consumers: 14 converted, 4 need no conversion, 7 pending (2026-10); old structure keeps working — see ["Migrate to the new Hugo template system (v0.146.0)"](#migrate-to-the-new-hugo-template-system-v01460) | low |
| Fonts in `static/fonts/` | generated from npm; documented exceptions only | keep (exceptions stay) |
| Deprecated `.Site.Data` template access | **mandatory**: Hugo deprecated `.Site.Data` (0.156.0, "Use `hugo.Data` instead") and will remove it — the theme's templates now use `hugo.Data`, sites with own `site.Data`/`.Site.Data` code must follow — see ["Replace deprecated `.Site.Data` access with `hugo.Data`"](#replace-deprecated-sitedata-access-with-hugodata) | high |
| Webmention workflows: single deployment connection | collectors copied from this repository must adopt the one-connection layout (variables `DEPLOY_SERVER`/`DEPLOY_USER`/`DEPLOY_PATH`/`DEPLOY_PASS`, `scripts/webmention/host.sh`, split deploy + harvest workflows - deploy runs on commits only, the reusable harvest workflow chains onto it and also runs on the hourly cron; the collected data is committed as `data/webmentions/mentions.json` to the site's own `main` branch — direct Hugo data, the old `fetch.sh` branch flow is gone) — see [services/webmentions/README.md](services/webmentions/README.md) | low |
| PostCSS CSS deduplication | flows from the theme (`assets/_jsconfig/postcss.config.js` + `scripts/init/package.json.sh`) — no consumer-side config needed — see ["CSS pipeline: PostCSS deduplication added"](#css-pipeline-postcss-deduplication-added) | informational |
| Automated accessibility checks | theme ships no CI gate, only a ready-to-run reference implementation (`npm run check:a11y` / `npm run check:lighthouse`) — sites copy and adapt the setup to their own tooling — see ["Add accessibility checks"](#add-accessibility-checks) | informational |

# Replace deprecated `.Site.Data` access with `hugo.Data`

**Mandatory** — Hugo deprecated `.Site.Data` in v0.156.0 ("Use
`hugo.Data` instead") and will remove it in a future Hugo release,
which breaks every template still using it. All site data access must
go through the `hugo.Data` namespace.

The deprecation showed up as a build warning in the theme's test
builds (and a related data loading bug was found along the way — see
"Related" below). The theme's templates and the exampleSite were
migrated in the same change that introduced the webmention
integration (October 2026):

| File | Change |
|---|---|
| `layouts/_partials/html/head/webmention.html` | new (webmention head advertisement), uses `hugo.Data` |
| `layouts/_partials/webmentions/list.html` | new (webmention list), uses `hugo.Data` |
| `layouts/_partials/html/head/stats.html` | already used `hugo.Data` — no change |
| `layouts/tag-list.json` | already used `hugo.Data` — no change |
| `exampleSite/layouts/_shortcodes/i18n-strings.html` | `.Site.Data.i18n` → `hugo.Data.i18n` |
| `exampleSite/content/i18n/index.md` | documentation text updated |

## What sites need to do

Find deprecated data access in the site's own templates and replace
every occurrence with the `hugo.Data` equivalent — the semantics are
identical, only the namespace changes:

```bash
grep -rn "site\.Data\|\.Site\.Data" layouts/ themes/*/layouts/
```

```text
{{ $data := .Site.Data.i18n }}          →    {{ $data := hugo.Data.i18n }}
{{ index site.Data "webmentions" }}     →    {{ index hugo.Data "webmentions" }}
```

Verify with a clean build — the deprecation warning must be gone:

```bash
hugo 2>&1 | grep -i "Site.Data was deprecated"
```

> [!WARNING]
> This also applies to new theme features like the [webmention
> integration](services/webmentions/README.md): their data is consumed
> through `hugo.Data.webmentions…` — site-local template overrides
> written before the switch must use the same namespace.

## Related: explicit `[module.mounts]` drop the implicit data mount

Found while migrating the exampleSite: once a site configures **any**
`[[module.mounts]]` entries, Hugo stops applying the implicit default
mounts — including the mount of the site's own `data/` directory. The
exampleSite (which mounts the theme's `i18n` directory as data for its
'i18n strings' page) lost its own `data/webmentions/` that way; it is
restored with an explicit mount, and sites with custom mounts should
check for the same:

```toml
[module]
  [[module.mounts]]
    source = '../i18n'
    target = 'data/i18n'
  # Explicit mounts replace the implicit defaults - keep the site's
  # own data directory mounted:
  [[module.mounts]]
    source = 'data'
    target = 'data'
```

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
`type="module"` (it stays a `defer` classic script otherwise). Sites
with copied `menu.html` builds need the same `"format"` addition in
their own opts (christianmahnke's mixed state is that case).

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

Since 2026-10 `script.html` also builds the `js` call parameter
centrally: string entries (asset paths, e.g. the IIIF viewers returned
by `iiif-js.html` after its script-handling refactor) are build entry
points — `js.Build` with the same opts as page scripts, including the
`.ts` → `.js` targetPath rename, so built output never leaks a `.ts`
extension (which servers deliver as `video/mp2t`, rejected for module
scripts). Resources passed via `js` are appended unbuilt. The former
`minify = false` exception for IIIF viewer builds is gone — viewer
bundles minify like every other bundle.

Since 2026-10 the partial **never concatenates ESM bundles**: every
bundle is fingerprinted individually and ships as its own
`<script type="module" … crossorigin="anonymous">` tag. Separately
minified bundles reuse the same mangled top level identifiers, so
concatenating them produced `SyntaxError: Identifier 'Pe' has already
been declared` on vintagereality's `/map/` page (main bundle +
`osm-map.ts`). Per-tag emission gives every bundle its own module scope,
making such collisions — and import-hoisting/ordering hazards of
concatenated modules — impossible. `splitBundles` only affects classic
(iife) bundles. Module tags execute in document order, so the main
bundle still runs before page scripts. Steps:

1. Pass `"opts" (dict "format" "esm")` to the `script.html` call in the
   site's `baseof.html` (or default the format in a site-side override
   of the partial).
2. `menu.js` and `print.js` can be switched one at a time by adding
   `"format" "esm"` to their `js.Build` options and changing their script
   tags to `type="module"` (drop `defer`, it is redundant on modules).
   Switch both branches of `baseof.print.html` (the development branch
   emits the tag without `defer` today). The `"target" "es2018"` of
   `print.js` is unrelated to the output format and can stay.

The former steps about `externals` (the partial hardcoded
`slice "domain"`) and about keeping concatenated bundles free of
top-level `import`/`export` statements are obsolete: the hardcoded
external was removed and ESM bundles are no longer concatenated.

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
  "pre-2024 browsers" housekeeping item above.

Path A specific:

- **Concatenation hazard (closed 2026-10).** `script.html` used to
  concatenate independently built bundles (`resources.Concat`: main +
  IIIF viewers + page scripts). For ESM that broke in two ways: top-level
  `import`/`export` statements hoist above the concatenated code
  (execution order changes, relative specifiers resolve against the
  concatenated file's URL), and separately minified bundles reuse the
  same mangled top level identifiers — the concatenation of
  vintagereality's main bundle and its OpenLayers page bundle declared
  `Pe` twice and failed to parse at all. ESM bundles are now emitted as
  one `type="module"` tag each (see Path A above), so neither can occur;
  the iife concatenation remains and stays safe because every part is
  wrapped in its own IIFE scope.

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

## Add accessibility checks

The theme ships no automated accessibility *gate* in CI, but a
ready-to-run reference implementation ships in this repository
(`npm run check:a11y` / `npm run check:lighthouse` — see the end of this
section). The underlying idea, for sites that want a lightweight setup of
their own: run [axe-core](https://github.com/dequelabs/axe-core)
through the already-present `puppeteer` devDependency against the built
pages. Sketch:

```js
import puppeteer from 'puppeteer';
import axe from 'axe-core'; // npm i -D axe-core

const browser = await puppeteer.launch();
const page = await browser.newPage();
await page.goto('http://localhost:1313/some-page/', {waitUntil: 'networkidle0'});
await page.addScriptTag({content: axe.source});
const violations = await page.evaluate(() =>
  axe.run().then((r) => r.violations.map((v) => `${v.id}: ${v.nodes.length} node(s)`)));
console.log(violations.join('\n'));
```

Iterate over the built HTML files (or a representative subset) and run the
script locally. These are suggested static checks of the generated pages
only — the theme sets up no CI job; copy and adapt the sketch to the
site's own tooling. A ready-to-run reference implementation of the sketch
ships in this repository: `scripts/check-a11y.mjs` (axe-core via
puppeteer, markdown report) plus a Lighthouse counterpart,
`scripts/check-lighthouse.mjs`. Both default to the site's `baseURL`
(read from `config.toml`/`hugo.toml`, falling back to
`http://localhost:1313/`) and accept `--url` to check a different URL,
`--urls-file` for a JSON page list (e.g. `test-urls.json`) and `--output`
to write the markdown report to a file; run them via `npm run
check:a11y` / `npm run check:lighthouse`. Both print agent-actionable
markdown tables to stdout, and the a11y script excludes the
`meta-viewport` rule by default (see below).

Run these checks against the **production site** as well, not only against
local builds: deployment pipelines (minification, fingerprinting, CDN and
external services, content changes) can introduce violations the local
build doesn't show. Point the same script at the deployed base URL and
iterate over the pages from the site's `test-urls.json` (see "Run the JS
runtime check against the example site" above) — keeping that list current
for the runtime check also keeps the accessibility scan's page set current.

### Viewport zoom behaviour (`disableScale` removed)

The viewport partial (`layouts/partials/html/head/viewport.html`) no
longer emits `user-scalable=no`: the `[params] disableScale` option has
been removed — setting it has no effect (Hugo ignores unknown params),
no warning is printed. Pinch zoom-in must stay allowed for accessibility
(WCAG 2.5.5 / Lighthouse `meta-viewport`). Only zoom-out is blocked via
`minimum-scale=1.0`. Pages
using the theme's partial therefore no longer trigger the `meta-viewport`
violation ("Zoom blocked"). The a11y
script still excludes `meta-viewport` by default (opt back in with
`--include-meta-viewport`), so scans of older builds remain usable.

## Check IIIF documents with the browser check

The browser check (`scripts/check-js-browser-errors.mjs`, wrapped by
`scripts/github/check-js-errors.sh`) has an IIIF awareness mode
(`-i`/`--iiif`): URLs ending in `manifest.json`, `collection.json` or
`info.json` are fetched and — when they are valid IIIF documents —
checked for referenced assets instead of being opened in the browser.
Only assets served by the internal web server are requested (external
hosts are skipped): `thumbnail`, `rendering`, `logo`, `seeAlso` and
annotation `body` ids, plus the Image API derivatives advertised by an
`info.json` (the canonical full image, one request per `sizes` entry
and one representative tile per `tiles` entry and scale factor). A
missing asset fails the run with exit code 127. The mode is documented
in detail in the example site's QA scripts post
(`exampleSite/content/posts/qa-scripts/index.md`).

What sites should do (optional):

1. Add the IIIF document URLs the site ships (manifests, collections,
   image `info.json` — at least one per service or template variant)
   to the site's `test-urls.json`.
2. Run the check with the flag — `scripts/github/check-js-errors.sh -i`
   (the wrapper forwards arguments) or add `-i` to the CI invocation.
3. Without the flag those URLs are only opened in the browser: a
   manifest whose referenced images 404 passes the check unnoticed.

The exampleSite's own `test-urls.json` lists no IIIF document URLs yet —
adopt the mode there together with the first manifest URLs.

## Remove downward compatibility (Hugo < 0.165.0)

The theme declares `min_version = "0.165.0"` in `theme.toml` — that is the
hard floor. Consuming sites:

1. Pin Hugo ≥ 0.165.0 in CI and deployment scripts (the theme's own
   workflows use `hugo-setup.yml` for this).
2. If they have bumped their own floor to Hugo ≥ 0.166, consider removing
   the fallbacks and version guards kept for older Hugo releases — this is
   optional; the bump is not required to build against the current theme
   release.

Known remaining compatibility code: three partials keep a single top-level
`return` statement, because Hugo < 0.166 supports only one value-return per
partial — `layouts/partials/iiif/3/structures.html`,
`layouts/partials/functions/iiif/coerce-language-map.html` and
`layouts/partials/functions/iiif/structure-span.html`. All known
consumers now pin Hugo 0.168.0 in their workflows (verified 2026-10), so
the natural multi-`return` code is unblocked for restoration; the theme
keeps shipping the workarounds until its next release drops them.

## Migrate to the new Hugo template system (v0.146.0)

Hugo re-implemented its template handling in v0.146.0 and changed the
layouts structure: `layouts/_default/` is gone (its files move up to the
`layouts/` root), `partials/` is renamed to `_partials/`, `shortcodes/`
to `_shortcodes/`, `index.<format>` home templates become `home.<format>`,
the `_internal/` template concept is removed and the lookup order is
unified — see
[gohugo.io/templates/new-templatesystem-overview](https://gohugo.io/templates/new-templatesystem-overview/).
Hugo keeps resolving the old structure by mapping old to new, so nothing
is required: any Hugo release the theme supports (≥ 0.165.0) already
ships the mapping, and this theme still builds from the old structure
today. Only `baseof.print.html` already uses new-style naming (the
identifier sits after `baseof.`).

Consumer status (2026-10): briefsteller, schatten, xn--h-zfa.xyz and
yaapb already use the new structure (`layouts/baseof.html`,
`layouts/_partials/`), kraehenbeisser is mid-migration — the mixed
old/new lookup across theme and site layers keeps working as described
below.

### Mixing old and new layouts across site and theme

A site adopting the new layout keeps working with a theme that still
ships the old one — and the other way round. The old-to-new mapping is
applied per template candidate in the unified lookup that spans all
file system layers (project, theme module), so the two components
migrate independently (the same pattern the community used on Hugo
0.146+: themes and sites converted one side at a time). The mapping is
documented as best-effort — "try it against your site" is part of the
official advice — and three changed behaviours deserve an explicit test
in mixed setups:

- **`{{ block }}`/`{{ define }}` semantics changed.** Redefining blocks
  in per-page-path or per-type base templates that are themselves
  redefined produced blank output in a number of reported cases after
  0.146.0 (an undocumented inheritance capability was dropped). Sites
  that copy `baseof.html` and redefine blocks per section must test
  before and after.
- **Custom layouts with output formats and cascaded `type:` broke** in
  edge cases (hugo issue #13667: templates like
  `section/list.<format>.xml` no longer found under some `type:`
  cascades). This theme's output format templates are fixed-name; the
  build comparison below covers the spot.
- **`taxonomy.html` no longer covers the term kind** — list-shaped
  templates now resolve per kind (`taxonomy.html` matches taxonomy
  pages only, `term.html` term pages). The theme covers all three list
  kinds with `list.html` at `_default/`, which keeps working; sites
  with their own `taxonomy.html`/`term.html` copies must check their
  term pages render.

### Migrating the theme's layouts

Inventory for this theme, when the switch happens (theme side and
consumer copies apply the same moves):

- `layouts/_default/*` → up to `layouts/`: `baseof.html`,
  `baseof.print.html` (names unchanged), `list.html`, `single.html`,
  `search.html` and `html-body.html` (custom layout identifiers),
  `sitemap.xml`, the render hooks (`_default/_markup/` → `_markup/`,
  the old location keeps working), and the output format templates —
  `home.iiif-collection.json`, `term.iiif-collection.json`,
  `section.iiif-manifest.json`, `single.iiif-manifest.json`,
  `single.codemeta.json`, `single.linkedart.json`, `single.qrcode.json`,
  `section.qrcode.json`, `section.geojson`, `post-list.json`,
  `tag-list.json`, `wikidata-list.json`, `linked-art-collection.json`,
  `schema-org.json` — which keep their names and just move up.
- `index.rss.xml` → `home.rss.xml` (the only `index.`-named template —
  home templates are `home.` in the new system).
- `layouts/partials/` → `layouts/_partials/`, `layouts/shortcodes/` →
  `layouts/_shortcodes/`.
- `layouts/redirect/` and the already-root-level `404.html`,
  `robots.txt` stay where they are — non-underscore directories are
  page paths in both eras, and the special template types live at the
  root.
- `layouts/redirect/single.html` calls *and* redefines
  `{{ template "_internal/alias.html" … }}` on purpose (see the
  exceptions section below). The call keeps working in compatibility
  mode (`_internal` removal is deferred to a future release) — when
  migrating, verify the new-system form (`partial "alias.html"`)
  resolves to Hugo's embedded template or the local redefine before
  switching.

### Consumer migration status (2026-10)

The same moves were applied to the consumer sites (each repo staged
separately, submodule pointers bumped to the current theme tip in the
same commit):

- **Converted, staged (commit pending):** `blaufusstoelpel`,
  `haesslicheplastiktiereundzeugs`, `kinderbuecher`, `vintagereality`,
  `vorsatzpapier`, `labs.projektemacher.org`,
  `backsteinexpressionismus`, `never-built`.
- **Nothing to convert** (no site layouts at all): `flugzeugbesteck`,
  `flohmarktfunde`, `diapraesentation`, `ric-unknownartist`.
- **Still on the old structure** (same recipe, pending):
  `merch.projektemacher`, `schriftmuster`, `kleiderbuegel`,
  `projektemacher`, `christianmahnke`, `wilmabraeuner` (has the
  `_default/terms.html` → `term.html` rename case) and
  `wilmabraeuner-complete` (5 `partial "partials/…` prefixed calls to
  rewrite first).

Findings from that run, matching the risk notes below: not one
converted site carried a `partials/`-prefixed call; the only consumer
`_internal` user is `schatten` (its `baseof.html` keeps
`{{ template "_internal/opengraph.html" }}` in compatibility mode
until a verified switch to `{{ partial "opengraph.html" }}`); the
`index.html` → `home.html` rename was needed in `blaufusstoelpel`,
`haesslicheplastiktiereundzeugs` and `kinderbuecher`; no site mounts
`layouts/`, so no mount adjustments were needed. The build comparison
below is still owed per converted site — the moves were staged without
a build.

### Risks

- **The mapping is best-effort, not a guarantee** — Hugo's own advice
  is to test; the build comparison below is the theme's translation of
  that advice.
- **Block redefinition breakage** (see above) — same check for the
  theme's own `baseof.html` consumers.
- **`_internal` templates are deprecated** — `redirect/single.html` is
  the theme's only user; pin the replacement behaviour before Hugo
  removes them.
- **Partials called with a `partials/` prefix** are no longer resolved
  (previously `partial "partials/foo.html"` and `partial "foo.html"`
  were equivalent). The theme calls partials without the prefix
  (verified 2026-10); among consumers only `wilmabraeuner-complete`
  still uses the prefix (5 calls, 2026-10 survey) — it results in a
  "no such template" error, so this one fails loudly.

### Verification

1. Build the current (old-layout) implementation and keep the output:
   `hugo --destination /tmp/layouts-old`.
2. Apply the moves (git `mv`, no content changes).
3. Rebuild: `hugo --destination /tmp/layouts-new && diff -r
   /tmp/layouts-old /tmp/layouts-new` — acceptable differences: build
   timestamps (they are embedded in the HTML), sitemap, and RSS file
   paths only after intentional renames. Anything else means the
   lookup mapping changed behaviour — fix before committing.
4. Run the runtime browser check
   (`./scripts/github/check-js-errors-example.sh`) and spot check the
   non-HTML output formats (qrcode/codemeta/iiif-collection JSON, RSS,
   sitemap, redirect pages).

## Custom front matter parameters go under the `params` key

In front matter, the standard field names are **reserved** (`title`,
`type`, `description`, `date`, …) and are read through their dedicated
methods (`.Title`, `.Type`, `.Description`, …) — a custom field cannot
use them. Custom page parameters must go under the front matter
`params` key and are read via `.Params` — see [Hugo docs: Front matter
→ Parameters](https://gohugo.io/content-management/front-matter/#parameters).

The theme's meta description chain reflects this
(`layouts/_partials/html/head/description.html`):
`site.Params.description` → `.Params.description` → `.Description` (the
reserved front matter field) → `.Summary`. A page's front matter root
`description` is therefore the reserved field, not a custom parameter —
moving it under `params.description` changes precedence (it then wins
over `.Description`) — only do that deliberately.

### What sites can do (optional)

Hugo exposes unknown root-level front matter fields through `.Params`,
and a front matter `params` map is merged into `.Params` as well — both
resolutions leave the consumed value identical (`.Params.<key>` in
every case; only the `description` chain above makes the distinction
visible). Nesting custom fields under `params:` is therefore
behavior-neutral; it only makes their custom nature explicit in the
content. The exampleSite was converted this way (2026-10).

Find the root-level candidates:

```bash
# Front matter root keys per file — keep the standard Hugo fields
# (title, description, date, tags, outputs, layout, resources, build,
# draft, slug, aliases, ...) and move the rest under a params: block.
# Anything the site or theme reads with `.Params.<key>` is such a field
# (theme inputs: `displayinlist`, `metaPage`, `iiif.*`, `toc`, `src`,
# `js`, `scss`, ...).
find content -name '*.md'
```

Then move the custom fields (YAML front matter shown; TOML sites use a
`[params]` table instead):

```yaml
# before               # after
---                    ---
title: Presentation 3  title: Presentation 3
description: "…"       description: "…"
displayinlist: false   params:
metaPage: true           displayinlist: false
iiif:                    metaPage: true
  structure:             iiif:
    - label: …             structure:
      page: page0001         - label: …
                                 page: page0001
---                    ---
```

Do **not** move:

- the standard Hugo fields as listed above — they are preferred over
  their `params.` twins (with `description` being the precedence
  exception already covered above);
- Hugo's `build` front matter (render options) and the `params` maps
  nested inside `resources` entries — unrelated mechanisms that look
  similar.

The theme reads all page-level inputs through `.Params.*` (`.Params.js`
in `layouts/_partials/html/head/script.html`, `.Params.scss` in
`style.html`, `isset .Params "iiif"` in `iiif/iiif-presentation.html`,
`.Params.displayinlist`/`.Params.metaPage` in `home.rss.xml` and
`list.html`), so the move needs no template changes — including for
`js:`/`scss:`, which may stay at the root where the discovery commands
in "Run the JS runtime check against the example site" expect them, or
move under `params:` when the site's content also matches the
tolerant `^\s*js:` grep form used there.

### Verification

Build the site before and after the move and compare — the output must
be identical apart from the embedded build timestamps, since
`.Params.*` resolves the same either way:

```bash
hugo --destination /tmp/frontmatter-old
# apply the move
hugo --destination /tmp/frontmatter-new && diff -r /tmp/frontmatter-old /tmp/frontmatter-new
```

## Move custom site configuration parameters into the `params` namespace

Custom site parameters belong under `[params]` (or
`[languages.<lang>.params]` for per-language values); unknown root keys
are not standard configuration — see [Hugo docs: Configure params](https://gohugo.io/configuration/params/).

**Open (2026-10)** — an earlier "complete" claim here was wrong: the
first audit whitelisted `description` as a standard root key (it is not
— the theme reads `site.Params.description`, so a root `description`
works only through Hugo's legacy merge) and its `[languages.<lang>]`
scan missed indented keys. The corrected audit found, **not yet fixed**:

| Site | Finding | Fix |
|---|---|---|
| kraehenbeisser | `description` at config root | move into a `[params]` table |
| diapraesentation | `description` at config root — redundant, both `[languages.<lang>.params] description` exist | delete the root key |
| christianmahnke | `[languages.de] description` at language level; `[languages.en] decription` — typo, never worked | move both under `[languages.<lang>.params]`, fixing the typo |
| flugzeugbesteck | `[languages.en] lanbel = "English"` — typo'd `label` | → `label` (broken English switcher label) |
| ric-unknownartist | `[languages.en] lable = "English"` — same typo class | → `label` |
| ric-unknownartist, schatten | `defaultcontentlanguage` + `DefaultContentLanguage` both present | drop the lowercase variant |

The theme and the exampleSite are clean (`description` lives under
`[params]`). The original audit greps and the scripts dual-lookup policy
(`scripts/PyHugo` errors when a key exists in both root and `params`,
`preview.py` prefers `params` and falls back to the root key) live in
the git history of this file (pre-2026-10).

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

Still open (2026-10): everything else drifted in the consumer audits is
deliberate customization (header/footer redesigns, section layouts,
custom menus) — review opportunistically, the remaining `R` renames to
the new template structure in briefsteller/schatten/xn--h-zfa.xyz/
yaapb/kraehenbeisser are staged migrations in progress.

## Shorten template fallbacks with the `default` function (optional)

**Done in the theme (2026-10), optional for sites.** Template constructs of
the shape "initialize with a fallback, then overwrite via `isset`/`with`"

```go
{{- $share := false -}}
{{- if isset . "share" -}}
  {{- $share = .share -}}
{{- end -}}
```

were shortened to the equivalent one-liner:

```go
{{- $share := .share | default false -}}
```

Applied to the theme's `iiif/_iiif-image.html`, `iiif/iiif-image.html`,
`html/head/script.html`, `html/head/style.html` and the `lucienne`
shortcode. Sites that copied these templates can apply the same pattern,
but mind the semantics: `default` treats `""`, `false` and `nil` as
unset, while `isset` distinguishes them — only convert when the fallback
itself is falsy (`""`, `false`, `0`), otherwise an explicitly empty
value would silently switch to the fallback. Non-falsy fallbacks (e.g.
`class="iiif iiif-image"`) were intentionally kept on `isset`.

Two bugs surfaced while refactoring and were fixed (relevant if you
copied the affected templates):

- `schema-org.json` and `metadata/linked-art/collection.json` called
  `isset "section" .Params` with swapped arguments — always false, so
  the `section`/`type` page params were never honoured. Arguments are
  now in the right order; sites setting these params will see the
  JSON output change accordingly.
- `iiif/_iiif-image.html` assigned `$baseURL :=` inside its `else`
  branch (shadowed, so the fallback never took effect). The un-shadowed
  fallback `path.Dir $infoJson` would mangle absolute info.json URLs
  (`https://` → `https:/`), so it is guarded: relative info.json paths
  now fall back to their directory, absolute URLs keep an empty
  `baseURL` (the previous effective behaviour).

Verification pattern: build before and after and diff the output —
`diff -r` should be empty apart from embedded build timestamps.

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

Still open (2026-10):

- The theme keeps three deliberate plain-CSS imports (`lucienne.css`,
  `tify`, `ol` — dart-sass warns on them, but inlining would change
  output semantics).
- `services/cookie-consent.scss` still `as *`-imports `icons` (pending
  conversion — schatten's pre-declared `$close-*`/`$color-*` would
  collide with it on the next submodule raise).
- **Deferred** consumers: merch.projektemacher + projektemacher (coder
  leakage architecture). never-built is cleared (2026-10): its `@import`
  backlog — including the duplicate `maps/projektemacher`/`link` loads —
  is gone from the audited files.
- **Kept by decision**: yaapb's `_bootstrap-subset.scss` shim and
  wilmabraeuner's `@import "bootstrap"` (isolated vendor code pending
  Bootstrap 6 module support).

# Pagination label fixes (open)

An accessibility fix that changes shipped markup. The pagination labels
remain open for sites with drifted `list.html` / `pagination.html`
copies (backsteinexpressionismus, briefsteller, ric-unknownartist,
schriftmuster, yaapb) — see the deduplication guide above:

- `layouts/partials/list.html` had the pagination labels swapped: the
  "previous page" link was labelled `next_page` and vice versa. The
  labels are fixed, and the `◀`/`▶` arrows are wrapped in
  `<span aria-hidden="true">` so screen readers announce the label
  only. The visible text of list pagination changes accordingly.

## Verification

- Check a paginated list: both links point in the direction their
  labels announce.

# Accessible pagination

`layouts/partials/pagination.html` changes:

- The `<nav>` is labelled (`aria-label`, new i18n key
  `paginationNavigation`) and the redundant `role="navigation"` was
  dropped.
- The current page link carries `aria-current="page"`.
- Every page number link gets a visually hidden "page N" prefix (new
  `.visually-hidden` utility in `assets/scss/theme.scss`), so screen
  readers announce context, not just a bare number.

## Consumer migration

Sites overriding the pagination styles: the links now contain an
additional `.visually-hidden` span before the number - selector based
styling like `a { text-transform: uppercase }` is unaffected, but
selectors such as `.nav-links a:first-child` or CSS that applies to all
inline content of a link may now also hit the hidden span. Sites with a
copied `pagination.html` keep the unlabeled version until they adopt
the theme's.

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
| `.Language.Lang` method | `.Language.Name` (deprecated in Hugo 0.158.0) |
| `.Site.LanguageCode` method | `.Site.Language.Locale` (deprecated in Hugo 0.158.0) |
| top-level `imaging.quality` config key | per-format: `imaging.jpeg.quality`, `imaging.webp.quality`, `imaging.avif.quality` (deprecated in Hugo 0.163.0) |
| top-level `imaging.compression` / `imaging.hint` config keys | format-specific under `[imaging.avif]` / `[imaging.webp]` (deprecated in Hugo 0.163.0) |
| `$.Scratch.Set` / `.Get` / `.Delete` | Plain variables with reassignment (`$x = …` inside `with` blocks, partial return values) |
| bare `substr` | `strings.Substr` — same function, namespaced form (`substr` is just its alias) |

> [!NOTE]
> There is no global `pagination.` function — `.Paginate` remains the
> documented `Page` method for creating pagers. Only the `paginate`
> *configuration key* and the `PageSize` *method* were deprecated in
> Hugo 0.128.0.

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
- ~~Nondeterministic element IDs~~ — deliberately **not** pursued:
  replacing random inputs (like `md5 (printf "%s-%s" $src now.UnixNano)`
  or `shuffle (seq 1 9)` name components) with deterministic
  discriminators breaks more things than it fixes; the theme's
  shortcodes and partials keep their current ID generation.

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

# 5. nondeterministic IDs — deliberate exception, no action
# (the theme keeps its current ID generation, see above)
# grep -rnE 'UnixNano|shuffle' layouts/

# 6. internal alias template shadowing
grep -rn '_internal/alias' layouts/

# 7. Language methods (deprecated in 0.158.0):
#    .Language.LanguageCode → .Language.Locale
#    .Language.LanguageName → .Language.Label
#    .Language.LanguageDirection → .Language.Direction
grep -rnE 'Language(Code|Name|Direction)' layouts/
# the .Language.Lang method (→ .Language.Name): [^u] keeps LanguageX
# methods out of the matches
grep -rnE '\.Language\.Lang([^u]|$)' layouts/

# 8. language config keys → locale / label / direction (deprecated in 0.158.0)
grep -rnE '^\s*language(Code|Name|Direction)\s*=' config*/ hugo.toml config.toml 2>/dev/null

# 9. top-level imaging quality/compression/hint → per-format sub-tables
#    (deprecated in 0.163.0) — review matches under the [imaging] section
grep -rnE '^\s*(quality|compression|hint)\s*=' config*/ hugo.toml config.toml 2>/dev/null
```

### Migrate JS sources to TypeScript

The recurring audit below is the check — the 2026-10 audit pass found
all consumers clean or carrying documented deliberate exceptions
(theme-contract ESM entry shims, vendored typed libraries).

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
a visitor can see or hear: viewer frameworks (three.js, OpenSeadragon,
tify, A-Frame), map libraries (OpenLayers), players (howler, PDFObject),
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

Known stale entries to watch for: the theme does not use
**OpenSeadragon** directly anymore — it ships only as tify's internal
dependency (and the theme's `package.json` pins a different major version
than tify requires). Remove it if it is listed standalone. Three.js, by
contrast, is used directly by the `model` / `hdr-model` shortcodes
(`assets/ts/shortcodes/model.ts`). Fonts come from the Fontsource npm
packages via `scripts/init/get-fonts.sh` — the About page should list the
families actually imported by the site's SCSS.

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
   `npm run check:a11y` — both are documented in "Add accessibility
   checks" (Housekeeping above). Run them against the production site as
   well, not only the local build.
