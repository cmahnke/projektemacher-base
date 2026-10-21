#!/usr/bin/env python3
"""Lint raw webmention store files and merge them for Hugo.

Reads the per-target JSON documents as written by the PHP endpoint
(services/webmentions/lib/store.php), drops broken material and merges
the valid entries into a single 'mentions.json' for the Hugo data
directory:

    {
      "mentions": {
        "https://example.org/blog/post/": [ { "source": ..., ... } ]
      }
    }

Dropped as broken:
- files that are no valid JSON or miss the 'target'/'mentions' fields
- entries missing required fields ('source', 'target', 'received')
- entries with malformed URLs or unparsable timestamps
- duplicates (same source, only the newest 'received' is kept)

Target keys are stored in several normalized forms (lowercase scheme
and host, trailing slash removed, plus a duplicated key with trailing
slash) so the theme's lookup partial can match page permalinks without
URL parsing.

Usage: lint.py <raw-dir> <output-file>
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

MAX_URL_LENGTH = 2000
MAX_TITLE = 300
MAX_CONTENT = 1000
MAX_AUTHOR_NAME = 200
MAX_AUTHOR_URL = 2000

VALID_TYPES = {"mention", "reply", "like", "repost", "bookmark", "pingback"}
REQUIRED_FIELDS = ("source", "received")


def normalize_target(url: str) -> str:
    """Lowercase scheme/host, drop fragment, default port and any
    trailing slash (except for the bare root) - mirrors the PHP store's
    wmNormalizeUrl()."""
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    host = parts.netloc.lower()
    for suffix in (":443", ":80"):
        if host.endswith(suffix) and (
            (scheme == "https" and suffix == ":443")
            or (scheme == "http" and suffix == ":80")
        ):
            host = host[: -len(suffix)]
    path = parts.path
    if path != "/" and path != "":
        path = path.rstrip("/") or "/"
    return f"{scheme}://{host}{path}{('?' + parts.query) if parts.query else ''}"


def target_keys(url: str) -> list:
    """All key variants under which a target should be findable."""
    normalized = normalize_target(url)
    keys = [normalized]
    if not normalized.endswith("/"):
        keys.append(normalized + "/")
    return keys


def clean_text(value, limit: int):
    """Plain, whitespace collapsed, hard capped string or None. Tags
    are stripped as defense-in-depth (the PHP collector already
    sanitizes, but stored data may come from anywhere)."""
    if not isinstance(value, str):
        return None
    text = re.sub(r"<[^>]*>", "", value)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit] if text else None


def clean_url(value):
    """http(s) URL string or None."""
    if not isinstance(value, str) or len(value) > MAX_URL_LENGTH:
        return None
    if not re.match(r"^https?://[^\s/$.?#].[^\s]*$", value, re.IGNORECASE):
        return None
    return value


def clean_timestamp(value):
    """ISO-8601 timestamp or None (also normalizes 'Z' suffix)."""
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def lint_entry(entry, expected_target):
    """Returns (clean_entry, None) or (None, reason).

    expected_target is the document's target (documents store one
    target each) or None for bare list documents, where every entry
    must carry its own target."""
    if not isinstance(entry, dict):
        return None, "not an object"
    for field in REQUIRED_FIELDS:
        if field not in entry:
            return None, f"missing field '{field}'"
    source = clean_url(entry.get("source"))
    if source is None:
        return None, "invalid source URL"
    # Entries may carry their own target (self contained, as written by
    # the PHP store); if present it must match the document's target,
    # otherwise the document's target applies.
    documented_target = clean_url(expected_target) if expected_target is not None else None
    entry_target = clean_url(entry.get("target"))
    if expected_target is not None:
        if documented_target is None:
            return None, "invalid target URL"
        if entry_target is not None and normalize_target(entry_target) != normalize_target(documented_target):
            return None, "invalid or mismatching target URL"
        target = documented_target
    elif entry_target is None:
        return None, "missing field 'target'"
    else:
        target = entry_target
    received = clean_timestamp(entry.get("received"))
    if received is None:
        return None, "invalid timestamp"

    clean = {
        "source": source,
        "target": target,
        "received": received,
        "type": entry.get("type") if entry.get("type") in VALID_TYPES else "mention",
    }
    title = clean_text(entry.get("title"), MAX_TITLE)
    if title:
        clean["title"] = title
    content = clean_text(entry.get("content"), MAX_CONTENT)
    if content:
        clean["content"] = content
    author = entry.get("author")
    if isinstance(author, dict):
        author_name = clean_text(author.get("name"), MAX_AUTHOR_NAME)
        author_url = clean_url(author.get("url"))
        if author_url is None:
            author_url = clean_text(author.get("url"), MAX_AUTHOR_URL)
        if author_name or author_url:
            clean_author = {}
            if author_name:
                clean_author["name"] = author_name
            if author_url:
                clean_author["url"] = author_url
            clean["author"] = clean_author
    return clean, None


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    raw_dir = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    if not raw_dir.is_dir():
        print(f"Error: raw directory '{raw_dir}' does not exist", file=sys.stderr)
        return 2

    files = entries_kept = entries_dropped = 0
    drop_reasons: dict = {}
    seen_sources: dict = {}

    for path in sorted(raw_dir.glob("*.json")):
        files += 1
        try:
            doc = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as error:
            print(f"Dropped {path.name}: unparsable JSON ({error})")
            entries_dropped += 1
            continue
        if isinstance(doc, list):
            # Bare list document: every entry must carry its own target.
            doc_target = None
            mentions = doc
        elif isinstance(doc, dict) and "target" in doc and clean_url(doc["target"]):
            doc_target = doc["target"]
            mentions = doc.get("mentions")
            mentions = mentions if isinstance(mentions, list) else []
        else:
            print(f"Dropped {path.name}: missing or invalid 'target'")
            entries_dropped += 1
            continue
        for entry in mentions:
            clean, reason = lint_entry(entry, doc_target)
            if clean is None:
                entries_dropped += 1
                drop_reasons[reason] = drop_reasons.get(reason, 0) + 1
                continue
            # Deduplicate by source within the normalized target, the
            # newest 'received' wins.
            group_key = normalize_target(clean["target"])
            previous = seen_sources.get(group_key, {}).get(clean["source"])
            if previous and previous["received"] >= clean["received"]:
                entries_dropped += 1
                drop_reasons["duplicate source (older)"] = (
                    drop_reasons.get("duplicate source (older)", 0) + 1
                )
                continue
            seen_sources.setdefault(group_key, {})[clean["source"]] = clean
            entries_kept += 1

    # Re-sort every group by received date.
    mentions_by_key: dict = {}
    for group_key, sources in seen_sources.items():
        entries = sorted(sources.values(), key=lambda entry: entry["received"])
        for key in target_keys(group_key):
            mentions_by_key[key] = entries

    # No run timestamp: the output must stay byte-identical across
    # harvests without mention changes (the harvest workflow commits
    # only on real changes), freshness lives in the git history.
    document = {"mentions": dict(sorted(mentions_by_key.items()))}
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(document, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    print(
        f"Linted {files} raw file(s): "
        f"{entries_kept} entr{'y' if entries_kept == 1 else 'ies'} kept, "
        f"{entries_dropped} dropped, {len(seen_sources)} target(s)"
    )
    for reason, count in sorted(drop_reasons.items()):
        print(f"  {count}x {reason}")
    print(f"Wrote {output_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
