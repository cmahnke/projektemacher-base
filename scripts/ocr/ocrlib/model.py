import json
from dataclasses import dataclass, field
from typing import List, Optional

MODEL_VERSION = "1.0"

BBOX_SOURCE_EXACT = "exact"
BBOX_SOURCE_DERIVED = "derived"


@dataclass
class Word:
    text: str
    bbox: List[int]
    bbox_source: str = BBOX_SOURCE_DERIVED
    confidence: Optional[float] = None

    def to_dict(self):
        return {
            "text": self.text,
            "bbox": self.bbox,
            "bbox_source": self.bbox_source,
            **({"confidence": self.confidence} if self.confidence is not None else {}),
        }


@dataclass
class Line:
    text: str
    bbox: List[int]
    order: int = 0
    confidence: Optional[float] = None
    words: List[Word] = field(default_factory=list)

    def to_dict(self):
        return {
            "text": self.text,
            "bbox": self.bbox,
            "order": self.order,
            **({"confidence": self.confidence} if self.confidence is not None else {}),
            "words": [w.to_dict() for w in self.words],
        }


@dataclass
class Block:
    type: str = "text"
    bbox: Optional[List[int]] = None
    order: int = 0
    lines: List[Line] = field(default_factory=list)

    def to_dict(self):
        return {
            "type": self.type,
            **({"bbox": self.bbox} if self.bbox is not None else {}),
            "order": self.order,
            "lines": [l.to_dict() for l in self.lines],
        }


@dataclass
class Source:
    file: str
    format: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    dpi: Optional[int] = None

    def to_dict(self):
        return {
            "file": self.file,
            **({"format": self.format} if self.format else {}),
            **({"width": self.width} if self.width is not None else {}),
            **({"height": self.height} if self.height is not None else {}),
            **({"dpi": self.dpi} if self.dpi is not None else {}),
        }


@dataclass
class Meta:
    engine: str
    model: Optional[str] = None
    engine_version: Optional[str] = None
    quant: Optional[str] = None
    segmenter: Optional[str] = None
    tasks: Optional[List[str]] = None
    timestamp: Optional[str] = None
    extra: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "engine": self.engine,
            **({"model": self.model} if self.model else {}),
            **({"engine_version": self.engine_version} if self.engine_version else {}),
            **({"quant": self.quant} if self.quant else {}),
            **({"segmenter": self.segmenter} if self.segmenter else {}),
            **({"tasks": self.tasks} if self.tasks else {}),
            **({"timestamp": self.timestamp} if self.timestamp else {}),
            **({"extra": self.extra} if self.extra else {}),
        }


@dataclass
class Doc:
    source: Source
    meta: Meta
    blocks: List[Block] = field(default_factory=list)
    text: str = ""

    def lines(self):
        for block in self.blocks:
            yield from block.lines

    def to_dict(self):
        return {
            "version": MODEL_VERSION,
            "source": self.source.to_dict(),
            "meta": self.meta.to_dict(),
            "blocks": [b.to_dict() for b in self.blocks],
            "text": self.text,
        }

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            f.write("\n")
