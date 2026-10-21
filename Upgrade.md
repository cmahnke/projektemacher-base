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
| Custom site parameters outside `params` | audit corrected: root `description` (kraehenbeisser, diapraesentation), language-level `description`/`decription` typo (christianmahnke), `lanbel`/`lable` typos (flugzeugbesteck, ric-unknownartist) — see ["Move custom site parameters into the `params` namespace"](#move-custom-site-parameters-into-the-params-namespace) | medium |
| Hugo layouts (`_default/`, `partials/`, `shortcodes/`) | consumers: 14 converted, 4 need no conversion, 7 pending (2026-10); old structure keeps working — see ["Migrate to the new Hugo template system (v0.146.0)"](#migrate-to-the-new-hugo-template-system-v01460) | low |
| Fonts in `static/fonts/` | generated from npm; documented exceptions only — see ["Upgrading fonts to the npm (Fontsource) based system"](#upgrading-fonts-to-the-npm-fontsource-based-system) | keep (exceptions stay) |
| PostCSS CSS deduplication | flows from the theme (`assets/_jsconfig/postcss.config.js` + `scripts/init/package.json.sh`) — no consumer-side config needed — see ["CSS pipeline: PostCSS deduplication added"](#css-pipeline-postcss-deduplication-added) | informational |

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
grep -rEl '^js:' content
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

# Upgrading IIIF Presentation API 2 → 3

Complete — every known consumer has migrated (all content uses
`presentation/3` contexts). The guard templates (`single.json`,
`single.iiif.json`) were removed in the 2026-10 cleanup: API 2 content
produces no manifest output at all. New setups use the `iiif-manifest`
output format with the partials in `layouts/partials/iiif/3/`.

# Upgrading `iiif.structure` to the shorthand format

Complete — all known consumer content uses the `label`/`page`/`items`
shorthand; the legacy `type:`/hand-written-id guard was removed in the
2026-10 cleanup. The shorthand is documented in
`exampleSite/content/iiif/page-metadata.md`.

# Upgrading fonts to the npm (Fontsource) based system

Complete — all known consumers import the generated `npm-fonts/<family>`
partials directly; `font-family:` usages use the mapped names (static
families keep theirs, variable families use `'<Family> Variable'`).
Everything in `static/fonts/` is generated by `scripts/fonts.sh` and
gitignored — do not commit or edit generated files. Exception fonts
without an npm source (`DSBehrensschrift`,
`FuturaRenner`) keep their handwritten `fonts/` partials. Every known
consumer has run `scripts/init/get-fonts.sh` (2026-10) — the generated
`assets/scss/npm-fonts/` partials are (re)created by the init set
locally and in CI. The
family-name mapping table and
the migration steps live in the git history of this file (pre-2026-10).

# Hugo site parsers merged into PyHugo

Complete — the parsers live in `scripts/PyHugo`; the deprecated `Posts.py`
class is gone and no consumer repo carries its own copy.

# Deprecation of the Mirador viewer

Complete — Mirador is gone; TIFY (`ts/iiif/tify.ts`) is the only
presentation viewer and no consumer references Mirador anymore.

# Housekeeping

The changes in this section are **optional**: no consuming site has to apply
them to keep building against the current theme release. They bundle work that
keeps a site aligned with the theme's direction — finishing half-done
migrations, dropping dead compatibility code and adopting the theme's tooling.
Pick items as time allows; each one stands on its own.

## Yarn retired

Complete (2026-10) — no known consumer ships a `yarn.lock`. Yarn remains
unsupported: `scripts/node/dependency-management.sh` exits with an error
when `DEPENDENCY_MANAGER=yarn` is set — use `DEPENDENCY_MANAGER=npm` (or
`pnpm`, the dependency-management default). The removal steps live in
the git history of this file (pre-2026-10).

## Finish the JS → TypeScript migration

Moved to the required checks — see
["Migrate JS sources to TypeScript"](#migrate-js-sources-to-typescript)
under Mandatory post-upgrade checks. The theme's own migration completed
2026-10 (`ts/search.ts`, `ts/timeline.ts`, `ts/fullscreen.ts`,
`ts/maps/projektemacher-map.ts` ported, Mirador-related sources removed,
unused `assets/js/` shims deleted); consumer front matter references
`ts/` paths everywhere.

## Switch the JS bundles from IIFE to ESM

Every JS bundle the theme emits is an esbuild IIFE: `js.Build` runs with
Hugo's default `format: "iife"` and produces a self-contained classic
script — no `import`/`export` statements — that `html/head/script.html`
loads with `defer`, fingerprinting and SRI. The same pattern covers the
main bundle and the page/shortcode bundles (`script.html`), the menu
script (`menu.html`, `js/menu.js`) and the print script
(`baseof.print.html`, `js/print.js`).

Consumer status (2026-10): eleven consumers emit ESM today —
ric-unknownartist (own pipeline, unconditional), diapraesentation and
flohmarktfunde (own baseof pipelines), never-built (via the wired
`js = 'esm'` param), yaapb (own `main.ts`, TS-ported), blaufusstoelpel
(own `main.ts`, TS-ported), merch.projektemacher (pdf-preview),
projektemacher (script.html opts), kleiderbuegel (print bundle + menu)
and vorsatzpapier (viewer builds) — with christianmahnke mixed
(script.html ESM + `splitBundles`, own menu/iiif/pdf builds still IIFE)
and wilmabraeuner partial (menu.js ESM, main bundle IIFE). The remaining
theme-pipeline consumers (backsteinexpressionismus, briefsteller,
kinderbuecher, kraehenbeisser, labs.projektemacher.org, schatten,
schriftmuster, vintagereality) can now flip via config alone — see the
config-driven switch below. flugzeugbesteck,
haesslicheplastiktiereundzeugs, plastikwarenfabrik and xn--h-zfa.xyz
have no JS pipeline.

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
`type="module"`.

There are two ways to switch to ES modules; both are optional — a site
picks one (Path B subsumes Path A's module semantics, see Risks below).

### Path A — opt in per bundle with `format: "esm"`

`html/head/script.html` already supports it:

```html
partial "html/head/script.html" (dict "context" . "splitBundles" true "opts" (dict "format" "esm"))
```

With `format` set to `esm` the partial emits `<script type="module">`
instead of the `defer` variant — modules are deferred implicitly, so the
timing stays the same. One opts pass covers all bundles built within the
call (main bundle, IIIF viewers, page scripts). Steps:

1. Pass `"opts" (dict "format" "esm")` to the `script.html` call in the
   site's `baseof.html` (or default the format in a site-side override
   of the partial).
2. Empty the `externals` list. The partial hardcodes `slice "domain"` —
   under esm an external dependency is emitted as an `import` statement
   and the bundle fails to load. Nothing imports `domain` today (checked
   2026-10), it is a leftover; drop it when switching.
3. Keep the concatenated bundles free of top-level `import`/`export`
   statements (see risks below) — re-check after every theme raise.
4. `menu.js` and `print.js` can be switched one at a time by adding
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
  "pre-2024 browsers" housekeeping item above.

Path A specific:

- **Concatenation is the fragile spot.** `script.html` concatenates
  independently built bundles (`resources.Concat`: main + IIIF viewers +
  page scripts). That is safe only while every part is self-contained:
  the moment one part emits top-level `import`/`export` statements,
  imports hoist above the concatenated code (execution order changes)
  and relative specifiers resolve against the concatenated file's URL,
  not the original bundle's. Guard: keep `externals` empty and no
  re-exports.

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
violation ("Zoom blocked"). Verified 2026-10: no known consumer carries
a viewport partial copy, `user-scalable=no` or a `disableScale`
reference. The a11y
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

- **Converted, committed:** `kraehenbeisser`, `yaapb`, `briefsteller`,
  `schatten`, `plastikwarenfabrik`, `xn--h-zfa.xyz`.
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

## Move custom site parameters into the `params` namespace

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

Still open (2026-10): the identical `quote.html` copy in
ric-unknownartist was removed (resolved); everything else drifted in the
consumer audits is deliberate customization (header/footer redesigns,
section layouts, custom menus) — review opportunistically, the remaining
`R` renames to the new template structure in
briefsteller/schatten/xn--h-zfa.xyz/yaapb/kraehenbeisser are staged
migrations in progress.

## Adopt the init scripts for generated assets

The theme generates more and more assets at build time instead of tracking
them in the repository — fonts were the first (see the fonts migration
guide above), meanwhile the pattern covers:

| Script | Generates |
| --- | --- |
| `scripts/init/get-fonts.sh` | Fonts in `static/`, CSS/SCSS in `assets/` |
| `scripts/init/get-map-styles.sh` | `static/map-styles/` VersaTiles sprites |
| `scripts/init/get-flags.sh` | Flag images for language switches |
| `scripts/init/get-favicons.sh` | Favicon set in `static/images/` |
| `scripts/init/i18n.sh` | Merged `i18n/<lang>.toml` files |
| `scripts/init/package.json.sh` | Merged `package.json` |

Complete (2026-10) — every known consumer runs the init set in CI (the
sites' `scripts/setup.sh` loops over `scripts/init/*.sh`), and the set
has been run locally in all consumer working copies: fonts generated
for every site importing `npm-fonts/…`, `package.json` merged
everywhere. `get-map-styles.sh` is only needed by sites shipping vector
tile maps, `get-favicons.sh` generates the theme-logo set (sites with
their own branding manage favicons individually). Keep the pattern:
delete vendored copies of generated assets instead of pinning them —
pinned copies go stale and mask upstream updates, exactly like the
duplicate templates above. Known pitfall: pnpm ≥ 10 aborts
`pnpm install` on unapproved build scripts (`gl@9` — remedied
interactively with `pnpm approve-builds`); the packages Hugo needs
(postcss, postcss-cli, postcss-discard-duplicates, pagefind) install
regardless.

## Archetype boilerplate removed

`archetypes/default.md` has been removed from every known consumer
(2026-10) — the files duplicated Hugo's builtin default archetype, and
no script, CI step or documentation uses `hugo new`. Site-specific
templates (`post.md`, `blog.md`) with real front matter (IIIF
resources, content types, object fields) stay where they exist.

## Reuse and merge the theme's i18n strings

Complete (2026-10) — every known consumer audited against the theme's
`i18n/<lang>.toml`: no site ships a full copy of the theme's file (the
stale-translation failure mode). The remaining duplicated keys are
deliberate site-specific overrides — site wording, licensing
(ric-unknownartist's BY-NC-SA `cc` key), plural forms
(kleiderbuegel's `[Tag]`), footer branding — and stay. Two proven-stale
copies were dropped: christianmahnke's HDR keys (they pinned the old
theme value with the "Cromium" typo, fixed upstream) and
kraehenbeisser's `[projektemacher]` footer key (the theme ships the
`alt` attribute since the npm-fonts theme). Hugo's merge behaviour
stands: the site's `i18n/<lang>.toml` wins per key, missing keys fall
back to the theme. The overlap scan lives in the git history of this
file (pre-2026-10).

## Extend lint coverage

Complete (2026-10) — all three blind spots are closed:

- **SCSS is linted recursively** — `lint-scss` runs
  `stylelint 'assets/scss/**/*.scss'`; the generated `assets/scss/npm-fonts/`
  partials are excluded via `ignoreFiles` (they are regenerated on every
  build and can never pass).
- **Markdown is linted** — `lint-md` runs `markdownlint` over `Upgrade.md`
  and the exampleSite content, configured via `.markdownlint.json`.
- **Generated CSS is checked** — `postbuild-lint` stylelints `docs/css/*.css`
  after builds. Consuming sites can adopt the same post-build check to catch
  regressions that only appear in the compiled output.

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

# Upgrading pages that load styles or scripts through `partials/head.html`

Complete — `head.html` is gone from the theme. Every known consumer either
calls the new `html/head/meta.html`/`links.html`/`style.html`/`script.html`
partials or ships a fully custom header (`labs.projektemacher.org`). When
touching this area, verify the built pages have title, meta description,
favicons, the RSS/`iiif-collection` alternates and that shortcode
styles/scripts still load.

# Accessible navigation menu (progressively enhanced checkbox hack)

The theme's menu previously used a pure CSS checkbox hack
(`input#menu-toggle` + `label.menu-button`). The `<label>` toggle was not
keyboard operable (WCAG 2.1.1), exposed no `aria-expanded`/`aria-controls`
(WCAG 4.1.2), and the `:checked + label + ul` sibling selector broke
silently when consumers restructured the markup. The menu is now
progressively enhanced and self-installing:

- `layouts/partials/menu.html` keeps the checkbox hack as the no-JS
  fallback and additionally loads a small script (`assets/ts/menu.ts`,
  built and emitted by the partial itself — no `main.js` wiring needed).
- Once the script runs, the `<label>` is replaced by a real `<button>`
  with `aria-expanded`/`aria-controls`, the list gets `inert` while
  closed (only while the CSS actually hides it, see below), Escape
  closes the menu and returns focus to the toggle, and the menu closes
  on outside clicks or when focus leaves it.
- `assets/scss/menu.scss` keys the open state on `data-menu-open` /
  `data-menu-js` attributes instead of the sibling chain and adds
  `:focus-visible` styles plus `prefers-reduced-motion` handling.
- New i18n keys `openNavigation` and `closeNavigation` label the toggle;
  sites with custom i18n files can add their own translations.

## 1. Consumer migration

Complete (2026-10) — every known consumer verified: sites using the
theme's `menu.html` unchanged get the enhancement automatically
(JavaScript disabled or the script failing leaves the untouched
checkbox hack fully functional). wilmabraeuner and kleiderbuegel run
adopted copies with their customizations re-applied (union menus,
`lang-switch` classes); christianmahnke ships its own already-enhanced
copy with an `idPrefix` extension; backsteinexpressionismus keys its
mobile open state off `.top-menu[data-menu-open="true"]` alongside the
no-JS `:checked` fallback. schatten, yaapb and
haesslicheplastiktiereundzeugs ship custom toggle-less menus to which
the enhancement does not apply. Sites that inline their whole
`<head>`/header without the theme partial get no enhancement and keep
the (accessible enough) no-JS fallback.

## 2. Behaviour changes

- With JavaScript enabled the toggle is announced as a button
  ("Open main navigation"/"Close main navigation", `aria-expanded`).
- Links in the closed mobile menu are no longer tabbable (`inert`),
  including when consumer CSS overrides the hiding rules. The script
  applies `inert` only while the closed list is actually hidden by CSS
  (detected via `getComputedStyle`) — an always-visible desktop
  navigation (`nav.top-menu` shown inline above the mobile breakpoint)
  is never inerted, and viewport resizes re-sync the state. Consumers
  with custom breakpoints (e.g. `35em` instead of the theme's `45em`)
  need no JavaScript-side changes.
- When the viewport crosses into the desktop regime (toggle button
  rendered `display: none`) while the menu is open, the script
  normalizes the state to closed, since the open state is meaningless
  without a rendered toggle.
- Escape, outside clicks and focus leaving the open mobile menu close it
  and return focus to the toggle.

## 3. Verification

- Keyboard only: tab to the burger button, toggle with Enter/Space,
  close with Escape (focus returns to the button), tab through the
  links while open.
- Desktop (viewport wider than the menu breakpoint): confirm the inline
  navigation links are clickable and tabbable and that no `inert`
  attribute is set on the list.
- Screen reader: the toggle announces name, role and
  expanded/collapsed state; list links are unreachable while collapsed.
- Disable JavaScript and confirm the menu still opens/closes via the
  checkbox hack (also test with "Emulate focused page"/scripting off in
  devtools).
- Confirm `prefers-reduced-motion: reduce` disables the open/close
  animation.

# Skip link and list pagination fixes

Two smaller accessibility fixes that change shipped markup. The skip
link fix is complete (2026-10): every known consumer ships an
accessible skip link — sites with their own `baseof.html` copy use the
class-based `.skip-link` markup (the class compiled via the theme's
`theme.scss` import or a local copy), the rest inherit the theme's
version. The pagination labels remain open for sites with drifted
`list.html` / `pagination.html` copies (backsteinexpressionismus,
briefsteller, kleiderbuegel, ric-unknownartist, schriftmuster, yaapb)
— see the deduplication guide above:

- The skip link in `layouts/_default/baseof.html` no longer hides
  itself with an inline style. It now relies on the `.skip-link` class
  (added to `assets/scss/theme.scss`), which reveals the link on
  `:focus` - previously it was unreachable for keyboard users because
  the inline `left: -9999px` could never be overridden.
- `layouts/partials/list.html` had the pagination labels swapped: the
  "previous page" link was labelled `next_page` and vice versa. The
  labels are fixed, and the `◀`/`▶` arrows are wrapped in
  `<span aria-hidden="true">` so screen readers announce the label
  only. The visible text of list pagination changes accordingly.

## Verification

- Keyboard only: the skip link becomes the first focusable element,
  pressing Enter jumps to `#main`.
- Check a paginated list: both links point in the direction their
  labels announce.

# Accessible iframe consent switch (progressively enhanced checkbox hack)

The consent toggle in the `html/iframe-consent` shortcode (and the
`html/iframe-consent.html` partial) previously hid its checkbox with
`display: none`. That removed the control from the tab order entirely:
keyboard users could not consent to embedded content (WCAG 2.1.1), the
`*:focus + .opt-in-slider` style was dead code, and the state was never
exposed to assistive technology. Like the navigation menu, the switch is
now progressively enhanced:

- `layouts/partials/html/iframe-consent.html` keeps the checkbox hack
  as the no-JS fallback - the checkbox is now visually hidden with the
  clip pattern instead of `display: none`, so it is focusable and Space
  toggles it; the slider shows a focus ring via
  `:focus-visible + .opt-in-slider`.
- `assets/ts/iframe-consent.ts` (loaded via the shortcode metadata, no
  wiring needed) replaces the `<label>` hack with a real
  `<button role="switch" aria-checked>` (same class, same slider span).
  The button keeps the hidden checkbox as the state source and
  dispatches `change` on it - consumer code binding to the checkbox
  keeps working. Escape-free single instance per iframe, idempotent.
- `assets/scss/iframe-consent.scss` styles the button switch off
  `[aria-checked]` instead of the `:checked +` sibling chain and adds
  `:focus-visible` styles plus `prefers-reduced-motion` handling for
  the slider transitions.
- The consent detection was fixed on the way: `getConsent()` compared
  the cookie *name* against `"1"` instead of its value, so a stored
  consent was never restored. Returning visitors with a stored consent
  now see the embedded content immediately and the switch reflects the
  state.
- The stale commented-out copy of the markup in
  `layouts/shortcodes/html/iframe-consent.html` was removed.

## 1. Consumer migration

Complete (2026-10) — every known consumer (backsteinexpressionismus,
christianmahnke, kleiderbuegel, kraehenbeisser,
labs.projektemacher.org, vintagereality, wilmabraeuner) verified: no
`skipShortcodeAssets: true` usage and no shortcode, partial or asset
copies, so the enhancement ships with the assets the shortcode helper
loads. vintagereality's `assets/scss/iframe-consent.scss` matches the
theme's current version plus site-specific `.iframe-wrapper` styles.
With JavaScript disabled the (now keyboard operable) checkbox hack
remains fully functional.

## 2. Behaviour changes

- The toggle is announced as a switch with its label ("Accept") and the
  checked/unchecked state; toggling works with Enter and Space.
- Returning visitors with a stored consent cookie get the embedded
  iframe loaded without interaction (previously the consent was saved
  but never acted upon).
- The slider animates only when `prefers-reduced-motion` is not set to
  `reduce`.

## 3. Verification

- Keyboard only: tab to the switch, toggle with Enter/Space, confirm
  the focus ring on both the fallback checkbox and the button.
- Screen reader: the control announces role "switch"/"toggle", the
  label and the state.
- Disable JavaScript and confirm the checkbox still toggles the
  consent via Space (also test with scripting off in devtools).
- Set the consent cookie manually and reload - the iframe content
  should appear and the switch should render as "on".
- Confirm `prefers-reduced-motion: reduce` disables the slider
  animation.

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

# Accessible map and IIIF viewer controls

The OpenLayers based viewers labelled their controls via `title`
attributes only (or not at all - the built-in zoom/full-screen/rotate
buttons render their glyphs via CSS content), so screen readers found
unnamed buttons. Changes:

- The custom rotate controls and the OpenLayers built-in controls now
  expose `aria-label` (same strings as the tooltips, localized de/en).
- Map popups inject `<h2>` for the feature name instead of `<h1>`
  (heading order).
- The Ken Burns style auto pan/zoom animation of the IIIF viewer now
  honours `prefers-reduced-motion: reduce` (it never starts) and can
  be started with the keyboard too (`focusin`/`focusout` alongside
  `mouseenter`/`mouseleave`).

## Consumer migration

Complete (2026-10) — no known consumer styles `.ol-popup-content h1`
(audited), so nothing breaks with the theme's heading change. Drifted
`geojson/popupContent.html` copies (kleiderbuegel, labs.projektemacher.org,
never-built, vintagereality) carry no `h1` styling of their own.

- Sites styling map popups via `.ol-popup-content h1` (font sizes
  etc.) would need to target `h2` instead.
- No other markup changes - the controls keep their classes and
  visuals.

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
packages via `scripts/init/get-fonts.sh` (see the fonts migration guide
above) — the About page should list the families actually imported by the
site's SCSS.

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
