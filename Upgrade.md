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

The default presentation viewer (`js/iiif/tify.js`, TIFY via
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
