`projektemacher-base` Theme
===========================

# Introduction

# Installation

```
git submodule add https://github.com/cmahnke/projektemacher-base.git themes/projektemacher-base
```

# Site configuration

## CSS deduplication (PostCSS)

On production builds the theme runs the concatenated stylesheet through
PostCSS (`postcss-discard-duplicates`) to remove rules duplicated across
the individually compiled SCSS resources and the plain CSS resources. The
PostCSS configuration ships with the theme
(`assets/_jsconfig/postcss.config.js`) and is picked up automatically by
Hugo — no PostCSS setup is needed in the site. The required npm packages
(`postcss`, `postcss-cli`, `postcss-discard-duplicates`) are part of the
theme's `package.json` and installed with the site's dependencies by
`scripts/init/package.json.sh`.

Notes:

* The step is skipped for `hugo server` (development) builds.
* It can be turned off with:

```toml
[params.css]
  dedupe = false
```

* Without a working Node.js/npm setup the production build fails with
  Hugo's "You need to install PostCSS" error — run the npm install (see
  above) or disable the feature. A missing `postcss-discard-duplicates`
  package alone is not fatal; the CSS then passes through unprocessed.
* Sites providing their own PostCSS configuration should place it in
  `assets/_jsconfig/postcss.config.js` of the site — it takes precedence
  over the theme's file.

## IIIF manifests

To generate IIIF JSON manifests you need to add the `JSON` output format to the site `config.toml`.

```
[outputs]
    page = ["HTML", "JSON"]
```

## Search (Pagefind)

The theme's `search` layout (see `exampleSite/content/search/`) is based
on [Pagefind](https://pagefind.com/) — `@pagefind/modular-ui` and the
`pagefind` CLI ship with the theme's `package.json` and are merged into
the site's dependencies by `scripts/init/package.json.sh`. Pagefind
indexes the **rendered** site, so the index must be (re)built after every
`hugo` run, using the theme's `pagefind-index.yaml` as configuration:

```
npx pagefind --config pagefind-index.yaml
```

Without an index the search page renders, but the search bundle finds
nothing — see "Run the JS runtime check against the example site" in
`Upgrade.md`.

When the site sets `[params.webMcpSearch] enabled = true`, the search is
additionally exposed to AI agents as a WebMCP tool on every page
(opt-in, see the [search page documentation](exampleSite/content/templates/search.md)
under "WebMCP / AI agents").

## Webmentions / Pingback

The theme ships a self-contained PHP collector for
[webmentions](https://www.w3.org/TR/webmention/) and classic pingbacks
(`services/webmentions/`, no database, no read API). Deployment and
data collection share a single connection to the web host
(`DEPLOY_SERVER`/`DEPLOY_USER`/`DEPLOY_PATH`/`DEPLOY_PASS`, defined
once in `scripts/webmention/host.sh`): `scripts/webmention/deploy.sh`
deploys the service, the same workflow harvests the flat files over
that connection and `scripts/webmention/lint.py` merges them, then the
merged `data/webmentions/mentions.json` is committed to the site
repository's `main` branch (`[skip ci]`) — Hugo reads it directly as
build data, no HTTP during the build.

```toml
[params.webmentions]
  endpoint = 'https://example.org/webmentions/endpoint.php'
  advertisePingback = true
```

The theme's default `hugo.toml` already sets
`endpoint = 'https://static.projektemacher.org/services/webmention.php'`;
site configs can override or unset it.

With `endpoint` set the document head advertises the endpoints
(`<link rel="webmention">` plus a `pingback` link by default -
`advertisePingback = false` disables just the pingback link) and
received mentions render below the page content
(`layouts/_partials/webmentions/list.html`, also available as the
`{{< webmentions >}}` shortcode). See
[services/webmentions/README.md](services/webmentions/README.md) for
the complete process, deployment and operations guide.

# Scripts

## Fonts

Fonts are provided by the Fontsource npm packages in `fonts/package.json` and
copied into `static/fonts/` together with generated CSS (`assets/css/fonts/`)
and SCSS (`assets/scss/npm-fonts/`) by:

```
./scripts/fonts.sh
```

Run it before building — sites consuming the theme as a submodule use
`scripts/init/get-fonts.sh` instead. See `Upgrade.md` ("Upgrading fonts to the
npm (Fontsource) based system") for the integration options and the SCSS
migration guide.

## i18n language files (IMPORTANT: run before building)

The `i18n/` directory contains source fragments named `<id>.<lang>.toml` (e.g. `iiif.en.toml`, `theme.de.toml`). The merged files `i18n/en.toml` and `i18n/de.toml` are **generated** (gitignored) and are what Hugo actually loads.

```
./scripts/init/i18n.sh i18n
```

This merges all fragments into `i18n/<lang>.toml` and **deletes the fragments from the worktree** in the process. CI always runs this before any Hugo build (see `.github/workflows/test.yml` and `.github/workflows/deploy.yaml`).

**Gotcha:** if the fragment files are present at build time (e.g. after `git checkout` / `git restore` of `i18n/`), multilingual site builds (exampleSite) fail with a cryptic error like:

```
ERROR error building site: "art-x-3d.de": language: tag is not well-formed
```

That's Hugo's i18n loader parsing the fragment filename `3d.de.toml` as a BCP47 language tag (Go maps the unknown base `3d` to the private-use tag `art-x-3d`). Fix: make sure the fragments are deleted before building — if `i18n/de.toml`/`i18n/en.toml` already exist the merge script skips and leaves them, so either delete the `*.<lang>.toml` fragments manually or remove the merged files and re-run `./scripts/init/i18n.sh i18n`.

**Translation completeness:** CI runs `python ./scripts/check_i18n.py i18n` (the `test_i18n` job) which fails when any language is missing keys that another language defines. The check works on merged files and unmerged fragments alike, so it can also be run locally:

```
python ./scripts/check_i18n.py i18n
```

To enable the merging of node dependencies including the `script` section you may want to add the following snippet to your setup

```
#NPM dependencies
echo "Calling theme scripts"
for SCRIPT in $PWD/themes/projektemacher-base/scripts/init/*.sh ; do
    echo "Running $SCRIPT"
    bash "$SCRIPT"
done
```

# Shortcode dependencies

Some shortcodes shipped with the theme require additional NPM packages and module mounts in the **site**:

| Shortcode | NPM package | Required mount |
|-----------|-------------|----------------|
| `gallery` | `photoswipe` | `source = "node_modules/photoswipe/dist"`, `target = "assets/css/photoswipe"` |
| `model` / `hdr-model` | `three` | – |
| `hdr-model`, `hdr-canvas`, `hdr-check`, `hdr-canvas-check` | `@projektemacher/hdr-canvas` | – |
| `chart` / `csv-chart` | `echarts` | – |

The shortcode asset pipeline (`partials/shortcodes/shortcode-helper.html`) only includes these on pages actually using the shortcode. Missing mounts produce a `warnf` message, the shortcode markup itself still renders.

# Development dependencies

## Dart SASS on Mac OS

Download the binary from https://github.com/sass/dart-sass-embedded/releases and install it to `/usr/local/bin/`.

To use Dart SASS on the command line also install it from brew

```
brew install sass/sass/sass
```

# Docker images

The `docker/` directory holds images used by the project's CI — see
`docker/graphics/README.md`. The images are built and pushed to
`ghcr.io` by the `Publish Docker images` workflow
(`.github/workflows/docker.yml`):

* `ghcr.io/cmahnke/projektemacher-base/graphics` — graphics processing
  (ImageMagick with JXL/UHDR support, libvips, Inkscape, Ghostscript,
  XSLT processor), so CI jobs don't have to install the system packages
  on the runner itself.

# Installation

Checking out as submodule

```
cd themes
git submodule add https://github.com/cmahnke/projektemacher-base.git
git commit
```

Don't forget to add `projektemacher-base` to `config.toml`


# Example site

The [example site](https://cmahnke.github.io/projektemacher-base/) is currently unfinished.

# TODO
* Finish example site
* Include nomalize.js by default
* Finish shortcode metadata

# Tools

* [IIIF validator](https://presentation-validator.iiif.io/)


# Python Modules

# JXL support

JXL images are handled by [pyvips](https://libvips.github.io/pyvips/) — the
Python bindings for libvips, which decodes JXL natively (via libjxl). This
needs a libvips installation with JXL support on the system, no Python
compile step is involved:

* macOS: `brew install vips`
* Debian/Ubuntu: `apt install libvips-tools` (libjxl support is included)
