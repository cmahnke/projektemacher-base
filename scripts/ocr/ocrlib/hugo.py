import logging
from pathlib import Path

from ocrlib import imageio

logger = logging.getLogger(__name__)


def collect_content_images(site_root, content_dir, include_ext=None, logger_name=__name__):
    """Find OCR-able images in a Hugo content tree via PyHugo.

    Walks page bundles (the directory containing each post's markdown file),
    skipping drafts. Returns a list of (label, [image paths]) where label is
    the post's relative path for logging.
    """
    from PyHugo import PyHugo

    include_ext = include_ext or set(imageio.IMAGE_EXTENSIONS)
    site = Path(site_root).resolve()
    ph = PyHugo(str(site))
    content = ph.getContent()
    if content_dir is not None:
        from PyHugo.content import Content

        content = Content(str(Path(content_dir).resolve()), config=ph.getConfig())
    results = []
    seen_dirs = set()
    for post in content:
        if post.draft:
            logger.debug(f"Skipping draft {post.path}")
            continue
        if post.path in seen_dirs:
            continue
        seen_dirs.add(post.path)
        images = sorted(
            [f for f in Path(post.path).rglob("*") if f.is_file() and f.suffix.lower() in include_ext],
            key=lambda f: str(f),
        )
        if images:
            try:
                rel = str(Path(post.path).relative_to(site))
            except ValueError:
                rel = str(post.path)
            results.append((rel, images))
    return results


def collect_input_images(paths, include_ext=None):
    """Plain recursive image discovery for explicitly given files or directories."""
    include_ext = include_ext or set(imageio.IMAGE_EXTENSIONS)
    results = []
    for path in paths:
        path = Path(path)
        if path.is_file() and path.suffix.lower() in include_ext:
            results.append((str(path.parent), [path]))
        elif path.is_dir():
            images = sorted(
                [f for f in path.rglob("*") if f.is_file() and f.suffix.lower() in include_ext and not f.name.startswith(".")]
            )
            if images:
                results.append((str(path), images))
        else:
            logger.warning(f"Input path '{path}' does not exist, skipping")
    return results
