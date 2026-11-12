from abc import ABC, abstractmethod
from pathlib import Path

from ocrlib.model import Doc


class Writer(ABC):
    name = None

    @abstractmethod
    def write(self, doc: Doc, output_path: Path):
        pass
