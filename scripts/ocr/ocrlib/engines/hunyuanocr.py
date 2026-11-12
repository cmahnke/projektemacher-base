import base64
import json
import logging
import re

import httpx

from ocrlib.engines.base import Engine, EngineResult
from ocrlib.model import BBOX_SOURCE_DERIVED, Block, Line, Word

logger = logging.getLogger(__name__)

DOC_PARSE_PROMPT = (
    "提取文档图片中正文的所有信息用markdown格式表示，其中页眉、页脚部分忽略，"
    "表格用html格式表达，文档中公式用latex格式表示，按照阅读顺序组织进行解析。"
)
SPOTTING_PROMPT = (
    "检测并识别图中所有的文字行，请按从上到下、从左到右的阅读顺序进行识别。 "
    '输出格式为 JSON 数组，每个元素必须包含："box": [xmin, ymin, xmax, ymax]'
    "（坐标需归一化到 [0, 1000] 范围内）；"
    '"text": "识别出的文字内容"。 '
    "注意：请直接输出 JSON 数组，不要包含任何多余的描述性文字。"
)

TASK_PROMPTS = {
    "doc_parse": DOC_PARSE_PROMPT,
    "spotting_json": SPOTTING_PROMPT,
}

DEFAULT_TASKS = ["spotting_json", "doc_parse"]


def parse_spotting_json(text):
    """Parse the spotting task output into a list of {box, text} dicts.

    The model is instructed to return a bare JSON array, but may wrap it in
    code fences or add prose around it.
    """
    start = text.find("[")
    while start >= 0:
        end = _balanced_array_end(text, start)
        if end is not None:
            try:
                data = json.loads(text[start:end])
            except json.JSONDecodeError:
                data = None
            if isinstance(data, list):
                return [item for item in data if isinstance(item, dict) and "box" in item]
        start = text.find("[", start + 1)
    raise ValueError(f"Could not parse spotting output as JSON array: {text[:200]!r}")


def _balanced_array_end(text, start):
    """Return the index just past the JSON array starting at `start`, or None."""
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return index + 1
    return None


def normalize_box(box, width, height):
    """Convert [0, 1000) normalized box coordinates to original image pixels."""
    values = [float(v) for v in box]
    if len(values) != 4:
        raise ValueError(f"Invalid box: {box!r}")
    x0, y0, x1, y1 = values
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    x0 = max(0, min(width, round(x0 * width / 1000)))
    x1 = max(0, min(width, round(x1 * width / 1000)))
    y0 = max(0, min(height, round(y0 * height / 1000)))
    y1 = max(0, min(height, round(y1 * height / 1000)))
    return [x0, y0, x1, y1]


def char_width(char):
    return 2 if ord(char) > 0x2E80 else 1


def derive_words(text, bbox):
    """Split a line into words with boxes proportional to their visual width.

    The spotting task only yields line-level geometry, so word boxes are
    approximated from the word's share of weighted character widths.
    """
    tokens = text.split()
    if not tokens:
        return []
    weights = [sum(char_width(c) for c in token) for token in tokens]
    total = sum(weights)
    x0, y0, x1, y1 = bbox
    span = x1 - x0
    words = []
    offset = 0
    for token, weight in zip(tokens, weights):
        start = x0 + round(span * offset / total)
        offset += weight
        end = x0 + round(span * offset / total)
        words.append(Word(text=token, bbox=[start, y0, end, y1], bbox_source=BBOX_SOURCE_DERIVED))
    return words


def group_lines(lines, gap_factor=0.75):
    """Group lines into blocks: a new block starts when the vertical gap
    between lines exceeds a fraction of the median line height, or when the
    horizontal ranges don't overlap."""
    if not lines:
        return []
    heights = sorted(l["bbox"][3] - l["bbox"][1] for l in lines)
    median_height = heights[len(heights) // 2]

    def horizontal_overlap(a, b):
        return min(a[2], b[2]) - max(a[0], b[0])

    blocks = []
    current = [lines[0]]
    for line in lines[1:]:
        previous = current[-1]
        gap = line["bbox"][1] - previous["bbox"][3]
        if gap > gap_factor * median_height or horizontal_overlap(previous["bbox"], line["bbox"]) <= 0:
            blocks.append(current)
            current = [line]
        else:
            current.append(line)
    blocks.append(current)
    return blocks


def block_bbox(lines):
    x0 = min(l["bbox"][0] for l in lines)
    y0 = min(l["bbox"][1] for l in lines)
    x1 = max(l["bbox"][2] for l in lines)
    y1 = max(l["bbox"][3] for l in lines)
    return [x0, y0, x1, y1]


def markdown_to_text(markdown):
    """Very small markdown-to-plain-text reduction for the text fallback path."""
    lines = []
    for line in markdown.splitlines():
        line = re.sub(r"^#{1,6}\s*", "", line)
        line = re.sub(r"\*\*?([^*]*)\*\*?", r"\1", line)
        line = re.sub(r"^[\s\-|:]+$", "", line)
        line = re.sub(r"\s+", " ", line.replace("|", " ")).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


class HunyuanOcrEngine(Engine):
    name = "hunyuanocr"

    def __init__(self, endpoint="http://127.0.0.1:18931", model="default", tasks=None,
                 temperature=0.0, top_k=-1, repeat_penalty=1.08, max_tokens=8192, timeout=600.0):
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.tasks = [task for task in (tasks or DEFAULT_TASKS) if task in TASK_PROMPTS]
        if not self.tasks:
            raise ValueError(f"No valid tasks in {tasks}, available: {', '.join(TASK_PROMPTS)}")
        self.temperature = temperature
        self.top_k = top_k
        self.repeat_penalty = repeat_penalty
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def server_version(self):
        try:
            response = self.client.get(f"{self.endpoint}/version", timeout=5.0)
            return response.json().get("version")
        except Exception:
            return None

    def complete(self, image_bytes: bytes, prompt: str) -> str:
        data_uri = "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode("ascii")
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_uri}},
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_k": self.top_k,
            "repeat_penalty": self.repeat_penalty,
            "top_p": 1.0,
        }
        response = self.client.post(f"{self.endpoint}/v1/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        choice = data["choices"][0]
        finish_reason = choice.get("finish_reason")
        content = choice["message"]["content"]
        if finish_reason not in ("stop", None):
            logger.warning(f"Inference finished with reason '{finish_reason}', output may be incomplete")
        return content

    def recognize(self, image_bytes: bytes, width: int, height: int, dpi=None) -> EngineResult:
        extra = {}
        lines = []
        text = ""
        for task in self.tasks:
            prompt = TASK_PROMPTS[task]
            output = self.complete(image_bytes, prompt)
            if task == "spotting_json":
                try:
                    items = parse_spotting_json(output)
                except ValueError as e:
                    logger.warning(str(e))
                    continue
                for order, item in enumerate(items):
                    try:
                        box = normalize_box(item["box"], width, height)
                    except (TypeError, ValueError) as e:
                        logger.warning(f"Skipping invalid box {item.get('box')!r}: {e}")
                        continue
                    lines.append({"text": str(item.get("text", "")).strip(), "bbox": box, "order": order})
            elif task == "doc_parse":
                extra["markdown"] = output

        if lines:
            lines.sort(key=lambda l: (l["bbox"][1], l["bbox"][0]))
            blocks = []
            for order, group in enumerate(group_lines(lines)):
                model_lines = []
                for line_order, line in enumerate(group):
                    model_lines.append(
                        Line(text=line["text"], bbox=line["bbox"], order=line_order,
                             words=derive_words(line["text"], line["bbox"]))
                    )
                blocks.append(Block(type="text", bbox=block_bbox(group), order=order, lines=model_lines))
            text = "\n".join(line["text"] for line in lines)
        elif "markdown" in extra:
            text = markdown_to_text(extra["markdown"])
            logger.warning("No spotting boxes available, structure omitted (text from doc_parse)")

        version = self.server_version()
        return EngineResult(blocks=blocks, text=text, engine_version=version, model=self.model, extra=extra)
