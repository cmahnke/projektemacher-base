import sys, os, argparse, logging, tempfile, shutil, contextlib
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}/")
print(f"loading from {sys.path[-1]}")
from PyHugo import Post, Content, Config, Site, Published, Tags, PyHugo
from PyHugo.content import WARNED_CONFIG_DIRS

hugo_dir = "../../../../"
hugo_config = os.path.abspath(os.path.join(os.path.dirname(__file__), hugo_dir))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--basedir", "-b", default=hugo_dir, help="Base directory")
    args = parser.parse_args()

    print(f"Using base directory: {args.basedir}")
    logging.basicConfig(level=logging.WARNING)

    failures = []

    def check(name, condition):
        status = "ok" if condition else "FAILED"
        print(f"  [{status}] {name}")
        if not condition:
            failures.append(name)

    # Config
    print("Config:")
    c = Config(args.basedir)
    check("baseURL is loaded", c.baseURL().startswith("http"))
    check("publishDir is loaded", c.publishDir() == "docs")
    check("defaultContentLanguage is loaded", c.defaultLanguage in (None, "en"))
    check("title is loaded", c.config.get("title") is not None and len(c.config.get("title")) > 0)
    check("i18n translations have the expected structure", isinstance(c.translations, dict))
    check("no language keys pollute translations", "en" not in c.translations or not isinstance(c.translations.get("en"), dict) or "en" not in c.translations)

    # Content walk
    print("Content:")
    content = Content(c.contentDir(), config=c)
    check("posts were found", len(content.posts) > 0)
    titles = [post.getMetadata().get("title") for post in content.posts]
    check("posts have titles", any(title for title in titles))
    check("draft status is available", all(post.draft in (True, False) for post in content.posts))
    print(f"  Found {len(content.posts)} posts: {titles}")

    # Params and metadata access
    any_post = next(post for post in content.posts if not post.section)
    check("getParam returns None for unknown keys", any_post.getParam("does-not-exist") is None)
    check("getMetadata is available", isinstance(any_post.getMetadata(), dict))
    check("getWikidata returns a list", isinstance(any_post.getWikidata(), list))

    # Tags and keywords (network access is optional, the API calls fail gracefully)
    print("Tags and keywords:")
    tagged_posts = [post for post in content.posts if len(post.getTags()) > 0]
    print(f"  Found {len(tagged_posts)} posts with tags")
    check("tagged posts are found", len(tagged_posts) > 0)
    tags = tagged_posts[0].getTags()
    print(f"  Found tags: {list(tags.keys())}")
    for tag_obj in tags.values():
        check("tag objects are loadable", isinstance(tag_obj.getWikidata(), list))
    keywords = tagged_posts[0].getKeywords()
    check("keywords are generated", isinstance(keywords, list))

    # Tag pages from the example site
    print("Tag pages:")
    content_dir = c.contentDir()
    tags_dir = Path(content_dir).joinpath("tags")
    if tags_dir.exists():
        tag_dirs = [d for d in tags_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
        if tag_dirs:
            tag_post = Post(tag_dirs[0], config=c)
            check("tag page is loadable", True)
        else:
            print("  (skipped, no tag page directories)")

    # Published (output URL list)
    print("Published:")
    if os.path.isdir(os.path.join(args.basedir, c.publishDir())):
        published = Published(c)
        urls = published.postList()
        check("published URLs are listed", len(urls) > 0)
        check("URLs are absolute", all(url.startswith("http") for url in urls))
    else:
        print("  (skipped, no publish directory found)")

    # Front matter write back (on a temporary copy to avoid modifying the example site)
    print("Front matter write back:")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_content = Path(tmp, "content")
        shutil.copytree(c.contentDir(), tmp_content)
        shutil.copy(Path(args.basedir, "hugo.toml"), tmp)
        tmp_config = Config(tmp)
        tmp_content_obj = Content(tmp_config.contentDir(), config=tmp_config)
        tmp_post = next(post for post in tmp_content_obj.posts if not post.section)
        tmp_post.addMetadata("testKey", "testValue")
        reloaded = Post(tmp_post.files[None], config=tmp_config)
        check("added metadata survives a reload", reloaded.getMetadata().get("testKey") == "testValue")

    # Configuration directory handling (config/_default plus environment directories)
    print("Config directory:")

    class WarningCapture(logging.Handler):
        def __init__(self):
            super().__init__()
            self.messages = []

        def emit(self, record):
            self.messages.append(record.getMessage())

    @contextlib.contextmanager
    def capturedConfigWarnings():
        capture = WarningCapture()
        logger = logging.getLogger("PyHugo.content")
        logger.addHandler(capture)
        propagate = logger.propagate
        logger.propagate = False
        try:
            yield capture.messages
        finally:
            logger.removeHandler(capture)
            logger.propagate = propagate

    def writeConfigDirSite(tmp, with_root=True):
        tmp = Path(tmp)
        if with_root:
            (tmp / "hugo.toml").write_text(
                'baseURL = "https://example.org/"\npublishDir = "docs"\ntitle = "Root"\n\n[params]\n  author = "root"\n'
            )
        (tmp / "config" / "_default" / "navigation").mkdir(parents=True)
        (tmp / "config" / "_default" / "config.toml").write_text(
            'title = "Default"\n\n[params]\n  author = "default"\n  tagline = "from default"\n'
        )
        (tmp / "config" / "_default" / "params.toml").write_text('foo = "bar"\n')
        (tmp / "config" / "_default" / "params.en.toml").write_text('subtitle = "English subtitle"\n')
        (tmp / "config" / "_default" / "sitemap.toml").write_text('[sitemap]\n  changefreq = "monthly"\n')
        (tmp / "config" / "_default" / "navigation" / "menus.toml").write_text('[[main]]\n  name = "Home"\n')
        (tmp / "config" / "development").mkdir()
        (tmp / "config" / "development" / "env.toml").write_text('devOnly = true\n')
        (tmp / "config" / "production").mkdir()
        (tmp / "config" / "production" / "prod.toml").write_text('prodOnly = true\n')
        return tmp

    WARNED_CONFIG_DIRS.clear()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = writeConfigDirSite(tmp)

        with capturedConfigWarnings() as warnings:
            site = Site(tmp)
        check("unread config directory triggers a warning", len(warnings) == 1)
        if warnings:
            check(
                "warning lists all unread files",
                "config/_default/config.toml" in warnings[0] and "config/development/env.toml" in warnings[0],
            )
        check("the root config file is loaded", site.config.get("title") == "Root")
        check("the config directory is not read by default", site.config.get("params", {}).get("tagline") is None)

        with capturedConfigWarnings() as warnings:
            Site(tmp)
        check("the warning is deduplicated", len(warnings) == 0)

        with capturedConfigWarnings() as warnings:
            merged = Site(tmp, load_config_dir=True)
        check("no warning when the config directory is loaded", len(warnings) == 0)
        check("config directory values override the root file", merged.config.get("title") == "Default")
        check(
            "params are deep merged",
            merged.config.get("params", {}).get("author") == "default"
            and merged.config.get("params", {}).get("tagline") == "from default",
        )
        check("unwrapped category files are supported", merged.config.get("params", {}).get("foo") == "bar")
        check(
            "wrapped category files are unwrapped",
            merged.config.get("sitemap", {}).get("changefreq") == "monthly",
        )
        check("files in subdirectories are read", isinstance(merged.config.get("menus", {}).get("main"), list))
        check(
            "language specific files are supported",
            merged.config.get("languages", {}).get("en", {}).get("params", {}).get("subtitle") == "English subtitle",
        )
        check(
            "all environments are merged by default",
            merged.config.get("env", {}).get("devOnly") is True and merged.config.get("prod", {}).get("prodOnly") is True,
        )

        dev = Site(tmp, load_config_dir="development")
        check("the given environment is merged", dev.config.get("env", {}).get("devOnly") is True)
        check("other environments are not merged", dev.config.get("prod", {}).get("prodOnly") is None)

        with capturedConfigWarnings() as warnings:
            config = Config(tmp)
        check("Config reads the config directory without warning", len(warnings) == 0)
        check(
            "Config sees config directory values",
            config.config.get("title") == "Default" and config.publishDir() == "docs",
        )

        wrapper = PyHugo(str(tmp))
        check("PyHugo wrapper merges the config directory", wrapper.getSite().config.get("params", {}).get("tagline") == "from default")

    # A site whose configuration lives only inside the config directory
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "config" / "_default").mkdir(parents=True)
        (tmp / "config" / "_default" / "config.toml").write_text('[params]\n  tagline = "from default"\n')
        with capturedConfigWarnings() as warnings:
            dirOnly = Site(tmp)
        check("no warning when the primary file lives in the config directory", len(warnings) == 0)
        check("config directory only sites are loadable", dirOnly.config.get("params", {}).get("tagline") == "from default")

    if failures:
        print(f"\n{len(failures)} check(s) failed: {failures}")
        sys.exit(1)
    print("\nAll checks passed")
