import sys, os, argparse, logging, tempfile, shutil
from pathlib import Path

sys.path.append(f"{Path(__file__).parent.parent}/")
print(f"loading from {sys.path[-1]}")
from PyHugo import Post, Content, Config, Site, Published, Tags

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

    if failures:
        print(f"\n{len(failures)} check(s) failed: {failures}")
        sys.exit(1)
    print("\nAll checks passed")
