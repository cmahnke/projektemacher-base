> **⚠️ Urgent:** the theme still carries deprecations and compatibility
> shims that are scheduled for removal — see
> [Deprecations.md](Deprecations.md) for the full list. Work through the
> items marked urgent there before the next release.

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
  `browser-banner`, `browser-hide-selector`, `code`, `gist`,
  `html/iframe-consent`, `iiif/iiif`, `iiif/presentation`, `lucienne`,
  `maps/osm`, `maps/osm-vector-tiles`, `mastodon`, `mermaid`, `pdf`,
  `pdf-preview`, `tagcloud`
- other pages with JS functionality: the search page (Pagefind, see
  below), the IIIF presentation examples, the i18n strings page with
  its client side table filter, the page specific assets post and the
  html-body test page

The checker also maps requests to the base URL's **origin root** to its
internal webserver, so root-relative resources like CSS
`url(/fonts/…)` load during the check even when the site is deployed
under a path (GitHub Pages project sites). Sites deployed at the origin
root are unaffected.

## Excluded: WebGL and WebGPU

Pages whose JS requires WebGL or WebGPU are deliberately not listed —
the checker runs with 3D APIs disabled (`--disable-gpu --disable-3d-apis`,
see the `-g` flag for GPU emulation via SwiftShader), so
`shortcodes/aframe-3d-model/` and `posts/3d-model/` would either fail or
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
grep -rEl '^{{< ?(maps/|pdf|iiif/|audioplayer|mermaid|lucienne|mastodon|browser-|gist|html/iframe-consent|code)' content

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
> ```
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

```
npm install --save-dev postcss postcss-cli postcss-discard-duplicates
```

## Behaviour and opt-out

* The step only runs for production builds — `hugo server` is unaffected.
* Disable it with:

```toml
[params.css]
  dedupe = false
```

* Without `postcss-cli` the build fails with Hugo's "You need to install
  PostCSS" error. If only the `postcss-discard-duplicates` package is
  missing, the build degrades gracefully and the CSS passes through
  unprocessed.
* A site's own `assets/_jsconfig/postcss.config.js` overrides the theme's.
  Note that Hugo resolves the configuration from `assets/_jsconfig/` first,
  so a `postcss.config.js` in the site root is no longer used for this
  pipeline.
* The exampleSite resolves its dependencies via the new
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
Exception fonts without an npm source (`DSBehrensschrift`,
`FuturaRenner`) keep their handwritten `fonts/` partials. Consumers
without generated files yet (kinderbuecher, wilmabraeuner,
xn--h-zfa.xyz) must run `scripts/init/get-fonts.sh` in their theme
copy after the next submodule raise. The family-name mapping table and
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

Yarn is no longer a supported package manager. The dependency scripts
(`scripts/node/dependency-management.sh`, `scripts/init/package.json.sh`)
**exit with an error** when `DEPENDENCY_MANAGER=yarn` is still set — switch
to `DEPENDENCY_MANAGER=npm` (or `pnpm`, the default). Consumers should:

- delete `yarn.lock` and let `npm install` regenerate `package-lock.json`
- replace `yarn install` / `yarn run X` in CI and package.json scripts with
  the `DEPENDENCY_MANAGER` variable mechanism (`npm install`, `npm run X`)
- drop yarn instructions from their READMEs

## Finish the JS → TypeScript migration

Done — the remaining plain-JS sources are ported (`ts/search.ts`,
`ts/timeline.ts`, `ts/fullscreen.ts`, `ts/maps/projektemacher-map.ts`) or
removed together with Mirador. The unreferenced `assets/js/` shims were
deleted in the 2026-10 cleanup; consumer front matter references `ts/`
paths everywhere.

## Add accessibility checks

The theme ships no automated accessibility testing yet. A lightweight setup
for consuming sites: run [axe-core](https://github.com/dequelabs/axe-core)
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
violation ("Zoom blocked"); sites with a copied viewport tag should adopt
the theme's version and can drop their exclusions of the rule. The a11y
script still excludes `meta-viewport` by default (opt back in with
`--include-meta-viewport`), so scans of older builds remain usable.

## Remove downward compatibility (Hugo < 0.165.0)

The theme declares `min_version = "0.165.0"` in `theme.toml` — that is the
hard floor. Consuming sites should:

1. Pin Hugo ≥ 0.165.0 in CI and deployment scripts (the theme's own
   workflows use `hugo-setup.yml` for this).
2. Remove fallbacks and version guards kept for older Hugo releases.

Known remaining compatibility code: three partials keep a single top-level
`return` statement, because Hugo < 0.166 supports only one value-return per
partial — `layouts/partials/iiif/3/structures.html`,
`layouts/partials/functions/iiif/coerce-language-map.html` and
`layouts/partials/functions/iiif/structure-span.html`. Once a site
guarantees Hugo ≥ 0.166, the natural multi-`return` code can be restored.

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

Consuming sites should run the full init set (or at least the scripts for
assets they use) before `hugo` in CI, and delete vendored copies of
generated assets instead of pinning them — pinned copies go stale and mask
upstream updates, exactly like the duplicate templates above.

## Reuse and merge the theme's i18n strings

Hugo merges translations per key: the site's `i18n/<lang>.toml` wins for
every key it defines, and missing keys fall back to the theme's
`i18n/<lang>.toml`. Consuming sites therefore never copy the theme's
strings — the site file only needs keys that are actually overridden or
genuinely new.

Find keys that are defined in both places (deletion candidates) from the
site root:

```bash
for f in i18n/*.toml; do
  lang="${f##*/}"
  theme="themes/projektemacher-base/i18n/$lang"
  [ -f "$theme" ] || continue
  echo "== $lang: keys defined in both site and theme"
  comm -12 <(grep -E '^\[' "$f" | sort) <(grep -E '^\[' "$theme" | sort)
done
```

A site file that is a full copy of the theme's is the failure mode: it
silently pins stale translations. Missing keys are harmless (the theme
provides them), outdated values are the real danger — the same problem as
with duplicated templates above.

Verify: the scan reports zero duplicated keys, and the multilingual build
renders both overridden and fallback strings.

## Extend lint coverage

The lint setup has known blind spots worth closing (all optional, done one
at a time):

- **SCSS is linted non-recursively** — `lint-scss` runs
  `stylelint 'assets/scss/*'`, so the subdirectories (`scss/shortcodes/`,
  `scss/iiif/`, …) are never linted. Change the glob to
  `'assets/scss/**/*.scss'` — expect new findings in files that were never
  linted, the same effect the `lint-js` coverage change documented in the
  TypeScript guide.
- **Markdown is not linted at all** — `markdownlint-cli` is already a
  devDependency, but no script uses it. Add `lint-md` over the content
  directory (with a `.markdownlint.json` config) to catch broken heading
  hierarchies and inconsistent lists in docs and posts.
- **Generated CSS is not checked** — the theme lints its built CSS
  (`npm run postbuild-lint`, stylelint against `docs/css/*.css`).
  Consuming sites can adopt the same post-build check to catch regressions
  that only appear in the compiled output.

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

* vendor prefixes and fallback rules for engines that no longer need them —
  every removal must be justified by the new browser floor, not done blindly
* `@supports` guards that only paper over pre-2024 browsers (guards
  enabling *new* features stay)
* UA sniffing blocks and IE guards (`documentMode`, conditional comments)
* `browser-banner` / `browser-hide-selector` calls configured for browsers
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
the build. The theme still uses `@import` throughout
(`assets/scss/fonts/*.scss`, `assets/scss/lint_dummy.scss`, the component
styles) — existing builds keep working, so the migration is optional, but
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

* `@use`/`@forward` statements must come before any other rules in a file.
* **Never `@use … as *` a module that exports variables from inside a
  partial** — files loaded via `@import` (consumer entry points, copied
  templates) dump those members into the *global* scope, where they
  collide with the consumer's own pre-declarations (`This module and
  the new module both define a variable named …`). Partials import
  namespaced (`@use "icons";` → `icons.$link-light`); `as *` and
  `… with (…)` belong in entry points (`base.scss`, `lint_dummy.scss`)
  only. This bit `media-info.scss`/`services/cookie-consent.scss`
  (both `as *`-ing `icons`) and broke `backsteinexpressionismus`'s
  build via its `$color-light` pre-declaration.
* Variables overridden *before* an `@import` become module configuration —
  e.g. `@use "theme" with ($font-body-font: …)`. A module can be configured
  only once per compilation, so configure it in the entry point.
* Members no longer leak between modules: every file must `@use` its own
  dependencies (`menu.scss` and `audioplayer.scss` each import
  `functions/color` themselves).
* Plain-CSS imports stay plain CSS statements — `@import "lucienne.css"`
  and the `ol` include (see the comment in `assets/scss/openlayers.scss`)
  are deliberately kept as plain CSS imports by dart-sass. `@use` with the
  same load paths (configured via `includePaths` in `style.html`) resolves
  modules instead — decide per case and let the comparison confirm the
  effect.
* Keep `assets/scss/lint_dummy.scss` importing every component, so
  `npm run lint-scss` still covers the whole tree.

Verify afterwards: `npm run lint` passes and a visual smoke check of the
affected pages shows no styling changes.

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

- Sites using the theme's `menu.html` unchanged need no action — the
  enhancement ships with the partial. With JavaScript disabled or the
  script failing, the untouched checkbox hack remains fully functional
  (the JS-mode marker is only set after successful enhancement).
- Sites that copied `menu.html` into their own layouts keep the old
  checkbox-hack behaviour until they adopt the theme's partial.
- Sites overriding `assets/scss/menu.scss` or the `.menu-button` styles:
  when the enhancement is active the toggle is a `<button class=
  "menu-button">` instead of a `<label>` (same classes and icon). Update
  selectors targeting `label.menu-button` specifically, and note that
  `#menu-toggle:checked + label + ul` no longer matches once the script
  has run — key custom open states off `.top-menu[data-menu-open="true"]`
  instead.
- Sites with their own toggle bound to `#menu-toggle`: the hidden
  checkbox stays in the DOM and the script syncs its `change` events
  with the button state.
- The script tag is emitted per page by `menu.html`; sites that inline
  their whole `<head>`/header without the theme partial get no
  enhancement and keep the (accessible enough) no-JS fallback.

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

Two smaller accessibility fixes that change shipped markup - sites with
drifted copies should adopt the theme's versions (see the deduplication
guide above):

- The skip link in `layouts/_default/baseof.html` no longer hides
  itself with an inline style. It now relies on the `.skip-link` class
  (added to `assets/scss/theme.scss`), which reveals the link on
  `:focus` - previously it was unreachable for keyboard users because
  the inline `left: -9999px` could never be overridden. Sites with a
  copy of `baseof.html` keep the broken inline style until they adopt
  the theme version; sites styling `.skip-link` themselves can drop
  their overrides.
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

- Sites using the shortcode or partial unchanged need no action - the
  enhancement ships with the assets the shortcode helper loads. With
  JavaScript disabled the (now keyboard operable) checkbox hack remains
  fully functional.
- Sites with `skipShortcodeAssets: true` must keep loading
  `ts/iframe-consent.ts` and `scss/iframe-consent.scss` manually (as
  before) to get the enhancement.
- Sites overriding `assets/scss/iframe-consent.scss`: once the
  enhancement is active the toggle is a `<button class="opt-in-switch"
  role="switch">` instead of a `<label>`. Update selectors targeting
  `label.opt-in-switch` specifically, and note that
  `input:checked + .opt-in-slider` no longer matches - key custom open
  states off `button[aria-checked="true"]` instead.
- Sites with their own toggle bound to the checkbox: the hidden
  checkbox stays in the DOM and the button syncs its state with it.

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

- Sites styling map popups via `.ol-popup-content h1` (font sizes
  etc.) need to target `h2` instead.
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
|---|---|
| `.Site.Params.…`, `$.Site.Title`, … | Global `site.` function: `site.Params.…`, `site.Title`, … |
| `paginate = …` site config key | `pagination.pagerSize = …` (the `paginate` key was deprecated in Hugo 0.128.0) |
| `Pager.PageSize` method | `Pager.PagerSize` (renamed in Hugo 0.128.0) |
| `.Language.LanguageCode` method | `.Language.Locale` (deprecated in Hugo 0.158.0) |
| `$.Scratch.Set` / `.Get` / `.Delete` | Plain variables with reassignment (`$x = …` inside `with` blocks, partial return values) |
| bare `substr` | `strings.Substr` — same function, namespaced form (`substr` is just its alias) |

> [!NOTE]
> There is no global `pagination.` function — `.Paginate` remains the
> documented `Page` method for creating pagers. Only the `paginate`
> *configuration key* and the `PageSize` *method* were deprecated in
> Hugo 0.128.0.

Deliberate exceptions in the theme's own templates — not outdated code:

* `layouts/partials/preview/prerendered.html` compares
  `hugo.Sites.Default` against `.context.Site` — a site *identity* check
  (multilingual awareness) that the `site.` global cannot express.
* `layouts/partials/html/head/iiif-js.html` reads the page Scratch key
  `iiifPrefix`. Nothing in the theme sets it — it is a consumer-facing
  extension point, so it cannot become a plain variable. (The former
  `footer` Scratch key was retired: `footer.html` now passes the
  footer string as a partial argument.) Local `newScratch` objects
  (e.g. in `kenburns.html`) are fine as-is; the rule targets
  page/`$`-Scratch state.
* `layouts/partials/pagination.html` still reads `$.Paginator` — as the
  *fallback* branch when the partial is called with a page context; the
  preferred input is the pager object returned by `.Paginate`.
* `layouts/redirect/single.html` calls *and* redefines
  `_internal/alias.html` on purpose: the local alias page carries
  additional meta tags (`noindex`, canonical, charset).

Minor cleanups for the same pass:

* Canonical camelCase for configuration keys: `canonifyURLs`, not
  `canonifyurls` — Hugo matches keys case-insensitively, but the
  documentation and tooling use the camelCase form.
* ~~Nondeterministic element IDs~~ — deliberately **not** pursued:
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

# 5. nondeterministic IDs
grep -rnE 'UnixNano|shuffle' layouts/

# 6. internal alias template shadowing
grep -rn '_internal/alias' layouts/

# 7. .Language.LanguageCode → .Language.Locale (deprecated in 0.158.0)
grep -rn 'LanguageCode' layouts/
```

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
|---|---|
| tify | IIIF presentation viewer |
| OpenLayers, ol-mapbox-style | Maps and the IIIF image viewer |
| @projektemacher/hdr-canvas | HDR rendering in the IIIF image viewer |
| mermaid | Diagrams (`mermaid` shortcode) |
| howler | Audio player |
| pdfobject | PDF viewer and preview |
| vis-timeline | Timeline |
| Pagefind | Search |
| A-Frame | 3D models (loaded from CDN) |
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
