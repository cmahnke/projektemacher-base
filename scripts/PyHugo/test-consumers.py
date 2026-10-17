"""
Tests the scripts built on top of PyHugo (`preview.py`, `post-calendar.py`)
against the example site's content. Runs entirely on temporary copies, the
example site itself is never modified.
"""

import sys, os, shutil, tempfile, subprocess
from pathlib import Path

repoRoot = Path(__file__).parents[2]
exampleSite = repoRoot / "exampleSite"

failures = []


def check(name, condition, detail=""):
    status = "ok" if condition else "FAILED"
    print(f"  [{status}] {name} {detail}")
    if not condition:
        failures.append(name)


def runScript(script, cwd):
    result = subprocess.run([sys.executable, str(script)], cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
    return result


previewTemplate = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <rect id="textbox" x="0" y="450" width="1200" height="100" />
    <style>
      @font-face {{
        font-family: 'Nunito';
        src: url("../../themes/projektemacher-base/static/fonts/nunito-v14-latin-ext_latin-regular.ttf") format('truetype');
      }}
    </style>
  </defs>
  <text id="text-container" xml:space="preserve" style="shape-inside:url(#textbox);font-size:80px;line-height:1.25;font-family:Nunito;text-align:center;white-space:pre;fill:#000000;"></text>
</svg>
"""

previewConfig = """[params]
  [params.preview]
    outputPrefix = "ogPreview"
    format = "svg"
    source = "overlay"

    [params.preview.size]
      height = 630
      width = 1200

    [params.preview.svg]
      template = "./Source Files/Other/preview-template.svg"
      removeMissing = true
"""


def testPreview():
    print("preview.py:")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copytree(exampleSite / "content", tmp / "content")
        # Deterministic short and long titles
        (tmp / "content" / "short-title").mkdir(parents=True)
        (tmp / "content" / "short-title" / "index.md").write_text("---\ntitle: Kurz\n---\n")
        (tmp / "content" / "long-title").mkdir(parents=True)
        (tmp / "content" / "long-title" / "index.md").write_text(
            "---\ntitle: Dieses ist ein ausgesprochen langer Titel für einen Blogartikel über die Digitalisierung historischer Quellen und Druckwerke\n---\n"
        )
        (tmp / "config" / "_default").mkdir(parents=True)
        (tmp / "config" / "_default" / "config.toml").write_text(previewConfig)
        (tmp / "Source Files" / "Other").mkdir(parents=True)
        (tmp / "Source Files" / "Other" / "preview-template.svg").write_text(previewTemplate)
        fontTarget = tmp / "themes" / "projektemacher-base" / "static" / "fonts"
        fontTarget.mkdir(parents=True)
        font = repoRoot / "static" / "fonts" / "nunito-v14-latin-ext_latin-regular.ttf"
        if font.exists():
            shutil.copy(font, fontTarget)

        result = runScript(repoRoot / "scripts" / "preview.py", tmp)
        check("preview.py exits successfully", result.returncode == 0)

        shortSVG = tmp / "content" / "short-title" / "ogPreview.svg"
        longSVG = tmp / "content" / "long-title" / "ogPreview.svg"
        exampleSVG = tmp / "content" / "posts" / "development" / "ogPreview.svg"
        check("preview for the example site content was generated", exampleSVG.exists())
        check("short title preview was generated", shortSVG.exists())
        check("long title preview was generated", longSVG.exists())

        if shortSVG.exists():
            content = shortSVG.read_text()
            check("short title keeps its font size", "font-size:80px" in content)
            check("short title has no textLength", "textLength" not in content)
        if longSVG.exists():
            content = longSVG.read_text()
            check("long title font size was shrunk", "font-size:80px" not in content and "font-size:" in content)
            check("long title got a textLength", 'textLength="' in content and 'lengthAdjust="spacingAndGlyphs"' in content)
        if exampleSVG.exists():
            content = exampleSVG.read_text()
            check("example site title was set", "Developing shortcodes" in content)


def testCalendar():
    print("post-calendar.py:")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copytree(exampleSite / "content", tmp / "content")
        shutil.copy(exampleSite / "hugo.toml", tmp)
        result = runScript(repoRoot / "scripts" / "post-calendar.py", tmp)
        check("post-calendar.py exits successfully", result.returncode == 0)
        check("calendar output is valid ICS", result.stdout.startswith("BEGIN:VCALENDAR") and "END:VCALENDAR" in result.stdout)

    # Running inside the example site directly
    result = runScript(repoRoot / "scripts" / "post-calendar.py", exampleSite)
    check("post-calendar.py works inside the example site", result.returncode == 0 and result.stdout.startswith("BEGIN:VCALENDAR"))


if __name__ == "__main__":
    testPreview()
    testCalendar()
    if failures:
        print(f"\n{len(failures)} check(s) failed: {failures}")
        sys.exit(1)
    print("\nAll checks passed")
