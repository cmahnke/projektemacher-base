# PyHugo

Python library to parse Hugo sites: configuration, content bundles and their
front matter. It is the single site parser used by this repository's scripts
(`preview.py`, `post-calendar.py`, `pdf.py`).

## Installation

The library lives in `scripts/PyHugo` and is used in place — add the
repository's `scripts/` directory to `sys.path` and import it:

```python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
from PyHugo import Config, Content, Post
```

Its dependencies (`python-frontmatter`, `toml`, `pyyaml`, `termcolor`,
`requests`) are part of the repository's `requirements.txt`.

## Configuration discovery

`Config` and `Site` locate a Hugo site automatically: starting from the given
directory they walk up the file system until a `config.toml`, `hugo.toml`,
`config/_default/config.toml` or `config/_default/hugo.toml` is found.

The configuration of `config/_default/*.toml` is merged over the root
configuration (dict values like `[params]` are merged recursively), matching
Hugo's behaviour.

## API

### `Config`

Loads the site configuration and translations.

```python
from PyHugo import Config

config = Config(".")                 # walks up from the current directory
config.baseURL()                     # 'https://example.org/'
config.publishDir()                  # 'public' or the configured value
config.langs                         # ['en', 'de'] (from [languages])
config.defaultLanguage               # from defaultContentLanguage
config.config                        # the merged configuration dict
config.translate("key", "en")        # i18n translation (theme + site i18n dirs)
config.getAuthors()                  # params.author(s) as a list
```

### `Site`

Base class of `Config`, used to resolve the site structure:

```python
from PyHugo import Site

site = Site("./")
site.contentDir()                    # absolute path of the content directory
site.translations                    # loaded i18n translations
```

### `Post`

A content bundle (a directory holding `index.md` / `_index.md` with optional
language suffixes like `index.de.md`). Posts can be loaded from a directory
(all language variants), from a language/file dict or from a single file:

```python
from pathlib import Path
from PyHugo import Post

post = Post(Path("content/post/42"), config=config)   # all variants
post = Post("content/post/42/index.de.md")            # single file
post = Post({None: "content/post/42/index.md", "de": "content/post/42/index.de.md"})

post.files                            # {lang: file path}
post.getMetadata("de")                # front matter dict
post.getContent("de")                 # markdown body
post.getParam("preview", "de")        # front matter key (root or params section)
post.getDraft("de")
post.getResources("de")               # page resources from the front matter
post.getResourcesByType("image", "de")
post.getTags("de")                    # {tag: Tag}
post.getWikidata("de")                # wikidata ids referenced by the page
post.getKeywords("de")                # tags (translated) + wikidata labels + keywords
post.addMetadata("key", "value", "de")  # writes the front matter back to disk
post.getURL()                         # absolute URL (needs a config, None for drafts)
```

Language fallback: passing a language that isn't loaded falls back to the
unsuffixed file (`None`), so `post.getMetadata("fr")` still works on a site
without French content.

### `Content`

Walks a content directory and collects all posts (sections included):

```python
from PyHugo import Content

content = Content(config.contentDir(), config=config)
for post in content.posts:            # full list, sections included
    print(post, post.getMetadata().get("title"))
```

Note: the iterator (`for post in content`) skips section pages for backwards
compatibility — iterate `content.posts` when sections are needed.

### `Published`

Lists the URLs of the built site (a relative `publishDir` is resolved against
the site's base directory):

```python
from PyHugo import Published

published = Published(config)
published.postList()                  # ['https://example.org/post/42/', ...]
```

### `Util` (`Wikidata`, `ArchiveOrg`)

Network helpers, used by `Post.getKeywords()`. All calls fail gracefully
(return `None`) when the API is unreachable:

```python
from PyHugo.Util import Wikidata, ArchiveOrg

Wikidata.getLabel("Q42", "en")
ArchiveOrg.latest("https://example.org/")
```

## Testing

```bash
python3 scripts/PyHugo/test-pyhugo.py -b exampleSite/
```

Runs a smoke test (configuration, content walk, tags, keywords, published URLs
and front matter write back on a temporary copy) against the example site.
This test is part of the `test_PyHugo` GitHub Actions job.

## Known limitations

* Theme `[params]` from the theme's own `config/` directory are not loaded
* Output format handling (`getOutputs()`) only collects the configured output
  names, it doesn't resolve output file names
* Only TOML/YAML front matter via `python-frontmatter`, no TOML (`+++`)
  fences have been tested
