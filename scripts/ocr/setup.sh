#!/usr/bin/env bash

set -e -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON_VERSION="${OCR_PYTHON_VERSION:-3.12.4}"
QUANT="${OCR_QUANT:-bf16}"
GGUF_REPO="ggml-org/HunyuanOCR-GGUF"
MODELS_DIR="$SCRIPT_DIR/models/hunyuanocr"

SKIP_LLAMA_CHECK=0
SKIP_MODELS=0
while [ $# -gt 0 ]; do
  case "$1" in
    --quant)
      QUANT="$2"
      shift 2
      ;;
    --skip-llama-check)
      SKIP_LLAMA_CHECK=1
      shift
      ;;
    --skip-models)
      SKIP_MODELS=1
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Usage: $0 [--quant bf16|q8_0] [--skip-llama-check] [--skip-models]" >&2
      exit 1
      ;;
  esac
done

if ! command -v pyenv >/dev/null 2>&1; then
  echo "pyenv not found"
  if command -v brew >/dev/null 2>&1; then
    echo "Installing pyenv via brew"
    brew install pyenv
  else
    echo "Install pyenv manually, see https://github.com/pyenv/pyenv#installation" >&2
    exit 1
  fi
fi

PYENV_ROOT="${PYENV_ROOT:-$HOME/.pyenv}"
if [ ! -x "$PYENV_ROOT/versions/$PYTHON_VERSION/bin/python" ]; then
  echo "Installing Python $PYTHON_VERSION via pyenv"
  pyenv install -s "$PYTHON_VERSION"
fi

if [ ! -x "$SCRIPT_DIR/.venv/bin/python" ]; then
  echo "Creating virtual environment in '$SCRIPT_DIR/.venv'"
  "$PYENV_ROOT/versions/$PYTHON_VERSION/bin/python" -m venv "$SCRIPT_DIR/.venv"
fi

echo "Installing Python dependencies"
"$SCRIPT_DIR/.venv/bin/pip" install --upgrade pip wheel
"$SCRIPT_DIR/.venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

if ! command -v vips >/dev/null 2>&1; then
  echo "libvips not found, install it and make sure 'vips' is in PATH" >&2
  echo "  macOS: brew install libvips" >&2
  echo "  Debian/Ubuntu: apt-get install libvips-dev" >&2
  exit 1
fi
VIPS_LOADERS="$(vips -l 2>&1 || true)"
if ! printf '%s\n' "$VIPS_LOADERS" | grep -qi jxl; then
  echo "libvips is missing JPEG XL (jxl) support, rebuild it with libjxl" >&2
  exit 1
fi

if [ "$SKIP_LLAMA_CHECK" -eq 0 ]; then
  if ! command -v llama-server >/dev/null 2>&1; then
    echo "llama-server not found" >&2
    echo "  macOS: brew install llama.cpp" >&2
    echo "  or build from source, see https://github.com/ggml-org/llama.cpp" >&2
    exit 1
  fi
  LLAMA_BUILD="$(llama-server --version 2>/dev/null | sed -n 's/.*\bb\([0-9][0-9]*\)\b.*/\1/p' | head -n 1)"
  if [ -n "$LLAMA_BUILD" ] && [ "$LLAMA_BUILD" -lt 11103 ]; then
    echo "Warning: llama.cpp build b$LLAMA_BUILD is older than b11103, update for HunyuanOCR improvements" >&2
  fi
fi

if [ "$SKIP_MODELS" -eq 0 ]; then
  mkdir -p "$MODELS_DIR"
  for FILE in "HunyuanOCR-$QUANT.gguf" "mmproj-HunyuanOCR-$QUANT.gguf"; do
    TARGET="$MODELS_DIR/$FILE"
    if [ -f "$TARGET" ]; then
      echo "Model file '$TARGET' already exists, skipping download"
      continue
    fi
    echo "Downloading '$FILE' from https://huggingface.co/$GGUF_REPO"
    curl -L --fail --retry 3 --progress-bar -o "$TARGET" "https://huggingface.co/$GGUF_REPO/resolve/main/$FILE"
  done
fi

echo "OCR setup complete"
echo "Model files: $MODELS_DIR"
echo "Run OCR via: $SCRIPT_DIR/run.sh --content ./content"
