#!/usr/bin/env bash

set -e -o pipefail

# Validates IIIF Presentation manifests and collections using the official validator
# https://github.com/IIIF/presentation-validator
#
# Usage: validate-iiif.sh [DIRECTORY]
#
# Manifests and collections are detected by their @context, the version is
# passed on to the validator, supported are 2.0, 2.1, 3.0 and 4.0 (draft).
#
# Environment variables:
#   IIIF_VALIDATOR  Command to use, defaults to 'iiif-validator'
#   IIIF_VERSIONS   Whitespace separated list of versions to validate,
#                   defaults to '2.0 2.1 3.0 4.0'

DIRECTORY=${1:-docs}
IIIF_VALIDATOR=${IIIF_VALIDATOR:-iiif-validator}
IIIF_VERSIONS=${IIIF_VERSIONS:-"2.0 2.1 3.0 4.0"}

if ! command -v "$IIIF_VALIDATOR" > /dev/null ; then
  echo "'$IIIF_VALIDATOR' not found, install it using 'pip install git+https://github.com/IIIF/presentation-validator'" >&2
  exit 1
fi

if [ ! -d "$DIRECTORY" ] ; then
  echo "Directory '$DIRECTORY' not found" >&2
  exit 1
fi

FAILURES=0
CHECKED=0
SKIPPED=0

validate() {
  local FILE=$1
  local VERSION=$2
  echo "Validating $FILE (Presentation API $VERSION)"
  CHECKED=$((CHECKED + 1))
  local RESULT
  # The validator always exits with 0, the result needs to be read from the JSON output
  if ! RESULT=$("$IIIF_VALIDATOR" validate --version "$VERSION" "$FILE") ; then
    echo "Validation of $FILE failed:" >&2
    echo "$RESULT" >&2
    FAILURES=$((FAILURES + 1))
    return
  fi
  local OKAY
  OKAY=$(printf '%s' "$RESULT" | python3 -c "
import json, sys
try:
    print(json.load(sys.stdin).get('okay', 0))
except Exception:
    print(0)")
  if [ "$OKAY" != "1" ] ; then
    echo "Validation of $FILE failed:" >&2
    echo "$RESULT" >&2
    FAILURES=$((FAILURES + 1))
  fi
}

# Contexts of the IIIF Presentation API versions
# https://iiif.io/api/presentation/2.1/#array-of-contexts
# https://iiif.io/api/presentation/3.0/#5-manifest
# https://iiif.io/api/presentation/4.0/
while IFS= read -r FILE ; do
  CONTEXT=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); c=d.get('@context', d.get('context','')); print(' '.join(c) if isinstance(c, list) else c)" "$FILE") || {
    echo "Skipping $FILE: could not parse JSON" >&2
    FAILURES=$((FAILURES + 1))
    continue
  }
  case "$CONTEXT" in
    *iiif.io/api/presentation/2.1/context.json*)
      VERSION=2.1
      ;;
    *iiif.io/api/presentation/2/context.json*)
      VERSION=2.0
      ;;
    *iiif.io/api/presentation/3/context.json*)
      VERSION=3.0
      ;;
    *iiif.io/api/presentation/4/context.json*)
      VERSION=4.0
      ;;
    *)
      echo "Skipping $FILE: no IIIF Presentation context found ('$CONTEXT')" >&2
      SKIPPED=$((SKIPPED + 1))
      continue
      ;;
  esac
  if [[ " $IIIF_VERSIONS " == *" $VERSION "* ]] ; then
    validate "$FILE" "$VERSION"
  else
    echo "Skipping $FILE: version $VERSION not in IIIF_VERSIONS ($IIIF_VERSIONS)" >&2
    SKIPPED=$((SKIPPED + 1))
  fi
done < <(find "$DIRECTORY" \( -name 'manifest.json' -o -name 'collection.json' \) -type f)

echo "Checked $CHECKED file(s), skipped $SKIPPED file(s), $FAILURES failure(s)"

if [ "$FAILURES" -gt 0 ] ; then
  exit 1
fi
