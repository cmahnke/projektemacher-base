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
- other pages with JS functionality: the IIIF presentation examples, the
  page specific assets post and the html-body test page

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
itself — and pages containing maps, PDF viewers and other JS
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

# Pages loading page specific scripts
grep -rEl '^js:' content
```

Keep the list in sync whenever a new shortcode with JS is added or a
page starts using JS functionality.
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

This theme no longer generates Presentation API 2 manifests. The templates
`layouts/_default/single.json` and `layouts/_default/single.iiif.json` (the
former `iiif` output format, `sc:Manifest` / `sc:Sequence` vocabulary) now
abort the build with an `errorf` when a page still opts in via a
`presentation/2` context.

Migrate affected sites to Presentation API 3 (`iiif-manifest` output format,
`layouts/partials/iiif/3/`).

## 1. Site configuration (`config.toml` / `hugo.toml`)

Replace the legacy output format:

```toml
# Remove this
[outputFormats.iiif]
  mediaType = "application/ld+json"
  baseName = "manifest"
  isPlainText = true
  isHTML = false
```

with:

```toml
[mediaTypes."application/ld+json"]
  suffixes = ["json"]

[outputFormats.iiif-manifest]
  mediaType = "application/ld+json"
  baseName = "manifest"
  isPlainText = true
  isHTML = false

# Optional: collections on home / term pages
[outputFormats.iiif-collection]
  mediaType = "application/ld+json"
  baseName = "collection"
  isPlainText = true
  isHTML = false
```

Also extend the home (and optionally term) outputs if collections are wanted:

```toml
[outputs]
  home = ["html", "rss", "iiif-collection"]
```

`isPlainText = true` / `isHTML = false` are required — without them the JSON
is HTML-escaped and invalid.

## 2. Page front matter

A typical API 2 page looks like this:

```yaml
iiifManifest: ./manifest.json
outputs:
- html
- iiif
iiifContext: http://iiif.io/api/presentation/2/context.json
resources:
- src: "front.jpg"
  name: front
  params:
    iiif: front/info.json
```

Change it to:

```yaml
outputs:
- html
- iiif-manifest
iiifcontext: http://iiif.io/api/presentation/3/context.json
iiif:
  manifest: ./manifest.json
resources:
- src: "front.jpg"
  name: front
  params:
    iiif: front/info.json
```

Mapping table for all legacy keys:

| API 2 (legacy) | API 3 (new) | Notes |
|---|---|---|
| `outputs: […, iiif]` | `outputs: […, iiif-manifest]` | Required, otherwise no manifest is rendered |
| `iiifContext: …/presentation/2/…` | `iiifcontext: http://iiif.io/api/presentation/3/context.json` | Keep the flat key — the viewer (`iiif-content.html`, `iiif-js.html`) reads `iiifcontext`, not the nested variant |
| `iiifManifest: ./manifest.json` | `iiif.manifest: ./manifest.json` | Both keys are still read by the viewer; the nested form is preferred |
| `iiifMetadata` | `iiif.metadata` | Build `errorf`s on the legacy key |
| `iiifStructure` | `iiif.structure` | Build `errorf`s on the legacy key |
| `iiifAttribution` | `iiif.attribution` | Build `errorf`s on the legacy key; rendered as `requiredStatement` |
| `iiifLogo` (`img`/`url` below) | `iiif.logo` (`img`/`url` below) | Same sub-keys, just nested |
| `params.canvasheight` / `params.canvaswidth` | — (remove) | Dead keys; API 3 manifests use the real image dimensions |
| `params.hint`, `params.label` | unchanged | Still supported |
| `params.iiif` | unchanged | Image API path, still required |
| `.Site.Params.iiifcanvasheight` / `iiifcanvaswidth` | — (remove) | Only used by the removed API 2 templates |

## 3. Viewers

The default presentation viewer (`ts/iiif/tify.ts`, TIFY via
`[params.iiif] presentationViewer`) supports API 3. No action required unless
the site pins an API 2-only viewer — then switch to TIFY. The bundled Mirador
integration is deprecated (see the deprecation guide below).

## 4. Verification

1. `hugo` — the build must finish without `errorf`. Remaining legacy keys
   produce explicit errors naming the offending page and the replacement key.
2. Validate the generated manifests, e.g. from a consuming site checkout:
   `find docs -name manifest.json -print0 | xargs -0 -n1 npx eslint -c themes/projektemacher-base/eslint.config.mjs`
3. Spot check one manifest: `@context` must be
   `http://iiif.io/api/presentation/3/context.json`, `type` must be
   `Manifest`, canvases under `items`.

## 5. Instructions for agents (automated migration)

Follow this recipe strictly. Do not delete page content — only rewrite keys.

1. **Enumerate candidates** in the consuming site (skip `docs/` build output):
   - `rg -l --glob '!docs/**' 'iiifContext.*presentation/2' content/` → API 2 pages
   - `rg -l --glob '!*docs*' 'outputFormats\.iiif\b' config.toml hugo.toml` → legacy format definition
2. **Fix the config** first (see section 1), so `iiif` no longer resolves.
3. **Rewrite each page's front matter** (front matter block only, between the
   leading `---` markers — never touch the body):
   - `- iiif` → `- iiif-manifest` in `outputs` (match the exact list item, not substrings like `iiif-manifest` or `iiif-collection`)
   - `iiifContext: http://iiif.io/api/presentation/2/context.json` → `iiifcontext: http://iiif.io/api/presentation/3/context.json`
   - `iiifManifest: <url>` → nest under `iiif:` as `manifest: <url>` (merge with an existing `iiif:` block if present)
   - `iiifMetadata:` → `iiif.metadata:`, `iiifStructure:` → `iiif.structure:`, `iiifAttribution:` → `iiif.attribution:` (nest under `iiif:`)
   - `iiifLogo:` block → nest under `iiif:` as `logo:` keeping `img:`/`url:` sub-keys and indentation
   - delete `canvasheight:` / `canvaswidth:` lines inside `params:` blocks
4. **Scripted reference implementation** (run from the site root, Python 3):
   ```python
   import re, pathlib
   for f in pathlib.Path("content").rglob("index.md"):
       text = f.read_text()
       m = re.match(r"(?s)^(---\n)(.*?)(\n---\n)(.*)$", text)
       if not m or "presentation/2" not in m.group(2):
           continue
       head = m.group(2)
       head = re.sub(r"(?m)^(\s*)-\s*iiif\s*$", r"\1- iiif-manifest", head)
       head = head.replace(
           "iiifContext: http://iiif.io/api/presentation/2/context.json",
           "iiifcontext: http://iiif.io/api/presentation/3/context.json")
       head = re.sub(r"(?m)^iiifManifest:\s*(.+)$", r"iiif:\n  manifest: \1", head)
       for old, new in [("iiifMetadata:", "metadata:"),
                        ("iiifStructure:", "structure:"),
                        ("iiifAttribution:", "attribution:")]:
           head = re.sub(r"(?m)^" + old + r"\s*", "iiif:\n  " + new + " ", head)
       head = re.sub(r"(?m)^iiifLogo:\n((?:\s+.+\n)+)",
                     lambda m: "iiif:\n  logo:\n" + re.sub(r"(?m)^(\s+)", r"  \1", m.group(1)), head)
       head = re.sub(r"(?m)^(\s*)(canvasheight|canvaswidth):.*\n", "", head)
       f.write_text(m.group(1) + head + m.group(3) + m.group(4))
       print("migrated", f)
   ```
   Review the diff afterwards — the script is line based and assumes the
   common patterns from section 2.
5. **Verify**: run `hugo`; every remaining `errorf` names the page and the
   replacement — fix those manually. Then run the eslint validation from
   section 4. Done when the build is green and all `docs/**/manifest.json`
   validate.

# Upgrading `iiif.structure` to the shorthand format

Structure entries with hand-written `id`s (IIIF Range objects with absolute
URLs) are no longer supported — the build aborts with an `errorf` on such
entries. Range and canvas identifiers are now generated at build time with
the deployment prefix, so the front matter carries no IDs or URLs and the
generated `structures` always match the manifest's own canvas identifiers.

Migrate affected pages to the shorthand:

```yaml
# Before (legacy)
iiif:
  structure:
    - id: https://static.example.org/post/example/range/vorwort
      type: Range
      label: {de: ["Vorwort"]}
      items:
        - {type: Canvas, id: https://static.example.org/post/example/canvas/page003}

# After (shorthand)
iiif:
  structure:
    - label: {de: ["Vorwort"]}
      page: page003
```

- A `page` reference resolves by the resource's `name`, its `params.iiif`
  directory or its `src` basename (without extension)
- `end:` spans a range over several canvases, nested `items` work as before
- The format is documented in the example site, see
  `exampleSite/content/iiif/page-metadata.md`
- The same shorthand drives the PDF bookmarks in `scripts/pdf.py`

# Upgrading fonts to the npm (Fontsource) based system

Font binaries are no longer tracked in the repository. `static/fonts/` is now
generated by `scripts/fonts.sh` from the Fontsource npm packages listed in
`fonts/package.json` (`@fontsource/*` and `@fontsource-variable/*`). Only fonts
that are not available via npm remain in the repository:
`DSBehrensschrift.otf/.ttf`, `FuturaRenner-Regular.*` and
`alata-regular-webfont.woff/.woff2`.

The theme offers three ways to integrate fonts:

1. **npm SCSS (recommended)** — `scripts/fonts.sh` concatenates each Fontsource
   package's CSS into `assets/scss/npm-fonts/<family>.scss` (gitignored,
   regenerated), with the font path configurable via `$font-base-path`
   (defaults to `/`). Variable font packages additionally get a
   `<family>-variable.scss` copy. Import them from site SCSS.
2. **npm CSS** — the same script writes plain CSS copies to
   `assets/css/fonts/<family>.css` (gitignored). Include them via page/config
   `css:` params or `@import` them from SCSS (`assets/css/fonts` is in the
   built-in Sass include paths).
3. **Handwritten `@font-face`** — the legacy way (`assets/scss/fonts/*.scss`
   referencing `/fonts/<file name>`). The theme's own files now import the
   generated SCSS (see below); only the custom fonts
   (`alata-regular.scss`, `ds-behrensschrift.scss`, `futura-renner.scss`) still
   contain handwritten rules.

## 1. Required steps for all consuming sites

1. Run the font script before building — this downloads the packages and fills
   `static/fonts/`, `assets/css/fonts/` and `assets/scss/npm-fonts/`:

   ```
   # from the site root, theme checked out as submodule
   themes/projektemacher-base/scripts/init/get-fonts.sh
   # or directly:
   themes/projektemacher-base/scripts/fonts.sh themes/projektemacher-base
   ```

   CI must do the same (the theme's own workflows run `./scripts/fonts.sh`
   before every build). Sites that pinned copies of the old `static/fonts/`
   files in their own repository can delete them.
2. Make sure the `assets/` directory is mounted (see
   `exampleSite/content/posts/post-specific-assets/index.md`).
3. Build — SCSS that imports `npm-fonts/*` fails with
   "can't find stylesheet to import" when step 1 was skipped.

`scripts/fonts.sh` also creates the legacy file names (e.g.
`JosefinSans-Bold.woff2`, `cormorant-v10-latin-regular.woff2`,
`lora-v16-latin-700.woff2`) as copies of the npm files, so old `@font-face`
rules keep working unchanged. Intentionally **not** recreated: `.ttf`, `.eot`
and `.svg` fallbacks, the old `-all-` subset files and `.woff` names of
variable-only families — browsers fall through the `src` list to the
`.woff2`/`.woff` entries.

## 2. Migrating SCSS to the npm-fonts imports

Replace handwritten `@font-face` blocks:

```scss
// Before (legacy, references tracked static files)
@font-face {
  font-family: 'Oswald';
  font-style: normal;
  font-weight: 400;
  src: url('/fonts/oswald-latin-400-normal.woff2') format('woff2'),
       url('/fonts/oswald-latin-400-normal.woff') format('woff');
}

// After (generated Fontsource SCSS, run scripts/fonts.sh first)
@import '../npm-fonts/oswald';
```

The relative path works from anywhere inside `assets/scss/`; when importing
from files outside the theme, add the theme's `assets/scss/npm-fonts/`
directory to the Sass `includePaths` and use `@import 'npm-fonts/oswald';`.

### Font family name mapping

Static packages keep their family names (`'Cormorant'`, `'Lato'`,
`'Berkshire Swash'`, …). Variable packages append ` Variable` and declare a
`font-weight` range instead of single weights:

| Legacy family (handwritten SCSS) | New family (npm SCSS) |
|---|---|
| `'EB Garamond'` | `'EB Garamond Variable'` |
| `'Inconsolata'` | `'Inconsolata Variable'` |
| `'Josefin Sans'` | `'Josefin Sans Variable'` |
| `'League Spartan'` | `'League Spartan Variable'` |
| `'Lora'` | `'Lora Variable'` |
| `'Montserrat'` | `'Montserrat Variable'` |
| `'Noto Serif Display'` | `'Noto Serif Display Variable'` |
| `'Nunito'` | `'Nunito Variable'` |
| `'Nunito Sans'` | `'Nunito Sans Variable'` |
| `'Open Sans'` | `'Open Sans Variable'` |
| `'Oswald'` | `'Oswald Variable'` |
| `'Raleway'` | `'Raleway Variable'` |
| `'Sono'` | `'Sono Variable'` |
| `'Source Code Pro'` | `'Source Code Pro Variable'` |

Check the generated `assets/scss/npm-fonts/*.scss` for the exact names and
weight ranges of a package.

### Custom font paths

If fonts are not served from the site root (e.g. a CDN prefix), set
`$font-base-path` **before** the import — the generated files use
`!default`:

```scss
$font-base-path: 'https://static.example.org/fonts/';
@import 'npm-fonts/oswald';
```

### Custom (non-npm) fonts

`DS Behrensschrift`, `Futura Renner` and the original `alata-regular-webfont`
files stay tracked in `static/fonts/` and keep their handwritten SCSS files
(`assets/scss/fonts/alata-regular.scss`, `ds-behrensschrift.scss`,
`futura-renner.scss`). Fonts of your own that npm doesn't provide go the same
way: commit the binaries to the site's `static/fonts/` and keep (or add) a
handwritten `@font-face` file.

## 3. Verification

1. All font references resolve — from the site root:
   ```bash
   for f in $(grep -rohE "url\(['\"]?/fonts/[^'\"]*['\"]?\)" assets/scss | \
              sed -E "s|url\(['\"]?/fonts/||;s|['\"]?\)$||" | sort -u); do
     [ -f "static/fonts/$f" ] || echo "MISSING: $f"
   done
   ```
2. `hugo` builds without Sass errors (npm-fonts imports resolve).
3. Spot check a built page in the browser dev tools: font requests hit
   `/fonts/…` with status 200 and render in the expected family.

## 4. Instructions for agents (automated migration)

1. Run `themes/projektemacher-base/scripts/init/get-fonts.sh` once; abort if it
   fails.
2. For every SCSS file of the site that declares `@font-face` for a family
   listed in the table above (or any family with an `@fontsource(-variable)`
   package in `fonts/package.json`): replace the `@font-face` blocks with
   `@import '<relative path>/npm-fonts/<family>';` — keep any file header
   comments, never touch unrelated rules.
3. Update font usages: replace each legacy family name with the mapped
   `<Name> Variable` name from the table (static families keep their name).
   Font weight declarations can stay — the variable faces accept ranges.
4. Leave handwritten rules for non-npm fonts (custom families) untouched.
5. Verify: run the missing-file loop from section 3, then build with `hugo` —
   done when the build is green and no font request 404s in the built site.

# Upgrading shortcode scripts from `assets/js` to TypeScript (`assets/ts`)

The JavaScript entry points bound to the shortcodes moved from `assets/js/` to
TypeScript sources in `assets/ts/`. Hugo's `js.Build` compiles them with esbuild
— no extra build step is required.

## Moved files

| Old path (deprecated shim) | New path |
|---|---|
| `assets/js/shortcodes/code.js` | `assets/ts/shortcodes/code.ts` |
| `assets/js/mermaid.js` | `assets/ts/mermaid.ts` |
| `assets/js/lucienne/lucienne.js` | `assets/ts/lucienne/lucienne.ts` |
| `assets/js/browser-banner.js` | `assets/ts/browser-banner.ts` |
| `assets/js/audioplayer.js` | `assets/ts/audioplayer.ts` |
| `assets/js/pdf-preview.js` | `assets/ts/pdf-preview.ts` |
| `assets/js/iiif-image-viewer.js` | `assets/ts/iiif-image-viewer.ts` |
| `assets/js/iiif/tify.js` | `assets/ts/iiif/tify.ts` |
| `assets/js/pdf-viewer.js` | `assets/ts/pdf-viewer.ts` |
| `assets/js/iframe-consent.js` | `assets/ts/iframe-consent.ts` |

The old `.js` files are kept as thin, deprecated shims importing the TypeScript
sources, so sites referencing the old paths (page front matter `js:` entries or
the `[params.iiif]` `imageViewer` / `presentationViewer` settings) keep working.
They will be removed in a future release — update the references to the
`ts/` paths instead.

## How to find direct inclusions fast (agent scan)

Run these from the site root to locate every reference that must be updated:

```bash
# 1. Front matter asset references (page/post bundles)
grep -rnE '^\s*(js|scss|css):' content --include='*.md' | \
  grep -E 'assets/(js|ts)/|(js|ts|scss)/'

# 2. Theme viewer settings in site configuration
grep -rn 'imageViewer\|presentationViewer' config hugo.toml config.toml 2>/dev/null

# 3. Direct <script>/<link> includes of the moved assets in layouts
grep -rnE '(src|href)="(assets/)?(js|ts)/' layouts/

# 4. resources.Get / js.Build references in overridden theme partials
grep -rnE 'resources\.Get "(js|ts)/' layouts/
```

## Risks / breakage

* **Shim removal (future release)** — the deprecated `assets/js/*.js` shims will
  be deleted. Sites that don't migrate keep building until then, but bundle
  output for shim entries keeps the *shim's* path as targetPath, so URLs
  don't change; only an update of the reference does.
* **Overridden `script.html`/`iiif-js.html` partials** — sites that copied these
  theme partials must port the `targetPath` `.ts` → `.js` remap
  (`replaceRE "\\.ts$" ".js" $script`). Without it, esbuild output is published
  as a `.ts` file with a non-executable media type and browsers won't run it —
  the page renders but the shortcodes stay dead (no console build error,
  only a browser `404`/wrong MIME type).
* **Strict type checking** — `npm run typecheck` now runs `tsc --noEmit` with
  `strict: true` over `assets/ts/**`. A site's own TypeScript added under
  `assets/ts/` must pass strict mode or the lint job fails.
* **Hugo ≥ 0.167 security model** — `js.Build`/`css.Build` refuse to read files
  outside the project working directory (GHSA-r4xx-89rf-5424). Sites building
  from a subdirectory (like this theme's own `exampleSite/`) need
  `security.node.permissions.allowRead` covering the working directory, the
  project root and the theme's `node_modules` (see the **IMPORTANT** note at
  the top of this file — an override replaces the default `['.']` and must not
  omit them, or `css.PostCSS` fails with "Access to this API has been
  restricted"), and sites bundling their own TS must keep their `node_modules`
  inside the project root.
* **ESLint coverage change** — `lint-js` now lints `assets/js` and `assets/ts`
  recursively. Files that were never linted before (subdirectories, e.g.
  `assets/js/maps/`) can produce new findings, including real bugs
  (the migration itself fixed a `clickFeature` ReferenceError in
  `osm-map.js` found this way).

## 1. Required steps for all consuming sites

1. Update `[params.iiif]` viewer settings to the new paths:
   ```toml
   [params.iiif]
     presentationViewer = "ts/iiif/tify.ts"
     imageViewer = "ts/iiif-image-viewer.ts"
   ```
2. Update page front matter `js:` entries pointing at the moved files
   (find them with the agent scan above).
3. Verify: `npm run typecheck` (runs `tsc --noEmit`, strict) and
   `npm run lint` (ESLint now lints `assets/ts/` too) — then build with
   `hugo`. The built bundles keep their `.js` target paths.

# Shortcodes now load their assets via the shortcode helper

The `pdf`, `html/iframe-consent` and `maps/osm` shortcodes used to require their
JS/CSS to be included globally by the site. They now declare shortcode metadata
and load their assets automatically:

| Shortcode | JS (via metadata) | SCSS (via metadata) |
|---|---|---|
| `pdf` | `ts/pdf-viewer.ts` | `scss/pdf-viewer.scss` |
| `html/iframe-consent` | `ts/iframe-consent.ts` | `scss/iframe-consent.scss` |
| `maps/osm` | `ts/maps/osm-map.ts` (moved from `assets/js/maps/osm-map.js`, which is now a deprecated shim) | `scss/map.scss`, `scss/openlayers.scss` (inlines `node_modules/ol/ol.css` via the Sass include path) |

This removes the last global-function requirements: `addPDFViewer()`,
`addConsent()` and `window.initMap()` are now only guaranteed to exist on pages
that actually use the corresponding shortcode.

## How to find direct inclusions fast (agent scan)

Every reference that should be **removed** from a consuming site (the assets
now load automatically):

```bash
# 1. Page front matter / bundle params loading the moved assets globally
grep -rnE '^\s*(js|scss|css):' content --include='*.md' | \
  grep -E 'pdf-viewer|iframe-consent|osm-map|map\.scss|openlayers|ol\.css'

# 2. Direct script/link tags in overridden layouts and head partials
grep -rnE 'pdf-viewer|iframe-consent|osm-map|openlayers|ol\.css' layouts/ | \
  grep -E '<script|<link|resources\.Get|\.js|\.css'

# 3. Sites that bundled the maps JS themselves
grep -rn 'initMap\|addConsent\|addPDFViewer' layouts/
```

Each hit is a candidate for deletion — the shortcode helper now attaches the
same assets per page.

## Risks / breakage

* **`skipShortcodeAssets: true` disables automatic loading** — sites with this
  parameter MUST keep their manual includes for these three shortcodes; the
  helper won't load anything for any shortcode then.
* **Shortcodes inside non-parsed content aren't detected** — the helper relies
  on Hugo's `HasShortcode`. Shortcode calls inside content fetched at runtime
  (e.g. via `html/include` from external files, or injected into
  `html/rawhtml`) are invisible to it — those pages keep needing manual
  includes of the assets above.
* **OpenLayers base CSS is now inlined per osm page** — pages using
  `maps/osm` grow by the full `ol.css` (~6 KB minified) plus `scss/map.scss`.
  Sites with custom OpenLayers CSS overrides loaded after the theme bundle are
  unaffected (source order: theme head bundles come before site CSS); sites
  that patched `ol.css` behavior by *omitting* it get a behavior change — the
  default OpenLayers control styles now apply.
* **Double inclusion** — keeping old manual includes alongside the metadata
  loading is harmless at runtime (the globals are only reassigned, no listeners
  are bound at module scope), but wastes bandwidth and can cause
  "load order lottery" if the site's own copy loads *after* the theme bundle:
  the site's version of `initMap`/`addConsent`/`addPDFViewer` would win.
  Remove the manual includes instead of relying on that.
* **`maps/osm` behavior fix** — the TypeScript port of `osm-map.js` declares
  the previously-undeclared `clickFeature`/`iconStyle` variables; the cluster
  click popup no longer throws a `ReferenceError`. Sites that (accidentally)
  depended on the old broken behavior of silently doing nothing on cluster
  clicks will see popups now.
* **Sass include-path pitfalls** — `scss/openlayers.scss` must keep
  `@import "ol";` (no `.css` suffix, and the file must not be named `ol.scss`):
  a `.css` suffix is kept as a plain CSS `@import` statement (styles missing at
  runtime), and `ol.scss` would import itself (circular load build error).
* **Generated npm-fonts in CI** — `scss/map.scss` (now loaded by `maps/osm`
  pages) imports the generated `assets/scss/npm-fonts/*` files. Every workflow
  that builds a site using this theme must run `scripts/fonts.sh` (or
  `scripts/init/get-fonts.sh`) before `hugo` — otherwise the build fails with
  "Can't find stylesheet to import". The theme's own CI does this in all
  build jobs.

## 1. Required steps for all consuming sites

Remove the now redundant global includes for these assets (page front matter
`js:`/`scss:` entries or head includes) — loading them twice is harmless at
runtime but wastes bandwidth:
* `ts/pdf-viewer.ts` / `assets/js/pdf-viewer.js`
* `ts/iframe-consent.ts` / `assets/js/iframe-consent.js` and `scss/iframe-consent.scss`
* `assets/js/maps/osm-map.js`, the OpenLayers CSS and `scss/map.scss`

## 2. Verification

1. `hugo` builds without warnings about missing assets.
2. The affected pages load their per-page bundles (visible in the built HTML as
   additional `<script>` tags).
3. `npm run typecheck` stays green (`ts/maps/osm-map.ts` is part of the strict
   TypeScript setup now).

# Hugo site parsers merged into PyHugo

The repository previously had multiple independent Hugo site parsers: the
`scripts/PyHugo` package, a deprecated `Posts.py` class inside it and an inline
configuration/front matter parser in `scripts/preview.py`. Everything now uses
`scripts/PyHugo` exclusively, and its README documents the resulting API.

## What was removed

* `scripts/PyHugo/Posts.py` — the deprecated parser class (it exited the
  process on construction). Use `PyHugo.Content` / `PyHugo.Post` instead.
* `scripts/PyHugo/setup.py` — build file of the long-deleted Go based
  prototype. The package stays importable in place; `pyproject.toml` remains
  for packaging.
* `scripts/preview.py` — the inline `loadConfig()`/`readMetadata()` functions
  (both carried a "Move to PyHugo" TODO). Site configuration is now loaded via
  `PyHugo.Config`, front matter via `PyHugo.Post`.

## 1. Consumer migration

Scripts parsing Hugo sites should use the PyHugo API:

```python
import sys, os
sys.path.append(os.path.dirname(__file__))  # the scripts/ directory
from PyHugo import Config, Content, Post

config = Config(".")                        # site configuration, merged from config/_default
content = Content(config.contentDir(), config=config)
for post in content.posts:                  # includes section pages
    for lang, file in post.files.items():   # language variants of the bundle
        title = post.getMetadata(lang).get("title")
```

* `from content import Post, Content` (with `scripts/PyHugo` on `sys.path`)
  must become `from PyHugo import Post, Content` (with `scripts/` on
  `sys.path`), as done in `scripts/pdf.py`.
* `Posts.Posts(paths).postList()` has no replacement — use `Content` per
  content directory, as done in `scripts/post-calendar.py`. Note that the old
  class crashed on construction, so nothing was using it successfully.
* Front matter lookups now go through `Post.getMetadata()` /
  `Post.getParam()`; the old `readMetadata()` flattened the `params` section
  into the root metadata — use the `params`-aware helpers instead.

## 2. Behaviour changes

* `Config`/`Site` also find `config/_default/config.toml` (previously only
  root `config.toml`/`hugo.toml`) and merge the `config/_default/*.toml`
  overrides recursively instead of replacing sections.
* A relative `publishDir` in `Published` is resolved against the site's base
  directory (previously against the process working directory).
* `Tags`, `Tag`, `Published.postList()` and `Post.addMetadata()` were broken
  (crashed on use) and are fixed now.
* Front matter lookups with an unloaded language fall back to the unsuffixed
  file instead of raising `KeyError`.
* `post-calendar.py` now deduplicates language variants sharing an unsuffixed
  file (one event per post instead of one per file) and honours
  `displayInList`/`draft` front matter keys case insensitively — posts with
  `displayinlist: false` are excluded from the calendar now (previously a
  bug kept them in).

## 3. Verification

1. `python3 scripts/PyHugo/test-pyhugo.py -b exampleSite/` passes.
2. `preview.py` produces the same `ogPreview*.svg` output as before (titles,
   font size auto shrink, `textLength` attributes).
3. `post-calendar.py` emits a valid ICS calendar (`BEGIN:VCALENDAR`).

# Deprecation of the Mirador viewer

The Mirador integration is deprecated — the `iiif/presentation` shortcode no
longer uses it and renders the TIFY based viewer (`ts/iiif/tify.ts`) instead.
Deprecated parts:

| File | Role |
| --- | --- |
| `layouts/partials/iiif/presentation/mirador.html` | Viewer partial |
| `assets/js/iiif/mirador.js` | `window.addMirador` bootstrap for the partial |
| `assets/scss/mirador.scss` | Viewer styles |

These files have been removed from the theme. Sites still calling the partial
get a build error until they migrate. The local Mirador build documentation
(`exampleSite/content/posts/mirador/`) and the accompanying `patches/`
directory (mirador patch files) have been removed as well.

## 1. Consumer migration

- Replace direct `partial "iiif/presentation/mirador.html"` calls with the
  [`iiif/presentation` shortcode](exampleSite/content/shortcodes/iiif/presentation.md)
  (TIFY based), or adopt Mirador locally: maintain your own copies of the
  former viewer partial, `assets/js/iiif/mirador.js` and
  `assets/scss/mirador.scss` in the site's own `layouts/` / `assets/` —
  they are no longer shipped by the theme (Mirador is bundled by the site
  itself).
- Update `[params.iiif] presentationViewer` if it points to
  `js/iiif/mirador.js` — switch to `ts/iiif/tify.ts` (or a site local
  viewer).

## 2. Verification

1. `hugo` — calling the removed `iiif/presentation/mirador.html` partial now
   fails the build, so a clean build proves no call remains.
2. Presentation pages render with the TIFY viewer.

# Housekeeping

The changes in this section are **optional**: no consuming site has to apply
them to keep building against the current theme release. They bundle work that
keeps a site aligned with the theme's direction — finishing half-done
migrations, dropping dead compatibility code and adopting the theme's tooling.
Pick items as time allows; each one stands on its own.

## Finish the JS → TypeScript migration

The migration guide above covers the shortcodes that moved to `assets/ts/`.
The remaining plain-JavaScript sources have been ported or dropped:

| Former JS source | Outcome |
| --- | --- |
| `assets/js/search.js` | Ported to `assets/ts/search.ts` — ambient declarations for `@pagefind/modular-ui` added to `assets/ts/vendor.d.ts` |
| `assets/js/timeline.js` | Ported to `assets/ts/timeline.ts` — `window.addTimeline` declared in `assets/ts/globals.d.ts` |
| `assets/js/iiif/mirador.js` | Removed together with the Mirador integration (see above) |
| `assets/js/maps/projektemacher-map.js` | Removed — superseded by `assets/ts/maps/projektemacher-map.ts` (which `mapWrapper.ts` imports) |

The `replaceRE` remap in `script.html`/`iiif-js.html` keeps `.ts` sources
building to `.js` target paths, so page front matter references stay
compatible.

Unreferenced legacy shims in `assets/js/` that already have an `assets/ts/`
counterpart (e.g. `maps/osm-map.js`, `iiif/tify.js`,
`lucienne/lucienne.js`, `iiif-image-viewer.js`, …) are left in place for now;
their deletion can happen in a later cleanup round once consumers are
re-verified.

Verify with `npm run typecheck` (strict) and `npm run lint`.

### Fullscreen helper ported to TypeScript

`assets/js/fullscreen.js` was ported to `assets/ts/fullscreen.ts`
(`window.addFSToggle`), the old shim is deleted:

1. Update page front matter `js:` entries from `js/fullscreen.js` to
   `ts/fullscreen.ts` — the bundle is emitted as `ts/fullscreen.js`.
2. The API is unchanged (`addFSToggle(button, elem)`), but the helper
   now syncs `aria-pressed` on the button and listens for
   `fullscreenchange`, so leaving fullscreen via Escape or the browser
   UI resets the button state instead of leaving it stale (WCAG 4.1.2).
   Sites depending on the old stale-state behaviour need no action.
3. The theme still does not wire `#fullscreen-button` automatically:
   consuming sites keep calling `window.addFSToggle(document.
   getElementById('fullscreen-button'), document.
   getElementById('fullscreen-context'))` themselves. The button in
   `layouts/_default/html-body.html` stays inert otherwise.

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

### Known false positive: "Zoom blocked"

The theme deliberately blocks pinch zoom on mobile: the viewport partial
(`layouts/partials/html/head/viewport.html`) emits `user-scalable=no` when
`[params] disableScale = true` is set. Accessibility tools report this as
the `meta-viewport` violation ("Zoom blocked"). This is **intended
behaviour** — never "fix" it. Exclude the `meta-viewport` rule from the
scan instead.

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

# Upgrading pages that load styles through `partials/head.html`

`layouts/partials/head.html` no longer compiles and links `scss/base.scss`
itself. `layouts/_default/baseof.html` already emits the stylesheet via
`partials/html/head/style.html`, which covers a superset of the old rules
(plus shortcode and page specific SCSS/CSS). With both in place the compiled
CSS was linked twice per page (same content, different file names), costing
bandwidth and hiding style regressions.

## 1. Consumer migration

- Sites using the theme's `baseof.html` unchanged need no action.
- Sites with a custom `baseof.html` that calls `partials/head.html` but not
  `partials/html/head/style.html` get no stylesheet at all any more — add
  `{{ partial "html/head/style.html" (dict "context" . "css" "css/style.css") }}`
  to their `<head>`.
- Sites with a copy of `partials/head.html` carry an unused duplicate —
  delete the `scss/base.scss` resource block there to match the theme.

## 2. Verification

Build the site and confirm every page has exactly one stylesheet `<link>`
per merged CSS bundle, and that shortcode styles still load (check pages
using shortcodes with dedicated SCSS/CSS includes).

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
it should be modernized — the theme's development uses the right-hand
column, and newer Hugo features expect it:

| Outdated | Replacement |
|---|---|
| `.Site.Params.…`, `$.Site.Title`, … | Global `site.` function: `site.Params.…`, `site.Title`, … |
| `$.Paginator` / `.Paginate …` | Global `pagination.` function (Hugo ≥ 0.128.0) with the `[pagination]` site configuration |
| `$.Scratch.Set` / `.Get` / `.Delete` | Plain variables with reassignment (`$x = …` inside `with` blocks, partial return values) |
| bare `substr` | `strings.Substr` — same function, namespaced form (`substr` is just its alias) |

Minor cleanups for the same pass:

* Copies that call *and* redefine the internal alias template
  (`_internal/alias.html`, see `layouts/redirect/single.html` for the
  pattern) — drop the local redefinition, Hugo's built-in alias template
  covers redirects.
* Canonical camelCase for configuration keys: `canonifyURLs`, not
  `canonifyurls` — Hugo matches keys case-insensitively, but the
  documentation and tooling use the camelCase form.
* Element IDs built from `now.UnixNano` inside `md5` make builds
  nondeterministic — replace them with deterministic IDs (a page-scoped
  counter, or a hash over stable content) so rebuilds produce identical
  HTML.

Find the candidates from the site root — site-owned layouts first; for
copied theme files run the deduplication scan under "Housekeeping" first:

```bash
# 1. .Site. / $.Site. → site.
grep -rnE '\$?\.Site\.' layouts/

# 2. .Paginator / .Paginate → pagination function
grep -rnE 'Paginat(e|or)' layouts/

# 3. Scratch → plain variables
grep -rn 'Scratch' layouts/

# 4. bare substr → strings.Substr (exclude JS substring() calls; strings.Substr doesn't match)
grep -rn 'substr' layouts/ | grep -v 'substring'

# 5. nondeterministic IDs
grep -rn 'UnixNano' layouts/

# 6. internal alias template shadowing
grep -rn '_internal/alias' layouts/
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
| Bootstrap (JS) | Tabs in the horizontal timeline only |

Known stale entries to watch for: the theme does not use **OpenSeadragon**
or **three.js** directly anymore — OpenSeadragon ships only as tify's
internal dependency (and the theme's `package.json` pins a different major
version than tify requires), three.js is an unused devDependency. Remove
them if they are listed standalone. Fonts come from the Fontsource npm
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
