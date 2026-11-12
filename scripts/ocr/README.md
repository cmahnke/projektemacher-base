# OCR

AI based OCR for Hugo content images. It walks the content tree (via
[PyHugo](../PyHugo)), recognizes text and document structure and writes results
as JSON next to each image. JPEG XL (`.jxl`) and JPEG are decoded through
[libvips](https://libvips.github.io/libvips/) (`pyvips`).

The engine is [HunyuanOCR-1.5](https://huggingface.co/tencent/HunyuanOCR), a
1.1B OCR specialized vision language model served locally through
[llama.cpp](https://github.com/ggml-org/llama.cpp)'s OpenAI compatible
`llama-server` (Metal on Apple Silicon, CUDA on NVIDIA GPUs). Engines and
output formats are pluggable, additional ones can be registered with
`--plugin`.

## Requirements

- `pyenv` and Python (installed automatically, see `setup.sh`)
- `libvips` with JPEG XL support (`brew install libvips`, `apt install libvips-dev`)
- `llama.cpp` build `b11103` or newer (`brew install llama.cpp`), provides `llama-server`
- ~3 GB disk for the model files

## Setup

```sh
./scripts/ocr/setup.sh                # venv + dependencies + bf16 model download
./scripts/ocr/setup.sh --quant q8_0   # or the smaller q8_0 quantization
./scripts/ocr/setup.sh --skip-models  # venv and dependency checks only
```

## Usage

```sh
# Hugo mode: walk ./content recursively, skip drafts and existing results
./scripts/ocr/run.sh

# Explicit content directory (site root is derived from it)
./scripts/ocr/run.sh --content exampleSite/content

# Plain recursive scan of files or directories, independent of Hugo
./scripts/ocr/run.sh --input "Source Files/scans"

# Parallel inference (llama-server handles concurrent requests)
./scripts/ocr/run.sh --jobs 2

# Reuse a running llama-server (started manually or by a previous run with OCR_KEEP_SERVER=1)
./scripts/ocr/run.sh --endpoint http://127.0.0.1:18931 ...
OCR_ENDPOINT=http://127.0.0.1:18931 ./scripts/ocr/run.sh

# List what would be processed
./scripts/ocr/run.sh --dry-run
```

`run.sh` starts `llama-server` for the selected quantization (`OCR_QUANT`,
default `bf16`) and shuts it down afterwards. Set `OCR_KEEP_SERVER=1` to keep
it running across invocations, or `OCR_ENDPOINT` to attach to a server you
started yourself. See `--help` for all options (`ocr.py --help` shows the
recognition options).

### Environment variables

| Variable | Default | Meaning |
| --- | --- | --- |
| `OCR_QUANT` | `bf16` | Model quantization used by `setup.sh` and `run.sh` (`bf16` or `q8_0`) |
| `OCR_PORT` | `18931` | Port for the spawned `llama-server` |
| `OCR_ENDPOINT` | unset | Attach to a running server instead of spawning one |
| `OCR_KEEP_SERVER` | `0` | Keep the spawned server alive after the run |
| `OCR_LLAMA_CTX` | `16384` | `llama-server` context size |
| `OCR_LLAMA_N_PREDICT` | `8192` | `llama-server` output token budget |
| `OCR_PYTHON_VERSION` | `3.12.4` | Python version managed through pyenv |

## Output

Each image gets a sibling `<name>.ocr.json` (or `<output-dir>/<relative
path>/<name>.ocr.json` with `--output-dir`). Structure:

```json
{
  "version": "1.0",
  "source": {"file": "page.jxl", "format": "jxl", "width": 2400, "height": 3200, "dpi": 300},
  "meta": {"engine": "hunyuanocr", "model": "default", "quant": "bf16", "tasks": ["spotting_json", "doc_parse"], "timestamp": "..."},
  "blocks": [
    {
      "type": "text",
      "bbox": [120, 80, 2280, 480],
      "order": 0,
      "lines": [
        {
          "text": "Die Photographie",
          "bbox": [120, 80, 1200, 160],
          "order": 0,
          "words": [
            {"text": "Die", "bbox": [120, 80, 360, 160], "bbox_source": "derived"}
          ]
        }
      ]
    }
  ],
  "text": "Die Photographie"
}
```

Coordinates are always in original image pixels. `dpi` is only present when
the image carries resolution metadata. The model reports text line geometry
(`spotting_json`, normalized to 0-1000 and rescaled); word boxes are derived
proportionally within each line and marked `bbox_source: "derived"`. The
`doc_parse` task additionally provides the page as markdown, stored under
`meta.extra.markdown`.

## Quality notes

- The model handles Fraktur and historical print (its training explicitly
  includes historical and ancient scripts), but there are no published
  accuracy numbers for historical German scans yet: spot-check results on
  your own material before batch processing
- Very large scans are downscaled to `--max-side` (default 4000 px) before
  inference; the model supports up to 4K input
- HunyuanOCR-1.5 is released under the Tencent Hunyuan Community License
  (not an OSI license), the GGUF conversions used here are provided by ggml-org

## Extending

- Engines: implement `ocrlib.engines.base.Engine` and register it in
  `ocrlib/engines/__init__.py`, or provide a module through `--plugin`
  (e.g. a remote vLLM endpoint for
  [OvisOCR3](https://huggingface.co/ATH-MaaS/OvisOCR3), whose `word_spotting`
  task provides word level boxes and currently holds the best published
  Fraktur accuracy for local models)
- Output formats: implement `ocrlib.writers.base.Writer` and register it in
  `ocrlib/writers/__init__.py` (ALTO, PAGE XML or hOCR writers are natural
  additions; the canonical JSON model carries everything they need)

## Tests

```sh
./scripts/ocr/.venv/bin/python ./scripts/ocr/test-ocr.py
```
