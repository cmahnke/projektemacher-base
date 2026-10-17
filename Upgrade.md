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
  `security.node.permissions.allowRead` for the theme's `node_modules`, and
  sites bundling their own TS must keep their `node_modules` inside the
  project root.
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
| `layouts/partials/iiif/presentation/mirador.html` | Viewer partial — emits a `DEPRECATED` build warning when called |
| `assets/js/iiif/mirador.js` | `window.addMirador` bootstrap for the partial |
| `assets/scss/mirador.scss` | Viewer styles |

The files stay in place for now (with the warning) and will be removed in a
future release.

## 1. Consumer migration

- Replace direct `partial "iiif/presentation/mirador.html"` calls with the
  [`iiif/presentation` shortcode](exampleSite/content/shortcodes/iiif/presentation.md)
  (TIFY based), or adopt Mirador site locally: copy the partial and
  `assets/js/iiif/mirador.js` / `assets/scss/mirador.scss` into the site's
  own `layouts/` / `assets/` and maintain them there (Mirador is bundled by
  the site itself, see `exampleSite/content/posts/mirador/`).
- Update `[params.iiif] presentationViewer` if it points to
  `js/iiif/mirador.js` — switch to `ts/iiif/tify.ts` (or a site local
  viewer).

## 2. Verification

1. `hugo` — the build finishes and no longer reports
   `[partials/iiif/presentation/mirador.html] DEPRECATED`.
2. Presentation pages render with the TIFY viewer.

# Housekeeping

The changes in this section are **optional**: no consuming site has to apply
them to keep building against the current theme release. They bundle work that
keeps a site aligned with the theme's direction — finishing half-done
migrations, dropping dead compatibility code and adopting the theme's tooling.
Pick items as time allows; each one stands on its own.

## Finish the JS → TypeScript migration

The migration guide above covers the shortcodes that moved to `assets/ts/`.
A few plain-JavaScript sources remain without a TypeScript counterpart:

| Remaining JS source | Notes |
| --- | --- |
| `assets/js/fullscreen.js` | Small helper, no dependencies |
| `assets/js/search.js` | Pagefind UI glue |
| `assets/js/timeline.js` | Thin vis-timeline wrapper |
| `assets/js/iiif/mirador.js` | Mirador viewer bootstrap (deprecated, see the Mirador guide above) |
| `assets/js/maps/projektemacher-map.js` | Vector tile map bootstrap |

Port them to `assets/ts/` and update every reference (page front matter
`js:` entries, `[params.iiif]` viewer settings). The rules from the existing
guide apply unchanged: bundles keep their `.js` targetPath via the
`replaceRE` remap in `script.html`/`iiif-js.html`, and the deprecated
`assets/js` shims can be deleted once nothing references them anymore.

Verify with `npm run typecheck` (strict) and `npm run lint`.

## Add accessibility checks

The theme ships no automated accessibility testing yet. A lightweight setup
for consuming sites: run [axe-core](https://github.com/dequelabs/axe-core)
through the already-present `puppeteer` devDependency against the built
pages. Sketch (not part of the theme — copy and adapt):

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

Iterate over the built HTML files (or a representative subset) and wire the
script as an optional CI job — non-blocking at first, turning it into a
build breaker once the findings are triaged.

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
