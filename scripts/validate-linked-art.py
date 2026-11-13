#!/usr/bin/env python3

"""Validates single object Linked Art JSON-LD documents against the official JSON schemas.

https://github.com/linked-art/json-validator

Collections (type 'Set') are skipped, as the API schemas don't cover them.

Usage: validate-linked-art.py [DIRECTORY]

The schema source can be configured using the LA_SCHEMA_BASE environment
variable or the --schema-base flag, by default the schemas are pulled from
the linked.art repository on GitHub. A specific revision can be pinned by
using the raw URL of a commit or tag as base, e.g.
https://raw.githubusercontent.com/linked-art/linked.art/<COMMIT>/docs/api/1.0/schema/

Environment variables:
  LA_SCHEMA_BASE  Base URL of the schemas, defaults to
                  https://raw.githubusercontent.com/linked-art/linked.art/master/docs/api/1.0/schema/
  LA_SCHEMA_CACHE Optional directory used to cache the downloaded schemas
"""

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

import jsonschema
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

# Base URL used by the $id and the relative $refs inside the schemas
CANONICAL_BASE = "https://linked.art/api/1.0/schema/"
# Default source of the schemas, can be overridden
DEFAULT_SCHEMA_BASE = "https://raw.githubusercontent.com/linked-art/linked.art/master/docs/api/1.0/schema/"
SCHEMA_BASE_DEFAULT = os.environ.get("LA_SCHEMA_BASE", DEFAULT_SCHEMA_BASE)
DEFAULT_CACHE = os.environ.get("LA_SCHEMA_CACHE")

# Mapping of Linked Art classes to the schema files of the API
SCHEMA_MAP = {
    "HumanMadeObject": "object.json",
    "DigitalObject": "digital.json",
    "Person": "person.json",
    "Group": "group.json",
    "Place": "place.json",
    "VisualItem": "image.json",
    "LinguisticObject": "text.json",
    "PropositionalObject": "abstract.json",
    "Type": "concept.json",
    "Event": "event.json",
    "Activity": "provenance.json",
    "Period": "event.json",
}


def urlopen(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": "projektemacher-validate-linked-art"})
    return urllib.request.urlopen(request, timeout=60)


def map_uri(uri: str, schema_base: str) -> str:
    """Resolves URIs of the canonical schema location against the configured base"""
    if uri.startswith(CANONICAL_BASE):
        return schema_base + uri[len(CANONICAL_BASE):]
    return uri


def cache_key(uri: str, schema_base: str) -> str:
    """File name used to store the schema in the cache directory"""
    for base in (schema_base, CANONICAL_BASE):
        if uri.startswith(base):
            return uri[len(base):].replace("/", "_")
    return uri.replace("/", "_")


def load_schema(uri: str, schema_base: str, cache_dir: Path | None):
    uri = map_uri(uri, schema_base)
    if cache_dir is not None:
        cached = cache_dir / cache_key(uri, schema_base)
        if cached.is_file():
            return json.loads(cached.read_text())
    schema = json.load(urlopen(uri))
    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / cache_key(uri, schema_base)).write_text(json.dumps(schema))
    return schema


def validate_file(path: Path, schema_base: str, validator_cache: dict, registry: Registry, cache_dir: Path | None, failures: list, warnings: list) -> tuple[bool, int]:
    """Validates a single file, returns a tuple of (validated, errors)"""
    try:
        document = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        failures.append(f"{path}: invalid JSON: {error}")
        return (True, 1)

    context = document.get("@context")
    if not (isinstance(context, str) and context.startswith("https://linked.art/ns/v1/")):
        warnings.append(f"{path}: no Linked Art context found, skipping")
        return (False, 0)

    doc_type = document.get("type")
    if doc_type == "Set":
        # Sets are collections, the API schemas don't support them
        warnings.append(f"{path}: Set collection, skipping")
        return (False, 0)
    schema_name = SCHEMA_MAP.get(doc_type)
    if schema_name is None:
        warnings.append(f"{path}: unknown Linked Art type '{doc_type}', skipping")
        return (False, 0)

    schema_uri = f"{CANONICAL_BASE}{schema_name}"
    if schema_uri not in validator_cache:
        validator_cache[schema_uri] = jsonschema.Draft202012Validator(load_schema(schema_uri, schema_base, cache_dir), registry=registry)
    validator = validator_cache[schema_uri]

    errors = 0
    for error in sorted(validator.iter_errors(document), key=lambda e: list(e.absolute_path)):
        location = "/".join(str(part) for part in error.absolute_path) or "<root>"
        failures.append(f"{path}: {location}: {error.message}")
        errors += 1
    return (True, errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validates Linked Art JSON-LD against the official JSON schemas")
    parser.add_argument("directory", nargs="?", default="docs", help="Directory to search for JSON files (default: docs)")
    parser.add_argument("--schema-base", default=SCHEMA_BASE_DEFAULT, help="Base URL of the Linked Art schemas")
    parser.add_argument("--cache", default=DEFAULT_CACHE, help="Directory to cache downloaded schemas")
    parser.add_argument("--name", default="linkedart.json", help="File name to look for (default: linkedart.json)")
    args = parser.parse_args()

    schema_base = args.schema_base if args.schema_base.endswith("/") else args.schema_base + "/"

    directory = Path(args.directory)
    if not directory.is_dir():
        print(f"Directory '{directory}' not found", file=sys.stderr)
        return 1

    cache_dir = Path(args.cache) if args.cache else None
    retrieved: dict[str, Resource] = {}

    def retrieve(uri: str) -> Resource:
        if uri not in retrieved:
            retrieved[uri] = Resource.from_contents(load_schema(uri, schema_base, cache_dir), default_specification=DRAFT202012)
        return retrieved[uri]

    registry = Registry(retrieve=retrieve)
    validator_cache: dict[str, jsonschema.Draft202012Validator] = {}

    checked = 0
    skipped = 0
    failures: list[str] = []
    warnings: list[str] = []

    for path in sorted(directory.rglob(args.name)):
        validated, _errors = validate_file(path, schema_base, validator_cache, registry, cache_dir, failures, warnings)
        if validated:
            checked += 1
        else:
            skipped += 1

    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    for failure in failures:
        print(failure, file=sys.stderr)

    print(f"Checked {checked} Linked Art document(s), skipped {skipped}, {len(failures)} error(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
