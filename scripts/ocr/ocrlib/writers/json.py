import json
from pathlib import Path

from ocrlib.writers.base import Writer


class JsonWriter(Writer):
    name = "json"

    def write(self, doc, output_path: Path):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(doc.to_dict(), f, ensure_ascii=False, indent=2)
            f.write("\n")
