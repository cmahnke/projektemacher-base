from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

from ocrlib.model import Block


@dataclass
class EngineResult:
    blocks: List[Block] = field(default_factory=list)
    text: str = ""
    engine_version: Optional[str] = None
    model: Optional[str] = None
    extra: dict = field(default_factory=dict)


class Engine(ABC):
    name = None

    @abstractmethod
    def recognize(self, image_bytes: bytes, width: int, height: int, dpi: Optional[int]) -> EngineResult:
        pass
