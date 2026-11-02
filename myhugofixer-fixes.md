# Hugo migration notes per version (myhugofixer)

Assembled verbatim from <https://github.com/bep/myhugofixer/tree/main/fixes> — fetched 2026-11-02, covering Hugo v0.55.0 to v0.169.0.

This theme pins Hugo >= 0.166.0 (`theme.toml` / `[module.hugoVersion]` in `hugo.toml`); the notes for v0.158.0 and newer are the relevant fix items here, see also [Upgrade.md](Upgrade.md).

## Contents

- [v0.55.0 Deprecations](#v0550-deprecations)
- [v0.62.0 Deprecations](#v0620-deprecations)
- [v0.75.0 Deprecations](#v0750-deprecations)
- [v0.92.0 Deprecations](#v0920-deprecations)
- [v0.96.0 Deprecations](#v0960-deprecations)
- [v0.98.0 Deprecations](#v0980-deprecations)
- [v0.110.0 Deprecations](#v01100-deprecations)
- [v0.114.0 Deprecations](#v01140-deprecations)
- [v0.116.0 Deprecations](#v01160-deprecations)
- [v0.120.0 Deprecations](#v01200-deprecations)
- [v0.123.0 Deprecations](#v01230-deprecations)
- [v0.124.0 Deprecations](#v01240-deprecations)
- [v0.127.0 Deprecations](#v01270-deprecations)
- [v0.128.0 Deprecations](#v01280-deprecations)
- [v0.129.0 Deprecations](#v01290-deprecations)
- [v0.141.0 Deprecations](#v01410-deprecations)
- [v0.144.0 Deprecations](#v01440-deprecations)
- [v0.145.0 Deprecations](#v01450-deprecations)
- [v0.146.0 Deprecations](#v01460-deprecations)
- [v0.148.0 Deprecations](#v01480-deprecations)
- [v0.149.0 Deprecations](#v01490-deprecations)
- [v0.150.0 Deprecations](#v01500-deprecations)
- [v0.153.0 Deprecations](#v01530-deprecations)
- [v0.155.0 Deprecations](#v01550-deprecations)
- [v0.156.0 Deprecations](#v01560-deprecations)
- [v0.158.0 Deprecations](#v01580-deprecations)
- [v0.161.0 Notes](#v01610-notes)
- [v0.163.0 Deprecations](#v01630-deprecations)
- [v0.164.0 Deprecations](#v01640-deprecations)
- [v0.165.0 Notes](#v01650-notes)
- [v0.166.0 Notes](#v01660-notes)
- [v0.167.0 Deprecations](#v01670-deprecations)
- [v0.169.0 Deprecations](#v01690-deprecations)

---

## v0.55.0 Deprecations

#### Page methods moved to .File

The following `.Page` methods are deprecated. Use the `.File` equivalent instead:

- `.Page.Filename` → `.File.Filename`
- `.Page.Dir` → `.File.Dir`
- `.Page.Extension` → `.File.Extension`
- `.Page.Ext` → `.File.Ext`
- `.Page.LogicalName` → `.File.LogicalName`
- `.Page.BaseFileName` → `.File.BaseFileName`
- `.Page.TranslationBaseName` → `.File.TranslationBaseName`
- `.Page.ContentBaseName` → `.File.ContentBaseName`
- `.Page.UniqueID` → `.File.UniqueID`
- `.Page.FileInfo` → `.File.FileInfo`

#### Other deprecated Page methods

- `.Page.IsDraft` → Use `.Draft` instead.
- `.Page.Hugo` → Use the global `hugo` function instead.
- `.Page.LanguagePrefix` → Use `.Site.LanguagePrefix` instead.
- `.Page.GetParam` → Use `.Param` or `.Params.myParam` instead.
- `.Page.RSSLink` → Use the Output Format's link, e.g. `{{ with .OutputFormats.Get "RSS" }}{{ .RelPermalink }}{{ end }}`.
- `.Page.URL` → Use `.Permalink` or `.RelPermalink`. For the front matter URL value, use `.Params.url`.

#### Deprecated Site methods

- `.Site.Permalinks` → Removed, no replacement.
- `.Site.Ref` → Use `.Site.GetPage` instead.
- `.Site.RelRef` → Use `.Site.GetPage` instead.

---

## v0.62.0 Deprecations

#### Amber and ACE template engines removed

- **Amber templates** are no longer supported. Use Go templates or a Hugo version <= 0.60.
- **ACE templates** are no longer supported. Use Go templates or a Hugo version <= 0.60.

---

## v0.75.0 Deprecations

#### CLI flag --ignoreVendor

- `--ignoreVendor` → Use `--ignoreVendorPaths "**"` instead.

---

## v0.92.0 Deprecations

#### .Page.Path on file-backed pages

- `.Path` when the page is backed by a file is deprecated. Hugo plans to use `.Path` for a canonical source path. Check the source is a file and use `.File`-based accessors instead.

---

## v0.96.0 Deprecations

#### .File.Extension

- `.File.Extension` → Use `.File.Ext` instead.

---

## v0.98.0 Deprecations

#### .Page.Author and .Page.Authors

- `.Page.Author` → Use taxonomies instead.
- `.Page.Authors` → Use taxonomies instead.

---

## v0.110.0 Deprecations

#### Config file renamed from config to hugo

The default config file is now `hugo.toml` (or `hugo.yaml`/`hugo.json`) instead of `config.toml` (or `config.yaml`/`config.json`).

Both names still work, but if both exist, `hugo.*` takes precedence. Rename your config file:

- `config.toml` → `hugo.toml`
- `config.yaml` → `hugo.yaml`
- `config.json` → `hugo.json`

The same applies to files inside config directories, e.g. `config/development/config.toml` → `config/development/hugo.toml`.

---

## v0.114.0 Deprecations

#### CLI flags

- `--verbose` → Use `--logLevel info` instead.
- `--debug` → Use `--logLevel debug` instead.

#### .Site.RSSLink

- `.Site.RSSLink` → Use the Output Format's Permalink method instead, e.g. `.OutputFormats.Get "RSS" | .Permalink`.

---

## v0.116.0 Deprecations

#### Deprecated kind name "taxonomyTerm"

- The kind `taxonomyTerm` in `disableKinds` and `outputs` configuration is deprecated. Use `taxonomy` instead.

---

## v0.120.0 Deprecations

#### Site methods

- `.Site.IsServer` → Use `hugo.IsServer` instead.
- `.Site.DisqusShortname` → Use `.Site.Config.Services.Disqus.Shortname` instead.
- `.Site.GoogleAnalytics` → Use `.Site.Config.Services.GoogleAnalytics.ID` instead.

#### Template functions

- `collections.EchoParam` (aka `echoParam`) → Use the `index` function instead.
- `lang.NumFmt` → Use `lang.FormatNumberCustom` instead.

---

## v0.123.0 Deprecations

#### Page navigation

- `.Page.NextPage` → Use `.Page.Next` instead.
- `.Page.PrevPage` → Use `.Page.Prev` instead.

#### Site

- `.Site.LastChange` → Use `.Site.Lastmod` instead.

#### File

- `.Page.File.Lang` → Use `.Page.Language.Lang` instead.

#### Data functions

- `data.GetCSV` → Use `resources.Get` or `resources.GetRemote` with `transform.Unmarshal`.
- `data.GetJSON` → Use `resources.Get` or `resources.GetRemote` with `transform.Unmarshal`.

---

## v0.124.0 Deprecations

#### Hugo global

- `hugo.IsMultiHost` → Use `hugo.IsMultihost` instead (lowercase 'h').

#### Site methods

- `.Site.Author` → Use taxonomies instead.
- `.Site.Authors` → Use taxonomies instead.
- `.Site.Social` → Use `.Site.Params` instead.
- `.Site.IsMultiLingual` → Use `hugo.IsMultilingual` instead.

---

## v0.127.0 Deprecations

#### .Sites.First

- `.Sites.First` → Use `.Sites.Default` instead.

---

## v0.128.0 Deprecations

#### Pagination config keys

- Site config key `paginate` → Use `pagination.pagerSize` instead.
- Site config key `paginatePath` → Use `pagination.path` instead.

#### Pagination method

- `.Paginator.PageSize` → Use `.Paginator.PagerSize` instead.

#### Resource transformation functions

- `resources.ToCSS` → Use `css.Sass` instead.
- `resources.PostCSS` → Use `css.PostCSS` instead.
- `resources.Babel` → Use `js.Babel` instead.

---

## v0.129.0 Deprecations

#### crypto.FNV32a

- `crypto.FNV32a` → Use `hash.FNV32a` instead.

---

## v0.141.0 Deprecations

#### Twitter → X config key rename

The `twitter` config keys have been renamed to `x`:

- `privacy.twitter.disable` → Use `privacy.x.disable` instead.
- `privacy.twitter.enableDNT` → Use `privacy.x.enableDNT` instead.
- `privacy.twitter.simple` → Use `privacy.x.simple` instead.
- `services.twitter.disableInlineCSS` → Use `services.x.disableInlineCSS` instead.

#### Twitter shortcode renamed to X

The `twitter` and `tweet` embedded shortcodes are deprecated. Use the `x` shortcode instead. Similarly, `twitter_simple` is replaced by `x_simple`.

---

## v0.144.0 Deprecations

#### Permalink tokens

- The `:filename` permalink token → Use `:contentbasename` instead.
- The `:slugorfilename` permalink token → Use `:slugorcontentbasename` instead.

#### Front matter keys

- Using `path`, `kind`, or `lang` in front matter is deprecated. These are now reserved for Hugo's internal use.

---

## v0.145.0 Deprecations

#### _build front matter key

- The `_build` front matter key → Use `build` (without underscore) instead. See https://gohugo.io/content-management/build-options/.

---

## v0.146.0 Deprecations

#### Template system restructured

Hugo v0.146.0 reimplements and simplifies the template system. The old layout conventions still work but are considered legacy and will eventually be removed. Upgrade your layouts directory as follows:

##### Remove `_default` directory

The `_default` directory is no longer needed. Move templates out of it:

- `layouts/_default/single.html` → `layouts/page.html`
- `layouts/_default/list.html` → `layouts/list.html`
- `layouts/_default/baseof.html` → `layouts/baseof.html`
- `layouts/_default/terms.html` → `layouts/taxonomy.html`
- `layouts/_default/taxonomy.html` → `layouts/term.html` (note: the old naming was confusing — what was called "taxonomy" in `_default` actually rendered individual terms)

##### Rename `single` to `page`

The layout name `single` is now `page`:

- `layouts/_default/single.html` → `layouts/page.html`
- `layouts/posts/single.html` → `layouts/posts/page.html`

##### Add underscore prefix to `partials` and `shortcodes`

The `partials` and `shortcodes` directories now use an underscore prefix:

- `layouts/partials/` → `layouts/_partials/`
- `layouts/shortcodes/` → `layouts/_shortcodes/`

##### Rename `index.html` for home page

The home page template `index.html` is now `home.html`:

- `layouts/index.html` → `layouts/home.html`

##### Baseof template naming

The baseof template naming convention has changed. The identifier that was hyphen-prepended before `baseof` is now dot-appended after it:

- `layouts/_default/list-baseof.html` → `layouts/baseof.list.html`
- `layouts/docs/list-baseof.html` → `layouts/docs/baseof.list.html`

##### Summary of common migrations

| Old path | New path |
|----------|----------|
| `layouts/_default/single.html` | `layouts/page.html` |
| `layouts/_default/list.html` | `layouts/list.html` |
| `layouts/_default/baseof.html` | `layouts/baseof.html` |
| `layouts/_default/terms.html` | `layouts/taxonomy.html` |
| `layouts/index.html` | `layouts/home.html` |
| `layouts/partials/header.html` | `layouts/_partials/header.html` |
| `layouts/shortcodes/mysc.html` | `layouts/_shortcodes/mysc.html` |
| `layouts/_default/list-baseof.html` | `layouts/baseof.list.html` |

---

## v0.148.0 Deprecations

#### Render hook config keys

- `markup.goldmark.renderHooks.image.enableDefault` → Use `markup.goldmark.renderHooks.image.useEmbedded` instead. Set to `"never"` if previous value was `false`, or `"fallback"` if previous value was `true`.
- `markup.goldmark.renderHooks.link.enableDefault` → Use `markup.goldmark.renderHooks.link.useEmbedded` instead. Set to `"never"` if previous value was `false`, or `"fallback"` if previous value was `true`.

---

## v0.149.0 Deprecations

#### chromastyles --omitEmpty flag

- The `--omitEmpty` flag on the `gen chromastyles` command is deprecated. Empty classes are now always omitted; the flag is no longer needed.

---

## v0.150.0 Deprecations

#### Minify config keys

- Top-level `minifyOutput` config key → Use `minify.minifyOutput` instead.
- `minify.tdewolff.json.decimal` (and similar `decimal` keys) → Use `precision` instead.
- `minify.tdewolff.html.keepConditionalComments` → Use `keepSpecialComments` instead.
- `minify.tdewolff.css.keepCSS2` → Use `version` instead.

---

## v0.153.0 Deprecations

#### Module mount config

- `module.mounts.includeFiles` → Replaced by the simpler `files` setting. See https://gohugo.io/configuration/module/#files.
- `module.mounts.excludeFiles` → Replaced by the simpler `files` setting. See https://gohugo.io/configuration/module/#files.
- `module.mounts.lang` → Replaced by the more powerful `sites.matrix` setting. See https://gohugo.io/configuration/module/#mounts.

#### Config segments

- `segments.[...].lang` → Use `sites.matrix` instead. See https://gohugo.io/configuration/segments/#segment-definition.

#### Cascade target

- `cascade.target.language` → Use `cascade.target.sites.matrix` instead. See https://gohugo.io/content-management/front-matter/#target.

#### css.Sass with libsass

- Using `css.Sass` with libsass transpiler is deprecated. Use Dart Sass instead. See https://gohugo.io/functions/css/sass/#dart-sass.

---

## v0.155.0 Deprecations

#### Image.Exif

- `.Image.Exif` → Use `.Image.Meta.Exif` instead. See [https://gohugo.io/content-management/image-processing/#meta.](https://gohugo.io/methods/resource/meta/#exif).

---

## v0.156.0 Deprecations

#### Site methods

- `.Site.Sites` and `.Page.Sites` → Use `hugo.Sites` instead.
- `.Site.Data` → Use `hugo.Data` instead.
- `.Site.BuildDrafts` → Deprecated. See https://discourse.gohugo.io/t/56732.
- `.Site.AllPages` → Deprecated. See https://discourse.gohugo.io/t/56732.
- `.Site.Languages` → Deprecated. See https://discourse.gohugo.io/t/56732.

#### Cascade target

- `cascade._target` → Use `cascade.target` instead. See https://gohugo.io/content-management/front-matter/#target.

---

## v0.158.0 Deprecations

#### Language configuration

- `languageCode` → Use `locale` instead.
- `languages.<lang>.languageCode` → Use `languages.<lang>.locale` instead.
- `languages.<lang>.languageName` → Use `languages.<lang>.label` instead.
- `languages.<lang>.languageDirection` → Use `languages.<lang>.direction` instead.

#### Language methods

- `.Site.LanguageCode` → Use `.Site.Language.Locale` instead.
- `.Language.LanguageCode` → Use `.Language.Locale` instead.
- `.Language.LanguageName` → Use `.Language.Label` instead.
- `.Language.LanguageDirection` → Use `.Language.Direction` instead.

---

## v0.161.0 Notes

#### Permalinks configuration

A new slice-based permalinks format is available, where each rule is a `{ target, pattern }` pair. The target is a `PageMatcher` (`kind`, `path` glob, `environment`, `sites.matrix`, ...), and the first matching rule wins. The legacy `[permalinks]` and `[permalinks.<kind>]` map-based formats still work.

Example (YAML):

```yaml
permalinks:
  - target:
      kind: page
      path: "/books/**"
    pattern: /books/:year/:slug/
  - target:
      kind: section
      path: "/{books,books/**}"
    pattern: /libros/:sections[1:]
  - target:
      kind: page
    pattern: /other/:slug/
```

---

## v0.163.0 Deprecations

#### Imaging configuration

- `imaging.quality` → Set the quality per format instead with `imaging.jpeg.quality`, `imaging.webp.quality` and/or `imaging.avif.quality`.
- `imaging.compression` → Set the compression type per format instead with `imaging.webp.compression` and/or `imaging.avif.compression`.
- `imaging.hint` → Set the hint per format instead with `imaging.webp.hint` and/or `imaging.avif.hint`.

#### Page methods

- `.Page.IsNode` → Use `.Page.IsBranch` or `not .Page.IsPage` instead.

---

## v0.164.0 Deprecations

#### Template functions

- `resources.PostProcess` → Use [`templates.Defer`](https://gohugo.io/functions/templates/defer/) instead.

---

## v0.165.0 Notes

#### Security configuration

The default `security.exec.allow` list no longer includes `tailwindcss` or the legacy Embedded Dart Sass binary names (`sass-embedded`, `dart-sass-embedded`). If the site uses `css.TailwindCSS`, add it back explicitly, e.g.:

```toml
[security.exec]
allow = ['^(dart-)?sass$', '^go$', '^git$', '^node$', '^postcss$', '^tailwindcss$']
```

Note that setting `security.exec.allow` replaces the default list, so keep the defaults the site needs.

---

## v0.166.0 Notes

#### Glob patterns

The glob library used for module mounts (`includeFiles`, `excludeFiles`), `cascade` targets, `segments`, `deployment` matchers and `noVendor` has been rewritten. Review these patterns:

- Malformed patterns (e.g. an unclosed `{`, an empty `[]` class) now fail with a syntax error.
- `**/x` requires the literal `/` and does not match `x`, and `a/**/b` does not match `a/b`. Use `{**/,}x` to match both.
- `\` is the escape character, so a literal backslash must be written as `\\`.

#### Templates

- `{{ return <value> }}` outside a partial is now an error. Remove it or move the logic into a partial.

#### Security configuration

- `text/org` content is now denied by default. If the site has Org mode content, add `text/org` to `security.allowContent`.
- `HTTP_PROXY`/`HTTPS_PROXY` are ignored for remote fetches unless `security.http.proxyFromEnvironment = true` is set.
- Mount roots in themes/modules that are symlinks (e.g. `themes/mytheme/assets -> /somewhere/else`) are dropped (symlinked mount roots in the main project are allowed again in v0.167.0). Replace them with a mount using an absolute `source` path.
- Node.js tools (PostCSS, Tailwind CSS) fail if a symlink in the project resolves outside the allowed roots. Add the link target to `security.node.permissions.allowRead`.

#### KaTeX

If the site uses `transform.ToMath` with `output` set to `html` or `htmlAndMathml`, update the KaTeX stylesheet to 0.18.4 or higher:

```diff
- <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.css">
+ <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.18.4/dist/katex.min.css">
```

#### URLs

A page without an explicit `slug` whose title contains a `/` (e.g. `Watch/listen to this`) now gets a single URL segment (`/watch-listen-to-this/`) instead of a nested one (`/watch/listen-to-this/`). To keep existing URLs, set `slug` or `url` in front matter, or add `aliases`.

---

## v0.167.0 Deprecations

#### Configuration

- `cleanDestinationDir` → Use `build.cleanDestinationDir.enable` instead. Note that `.git` files in the publish dir are now kept by default; use `build.cleanDestinationDir.keepFiles`/`keepDirs` to keep other files.

### v0.167.0 Notes

#### Configuration

- The default `baseURL` is now `https://example.org/` (it was empty). If the site relied on an empty `baseURL`, set it explicitly.

#### Templates

- `eq` now compares numbers by value, so `eq 1 1.0` is `true`. `in`, `intersect`, `union`, `uniq`, `symdiff`, `complement` and `where`'s `in`/`not in` also compare numbers exactly and no longer require the Go types to match.
- A table render hook in the project now takes precedence over the embedded one.

---

## v0.169.0 Deprecations

#### Page methods

Looking up reserved front matter fields via `.Params` is deprecated (also in `ByParam "title"`, `where .Pages "Params.title" ...` etc.). Fields set in the `params` section of front matter are not affected.

- `.Params.date` → Use `.Date` instead.
- `.Params.description` → Use `.Description` instead.
- `.Params.draft` → Use `.Draft` instead.
- `.Params.expirydate` → Use `.ExpiryDate` instead.
- `.Params.keywords` → Use `.Keywords` instead.
- `.Params.lastmod` → Use `.Lastmod` instead.
- `.Params.layout` → Use `.Layout` instead.
- `.Params.linktitle` → Use `.LinkTitle` instead.
- `.Params.publishdate` → Use `.PublishDate` instead.
- `.Params.slug` → Use `.Slug` instead.
- `.Params.summary` → Use `.RawSummary` instead.
- `.Params.title` → Use `.Title` instead.
- `.Params.translationkey` → Use `.TranslationKey` instead.
- `.Params.type` → Use `.Type` instead.
- `.Params.weight` → Use `.Weight` instead.

For `where` and sorting, use the method name, e.g. `where .Pages "Title" "foo"` instead of `where .Pages "Params.title" "foo"`.

### v0.169.0 Notes

#### Templates

- `emojify` and `plainify` now return a `string` unless the input is `template.HTML`. If the site relied on the result being treated as HTML with trusted input, pipe it through `safeHTML`.
- `pre` and `post` in menu entries defined in front matter are now HTML escaped unless `text/html` is in `security.allowContent`. Move menu entries that need HTML in `pre`/`post` to the site configuration.
