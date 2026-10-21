#!/usr/bin/env bash
#
# Test for 'scripts/webmention/lint.py' - builds fixture files with
# valid and broken mentions, runs the linter and asserts the merged
# output. Requires python3.
#
# Usage: test-lint.sh
# Exit code: 0 when all checks pass, 1 otherwise.

set -u -o pipefail

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
TMP="$(mktemp -d /tmp/webmention-lint-test.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT
FAILURES=0

check() {
  local name="$1" expected="$2" actual="$3"
  if [ "$actual" = "$expected" ]; then
    echo "ok: $name"
  else
    echo "FAIL: $name (expected '$expected', got '$actual')"
    FAILURES=$((FAILURES + 1))
  fi
}

# --- Fixtures ------------------------------------------------------------

python3 - "$TMP" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
raw = root / "raw"
raw.mkdir(parents=True)

def write(name, obj):
    (raw / name).write_text(obj if isinstance(obj, str) else json.dumps(obj), encoding="utf-8")

# Valid document: reply, like (without author), plus an entry with an
# unknown type and a very long content that needs truncation.
write("a.json", {
    "target": "https://example.org/blog/post/",
    "mentions": [
        {
            "source": "https://other.org/replies/1",
            "received": "2026-01-02T10:00:00Z",
            "type": "reply",
            "title": "My reply  <b>bold</b>",
            "content": "A" * 2000,
            "author": {"name": "  Anna   Example ", "url": "https://other.org/~anna"},
        },
        {
            "source": "https://other.org/likes/1",
            "received": "2026-01-03T10:00:00Z",
            "type": "wtf",
        },
    ],
})

# Same source twice: the older entry must lose.
write("b.json", {
    "target": "https://example.org/blog/post/",
    "mentions": [
        {
            "source": "https://other.org/replies/1",
            "received": "2026-01-01T10:00:00Z",
            "type": "mention",
        },
    ],
})

# Different target, a bare list document (tolerated), an entry with a
# mismatching target and one with a missing field.
write("c.json", {
    "target": "https://example.org/blog/other/",
    "mentions": [
        {
            "source": "https://other.org/links/2",
            "target": "https://elsewhere.org/blog/other/",
            "received": "2026-01-04T10:00:00Z",
        },
    ],
})
write("d.json", [
    {
        "source": "https://other.org/bare/1",
        "target": "https://example.org/blog/other/",
        "received": "2026-01-05T10:00:00Z",
        "type": "pingback",
    }
])
write("e.json", {
    "target": "https://example.org/blog/other/",
    "mentions": [{"source": "https://other.org/missing-received/1"}],
})

# Broken documents.
write("f.json", "not json at all {")
write("g.json", {"mentions": []})
PY

# --- Run ----------------------------------------------------------------

python3 "$SCRIPT_DIR/lint.py" "$TMP/raw" "$TMP/out/mentions.json" > "$TMP/lint.log" 2>&1
EXIT=$?

python3 - "$TMP/out/mentions.json" <<'PY'
import json
import sys
from pathlib import Path

failures = 0


def fail(msg):
    global failures
    print(f"FAIL: {msg}")
    failures += 1


def ok(name):
    print(f"ok: {name}")


doc = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if "generated" in doc:
    fail("generated timestamp present (output must stay deterministic)")
else:
    ok("no generated timestamp (deterministic output)")
mentions = doc.get("mentions", {})

if "https://example.org/blog/post" not in mentions:
    fail("blog/post group missing (key without trailing slash)")
else:
    ok("key variant without trailing slash present")
if "https://example.org/blog/post/" not in mentions:
    fail("blog/post group missing (key with trailing slash)")
else:
    ok("key variant with trailing slash present")

post = mentions.get("https://example.org/blog/post", [])
if len(post) != 2:
    fail(f"expected 2 entries for blog/post (duplicate must lose), got {len(post)}")
else:
    ok("duplicate source deduped")
reply = post[0]
if reply.get("source") != "https://other.org/replies/1" or reply.get("type") != "reply":
    fail(f"reply entry wrong: {reply}")
else:
    ok("reply entry kept with newest state")
if len(reply.get("content", "")) > 1000:
    fail("content not truncated")
else:
    ok("content truncated to 1000 chars")
if "<" in reply.get("title", ""):
    fail(f"title not sanitized: {reply.get('title')!r}")
else:
    ok("title sanitized (tags stripped, entities collapsed)")
if reply.get("author", {}).get("name") != "Anna Example":
    fail(f"author name not normalized: {reply.get('author')!r}")
else:
    ok("author name collapsed")

other = mentions.get("https://example.org/blog/other/", [])
if len(other) != 1 or other[0].get("source") != "https://other.org/bare/1":
    fail(f"bare-list document mishandled: {other}")
else:
    ok("bare list document accepted, mismatching target dropped")
if other and other[0].get("type") != "pingback":
    fail(f"pingback type lost: {other[0]}")
else:
    ok("pingback type preserved")

sys.exit(1 if failures else 0)
PY
if [ $? -eq 0 ]; then
  :
else
  FAILURES=$((FAILURES + 1))
fi

check "lint exit code" "0" "$EXIT"

# Deterministic output: a second run over the same fixtures must be
# byte-identical (the harvest workflow only commits on real mention
# changes).
python3 "$SCRIPT_DIR/lint.py" "$TMP/raw" "$TMP/out2/mentions.json" > "$TMP/lint2.log" 2>&1
if cmp -s "$TMP/out/mentions.json" "$TMP/out2/mentions.json"; then
  REPEAT="same"
else
  REPEAT="differ"
fi
check "byte-identical output on re-run" "same" "$REPEAT"

echo
if [ "$FAILURES" -gt 0 ]; then
  echo "$FAILURES check(s) failed"
  exit 1
fi
echo "All lint checks passed"
