#!/usr/bin/env bash

set -e -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ ! -x "$SCRIPT_DIR/.venv/bin/python" ]; then
  echo "Virtual environment not found, run $SCRIPT_DIR/setup.sh first" >&2
  exit 1
fi

export PYTHONPATH="${SCRIPTS_ROOT}:${PYTHONPATH}"

ATTACH=0
for ARG in "$@"; do
  case "$ARG" in
    --endpoint=*|--endpoint)
      ATTACH=1
      ;;
  esac
done
if [ -n "$OCR_ENDPOINT" ]; then
  ATTACH=1
fi

LLAMA_PID=""
cleanup() {
  if [ -n "$LLAMA_PID" ] && kill -0 "$LLAMA_PID" 2>/dev/null && [ "${OCR_KEEP_SERVER:-0}" != "1" ]; then
    kill "$LLAMA_PID" 2>/dev/null
    wait "$LLAMA_PID" 2>/dev/null
  fi
}
trap cleanup EXIT

PORT="${OCR_PORT:-18931}"
ENDPOINT="http://127.0.0.1:$PORT"

if [ "$ATTACH" -eq 0 ]; then
  QUANT="${OCR_QUANT:-bf16}"
  MODEL="$SCRIPT_DIR/models/hunyuanocr/HunyuanOCR-$QUANT.gguf"
  MMPROJ="$SCRIPT_DIR/models/hunyuanocr/mmproj-HunyuanOCR-$QUANT.gguf"
  if [ ! -f "$MODEL" ] || [ ! -f "$MMPROJ" ]; then
    echo "Model files not found ($MODEL, $MMPROJ), run $SCRIPT_DIR/setup.sh first" >&2
    exit 1
  fi
  if ! command -v llama-server >/dev/null 2>&1; then
    echo "llama-server not found, install llama.cpp (brew install llama.cpp) or run setup.sh" >&2
    exit 1
  fi
  echo "Starting llama-server on port $PORT (set OCR_ENDPOINT to attach to a running server instead)"
  llama-server \
    --model "$MODEL" \
    --mmproj "$MMPROJ" \
    --host 127.0.0.1 \
    --port "$PORT" \
    --ctx-size "${OCR_LLAMA_CTX:-16384}" \
    --n-predict "${OCR_LLAMA_N_PREDICT:-8192}" \
    --alias "${OCR_MODEL_ALIAS:-default}" \
    >/dev/null 2>&1 &
  LLAMA_PID=$!

  for _ in $(seq 1 "${OCR_STARTUP_TIMEOUT:-60}"); do
    if curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
      break
    fi
    if ! kill -0 "$LLAMA_PID" 2>/dev/null; then
      echo "llama-server exited prematurely, check model files and logs" >&2
      exit 1
    fi
    sleep 1
  done
  if ! curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
    echo "llama-server did not become healthy within ${OCR_STARTUP_TIMEOUT:-60}s" >&2
    exit 1
  fi
fi

STATUS=0
python "$SCRIPT_DIR/ocr.py" --endpoint "$ENDPOINT" "$@" || STATUS=$?

exit $STATUS
