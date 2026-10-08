#!/usr/bin/env bash
#
# Convert all flat *.tif / *.tiff files in a given directory to JXL.
# Usage: convertDirToJXL.sh <input-dir>
# Output: <input-dir>/jxl/<name>.jxl (skips files that already exist)
# Based on convertScantailorOutToJXL.sh (JXL part only).

set -u

JOBS=1

MAGICK=magick
EXIF=exiftool

if [ $# -lt 1 ]; then
  echo "Usage: $0 <input-dir>" >&2
  exit 1
fi

# Strip trailing slash(es), keep "/" itself intact.
INPUT_DIR="$1"
while [ "${INPUT_DIR%/}" != "$INPUT_DIR" ] && [ "$INPUT_DIR" != "/" ]; do
  INPUT_DIR="${INPUT_DIR%/}"
done

if [ ! -d "$INPUT_DIR" ]; then
  echo "Error: '$1' is not a directory" >&2
  exit 1
fi

DIR="$INPUT_DIR"
JOBFILE="$DIR/vips-jobs"

if ! command -v "$EXIF" >/dev/null 2>&1; then
  echo "exiftool not found, install it and make sure it's in PATH" >&2
  exit 1
fi

if ! command -v "$MAGICK" >/dev/null 2>&1; then
  MAGICK=convert
fi
if ! command -v "$MAGICK" >/dev/null 2>&1; then
  echo "neither 'magick' nor 'convert' found, install ImageMagick" >&2
  exit 1
fi
# Legacy fallback: imagemagick-full install (takes precedence if present).
for _c in /opt/homebrew/Cellar/imagemagick-full/*/bin/convert; do
  if [ -x "$_c" ]; then
    MAGICK="$_c"
    break
  fi
done

IMAGES=$(find "$DIR" -maxdepth 1 -type f \( -iname '*.tif' -o -iname '*.tiff' \) | LC_ALL=C sort)

if [ -z "$IMAGES" ]; then
  echo "No *.tif / *.tiff files found in '$DIR'"
  exit 0
fi

mkdir -p "$DIR/jxl/"

>"$JOBFILE"

COUNT=0
QUEUED=0
IFS=$'\n'
for IMAGE in $IMAGES; do
  COUNT=$((COUNT + 1))
  BASE=$(basename "$IMAGE")
  FILENAME="${BASE%.*}"
  echo "Processing '$IMAGE' in '$DIR'"
  if [ ! -f "$DIR/jxl/$FILENAME.jxl" ]; then
    PPIX=$($EXIF -XResolution -S -n "$IMAGE" | cut -d ' ' -f 2)
    PPIY=$($EXIF -YResolution -S -n "$IMAGE" | cut -d ' ' -f 2)

    # xargs parses quotes: the whole command must be ONE single-quoted string,
    # otherwise it is split into words and 'sh -c' receives fragments.
    CMD="'$MAGICK \"$IMAGE\" -define jxl:distance=0.6 -define jxl:brotli_effort=11 -define jxl:effort=9 \"$DIR/jxl/$FILENAME.jxl\" && $EXIF -m \"$DIR/jxl/$FILENAME.jxl\" -resolutionunit=inches -XResolution=$PPIX -YResolution=$PPIY'"
    echo "$CMD" >> "$JOBFILE"
    QUEUED=$((QUEUED + 1))

    echo "Added generation of $DIR/jxl/$FILENAME.jxl to queue"
  fi
done
unset IFS

if [ "$QUEUED" -gt 0 ]; then
  echo "Running JXL processing with $JOBS jobs, this may take a while"
  # shellcheck disable=SC2013
  cat "$JOBFILE" | xargs -P "$JOBS" -n 1 sh -c
  echo "If this fails due to being too large you need to convert to PNG first with magick and use cjxl from there, don't forget to update the metadata"
else
  echo "Nothing to do, all JXL files already exist"
fi
echo "Number of images: $COUNT (queued: $QUEUED)"

echo "Removing backup files"
find "$DIR/jxl" -maxdepth 1 -name '*.jxl_original' -delete
