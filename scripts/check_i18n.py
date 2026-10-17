#!/usr/bin/env python3
"""Check the theme's i18n files for missing translations.

Groups all TOML files in an i18n directory by language (the last
dot separated part of the file name, e.g. 'de.toml' and 'tags.de.toml'
both belong to 'de'), merges the keys per language and compares them
against the union of keys of all languages. Exits non zero and lists
the missing keys if a language is incomplete.

This mirrors the grouping of the example site's 'i18n-strings' shortcode
(exampleSite/layouts/shortcodes/i18n-strings.html) and works with both
merged files and unmerged fragments.

Usage: check_i18n.py [LANG_DIR]
"""

import sys
import tomllib
from pathlib import Path

EXIT_OK = 0
EXIT_MISSING = 1
EXIT_ERROR = 2


def language_of(stem: str) -> str:
    return stem.split(".")[-1]


def collect(lang_dir: Path) -> dict[str, set[str]]:
    languages: dict[str, set[str]] = {}
    files = sorted(lang_dir.glob("*.toml"))
    if not files:
        raise RuntimeError(f"No TOML files found in '{lang_dir}'")
    for file in files:
        lang = language_of(file.stem)
        data = tomllib.loads(file.read_text(encoding="utf-8"))
        languages.setdefault(lang, set()).update(data.keys())
    return languages


def main() -> int:
    lang_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "i18n")
    if not lang_dir.is_dir():
        print(f"ERROR: '{lang_dir}' is not a directory", file=sys.stderr)
        return EXIT_ERROR

    try:
        languages = collect(lang_dir)
    except (RuntimeError, tomllib.TOMLDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return EXIT_ERROR

    union: set[str] = set()
    for keys in languages.values():
        union |= keys

    ok = True
    for lang in sorted(languages):
        keys = languages[lang]
        missing = sorted(union - keys)
        print(f"{lang}: {len(keys)} keys, missing {len(missing)}")
        if missing:
            ok = False
            shown = ", ".join(missing[:10])
            suffix = " …" if len(missing) > 10 else ""
            print(f"  missing: {shown}{suffix}")

    if not ok:
        print("MISSING TRANSLATIONS: add the keys above to every language file", file=sys.stderr)
        return EXIT_MISSING
    print("OK: all languages define the same keys")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
