import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocrlib import imageio
from ocrlib.engines.hunyuanocr import (
    derive_words,
    group_lines,
    markdown_to_text,
    normalize_box,
    parse_spotting_json,
)
from ocrlib.model import Block, Doc, Line, Meta, Source, Word
from ocrlib.writers import WRITERS

TEST_DIR = Path(__file__).parent
FIXTURE = TEST_DIR / "testdata" / "page.jxl"


def ensure_fixture():
    if FIXTURE.exists():
        return
    import io

    import pyvips
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("L", (600, 400), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=28)
    lines = ["Die Photographie", "im 19. Jahrhundert", "Alte Schriften", "Fraktur und Antiqua"]
    y = 40
    for line in lines:
        draw.text((50, y), line, fill=0, font=font)
        y += 56
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    vips_image = pyvips.Image.new_from_buffer(buffer.getvalue(), "")
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    vips_image.write_to_file(str(FIXTURE))


def test_parse_spotting_json_bare():
    items = parse_spotting_json('[{"box": [10, 20, 500, 80], "text": "Hallo Welt"}]')
    assert items == [{"box": [10, 20, 500, 80], "text": "Hallo Welt"}]


def test_parse_spotting_json_fenced_and_prose():
    text = 'Ergebnis:\n```json\n[{"box": [1, 2, 3, 4], "text": "a"}]\n```\nFertig.'
    items = parse_spotting_json(text)
    assert len(items) == 1
    assert items[0]["text"] == "a"


def test_parse_spotting_json_invalid():
    try:
        parse_spotting_json("no json here")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_normalize_box():
    assert normalize_box([0, 0, 1000, 1000], 2000, 1000) == [0, 0, 2000, 1000]
    assert normalize_box([500, 100, 400, 900], 1000, 1000) == [400, 100, 500, 900]
    assert normalize_box([-5, 0, 1001, 500], 1000, 1000) == [0, 0, 1000, 500]


def test_derive_words():
    words = derive_words("Alte Schriften", [100, 10, 300, 50])
    assert [w.text for w in words] == ["Alte", "Schriften"]
    assert words[0].bbox[0] == 100
    assert words[1].bbox[2] == 300
    assert words[0].bbox_source == "derived"


def test_group_lines_paragraph_gap():
    lines = [
        {"text": "eins", "bbox": [10, 10, 100, 40], "order": 0},
        {"text": "zwei", "bbox": [10, 50, 100, 80], "order": 1},
        {"text": "drei", "bbox": [10, 200, 100, 230], "order": 2},
    ]
    blocks = group_lines(lines)
    assert len(blocks) == 2
    assert [l["text"] for l in blocks[0]] == ["eins", "zwei"]
    assert [l["text"] for l in blocks[1]] == ["drei"]


def test_markdown_to_text():
    text = markdown_to_text("# Titel\nEin **Wort** | a | b\n- - -\n")
    assert "Titel" in text
    assert "Ein Wort a b" in text


def test_doc_serialization():
    doc = Doc(
        source=Source(file="x.jxl", format="jxl", width=100, height=50, dpi=None),
        meta=Meta(engine="hunyuanocr", model="default", quant="bf16", tasks=["spotting_json"]),
        blocks=[Block(type="text", bbox=[0, 0, 100, 50], order=0, lines=[Line(text="a b", bbox=[0, 0, 100, 50], order=0, words=[Word(text="a", bbox=[0, 0, 50, 50])])])],
        text="a b",
    )
    data = doc.to_dict()
    assert data["version"] == "1.0"
    assert "dpi" not in data["source"]
    assert data["blocks"][0]["lines"][0]["words"][0]["bbox_source"] == "derived"
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "out.ocr.json"
        WRITERS.get("json").write(doc, path)
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded["meta"]["engine"] == "hunyuanocr"
        assert loaded["blocks"][0]["lines"][0]["text"] == "a b"


def test_imageio_jxl():
    ensure_fixture()
    image = imageio.load(FIXTURE)
    assert image.width == 600
    assert image.height == 400
    payload = imageio.to_image_bytes(image, max_side=300)
    assert len(payload) > 0


def test_hugo_discovery():
    from ocrlib.hugo import collect_content_images

    site_root = TEST_DIR.parent.parent / "exampleSite"
    content_dir = site_root / "content"
    if not content_dir.exists():
        return
    groups = collect_content_images(site_root, content_dir)
    all_images = [img for _, images in groups for img in images]
    assert any(img.name == "example.jpg" for img in all_images)


def main():
    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    failures = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
        except Exception as e:
            failures += 1
            print(f"FAIL {name}: {e}")
    print(f"{len(tests) - failures}/{len(tests)} tests passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
