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
the site pins an API 2-only viewer — then switch to TIFY or the bundled
Mirador (`js/iiif/mirador.js`, see `exampleSite/content/posts/mirador/`).

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

## 1. Required steps for all consuming sites

1. Update `[params.iiif]` viewer settings to the new paths:
   ```toml
   [params.iiif]
     presentationViewer = "ts/iiif/tify.ts"
     imageViewer = "ts/iiif-image-viewer.ts"
   ```
2. Update page front matter `js:` entries pointing at the moved files.
3. Verify: `npm run typecheck` (runs `tsc --noEmit`, strict) and
   `npm run lint` (ESLint now lints `assets/ts/` too) — then build with
   `hugo`. The built bundles keep their `.js` target paths.
