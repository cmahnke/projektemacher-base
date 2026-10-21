#!/usr/bin/env bash
#
# Integration test for the webmention/pingback endpoint
# ('services/webmentions/webmention.php'), using two instances of PHP's
# built-in web server - one serving the endpoint, one acting as the
# "source site" that mentions link from. Requires php and curl.
#
# Usage: test-endpoint.sh
# Exit code: 0 when all checks pass, 1 otherwise.

set -u -o pipefail

THEME_DIR="$(cd "$(dirname "$(realpath "$0")")/../.." && pwd)"
ENDPOINT_DIR="$THEME_DIR/services/webmentions"
ENDPOINT_PORT=18223
SOURCE_PORT=18224
ENDPOINT_URL="http://127.0.0.1:$ENDPOINT_PORT"
SOURCE_URL="http://127.0.0.1:$SOURCE_PORT"
TARGET_URL="https://example.org/blog/post/"

TMP="$(mktemp -d /tmp/webmention-test.XXXXXX)"
ENDPOINT_PID=""
SOURCE_PID=""
FAILURES=0
COUNT=0

fail() {
  FAILURES=$((FAILURES + 1))
  echo "FAIL: $*"
}

check() {
  local name="$1" expected="$2" actual="$3"
  COUNT=$((COUNT + 1))
  if [ "$actual" = "$expected" ]; then
    echo "ok: $name"
  else
    fail "$name (expected '$expected', got '$actual')"
  fi
}

cleanup() {
  [ -n "$ENDPOINT_PID" ] && kill "$ENDPOINT_PID" 2>/dev/null
  [ -n "$SOURCE_PID" ] && kill "$SOURCE_PID" 2>/dev/null
  rm -rf "$TMP"
}
trap cleanup EXIT

post() {
  curl -s -o "$TMP/response" -w '%{http_code}' "$@" 2>/dev/null || echo curl-error
}

# --- Source site fixtures ------------------------------------------------

mkdir -p "$TMP/source"
cat > "$TMP/source/link.html" <<EOF
<!DOCTYPE html>
<html>
<head><title>My Reply</title><meta name="author" content="Meta Author"></head>
<body>
  <article class="h-entry">
    <p class="p-name">My Reply</p>
    <p class="p-content">Great post, see <a class="u-in-reply-to" href="$TARGET_URL">the post</a>.</p>
    <div class="p-author h-card"><a class="u-url" href="$SOURCE_URL/author">Test Author</a></div>
  </article>
</body>
</html>
EOF
cat > "$TMP/source/nolink.html" <<'EOF'
<!DOCTYPE html>
<html><head><title>No link here</title></head>
<body><article class="h-entry"><p class="p-content">Nothing points at the target.</p></article></body>
</html>
EOF
cat > "$TMP/source/link-ping.html" <<EOF
<!DOCTYPE html>
<html><head><title>Pingback Source</title></head>
<body><a href="$TARGET_URL">The target post</a></body>
</html>
EOF
# Erroring pages that do link to the target - used to check that only
# HTTP 200 responses can add mentions.
for CODE in 404 500; do
cat > "$TMP/source/status$CODE.php" <<EOF
<?php http_response_code($CODE); ?>
<!DOCTYPE html>
<html><head><title>Broken Source $CODE</title></head>
<body><a href="$TARGET_URL">the target post</a></body>
</html>
EOF
done
cat > "$TMP/source/redirect.php" <<EOF
<?php
http_response_code(302);
header('Location: link.html');
?>
EOF
# Internet Archive save stub: records method, URI, Authorization
# header and request body into a log file, always answers 200.
cat > "$TMP/source/archive.php" <<'EOF'
<?php
$entry = $_SERVER['REQUEST_METHOD'] . ' ' . $_SERVER['REQUEST_URI'] . "\n"
    . 'auth: ' . ($_SERVER['HTTP_AUTHORIZATION'] ?? 'none') . "\n"
    . 'body: ' . file_get_contents('php://input') . "\n---\n";
file_put_contents(__DIR__ . '/archive-calls.log', $entry, FILE_APPEND);
http_response_code(200);
echo 'save acknowledged';
EOF
# Archive endpoint that always fails (HTTP 500) - to verify that an
# archiving failure never fails the mention response. It logs its own
# request for the 'attempted' check below.
cat > "$TMP/source/archivefail.php" <<'EOF'
<?php
file_put_contents(__DIR__ . '/archive-calls.log',
    $_SERVER['REQUEST_METHOD'] . ' ' . $_SERVER['REQUEST_URI'] . "\n---\n",
    FILE_APPEND);
http_response_code(500);
echo 'save failed';
EOF

# --- Endpoint instance (functional tests) --------------------------------

echo "Starting web servers ..."
(php -S "127.0.0.1:$SOURCE_PORT" -t "$TMP/source" >/dev/null 2>&1) &
SOURCE_PID=$!
(
  cd "$ENDPOINT_DIR"
  exec env \
    WEBMENTION_DATA_DIR="$TMP/data" \
    WEBMENTION_ALLOWED_DOMAINS='["example.org"]' \
    WEBMENTION_ALLOW_PRIVATE=1 \
    WEBMENTION_RATE_LIMIT=1000 \
    php -S "127.0.0.1:$ENDPOINT_PORT" webmention.php >/dev/null 2>&1
) &
ENDPOINT_PID=$!

for _ in $(seq 1 30); do
  SOURCE_UP=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$SOURCE_PORT/link.html" 2>/dev/null || echo 0)
  ENDPOINT_UP=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$ENDPOINT_URL" 2>/dev/null || echo 0)
  [ "$SOURCE_UP" = "200" ] && [ "$ENDPOINT_UP" != "0" ] && break
  sleep 0.2
done

# --- Checks --------------------------------------------------------------

STATUS=$(post -X POST "$ENDPOINT_URL" --data-urlencode "source=$SOURCE_URL/link.html" --data-urlencode "target=$TARGET_URL")
check "webmention with backlink is accepted" "202" "$STATUS"

STATUS=$(post -X POST "$ENDPOINT_URL" --data-urlencode "source=$SOURCE_URL/nolink.html" --data-urlencode "target=$TARGET_URL")
check "webmention without backlink is rejected" "422" "$STATUS"

STATUS=$(post -X POST "$ENDPOINT_URL" --data-urlencode "target=$TARGET_URL")
check "webmention with missing source" "400" "$STATUS"

STATUS=$(post -X POST "$ENDPOINT_URL" --data-urlencode "source=$SOURCE_URL/link.html" --data-urlencode "target=https://evil.org/blog/post/")
check "webmention with non-allowed target" "400" "$STATUS"

STATUS=$(post -X POST "$ENDPOINT_URL" --data-urlencode "source=$SOURCE_URL/link.html" --data-urlencode "target=$TARGET_URL" --data-urlencode "url2=spam-bot-was-here")
check "honeypot request pretends acceptance" "202" "$STATUS"

STATUS=$(curl -s -o "$TMP/response-get" -w '%{http_code}' "$ENDPOINT_URL" 2>/dev/null || echo curl-error)
check "GET is rejected" "405" "$STATUS"

# Pingback via XML-RPC
PINGRESPONSE=$(cat <<EOF | curl -s -X POST -H 'Content-Type: text/xml' --data-binary @- "$ENDPOINT_URL" 2>/dev/null
<?xml version="1.0"?>
<methodCall><methodName>pingback.ping</methodName>
<params><param><value><string>$SOURCE_URL/link-ping.html</string></value></param>
<param><value><string>$TARGET_URL</string></value></param></params>
</methodCall>
EOF
)
COUNT=$((COUNT + 1))
if echo "$PINGRESPONSE" | grep -q "Pingback registered"; then
  echo "ok: pingback registers"
else
  fail "pingback registers ('$PINGRESPONSE')"
fi

PINGRESPONSE=$(cat <<EOF | curl -s -X POST -H 'Content-Type: text/xml' --data-binary @- "$ENDPOINT_URL" 2>/dev/null
<?xml version="1.0"?>
<methodCall><methodName>pingback.ping</methodName>
<params><param><value><string>$SOURCE_URL/nolink.html</string></value></param>
<param><value><string>$TARGET_URL</string></value></param></params>
</methodCall>
EOF
)
COUNT=$((COUNT + 1))
if echo "$PINGRESPONSE" | grep -q "faultCode" && echo "$PINGRESPONSE" | grep -q "17"; then
  echo "ok: pingback without backlink answers with fault 17"
else
  fail "pingback without backlink answers with fault 17 ('$PINGRESPONSE')"
fi

# Reachability gate: sources answering with an HTTP error code are
# rejected even when they link to the target.
STATUS=$(post -X POST "$ENDPOINT_URL" --data-urlencode "source=$SOURCE_URL/status404.php" --data-urlencode "target=$TARGET_URL")
check "404 source is rejected" "400" "$STATUS"
STATUS=$(post -X POST "$ENDPOINT_URL" --data-urlencode "source=$SOURCE_URL/status500.php" --data-urlencode "target=$TARGET_URL")
check "500 source is rejected" "400" "$STATUS"
STATUS=$(curl -s -o /dev/null -w '%{http_code}' "$SOURCE_URL/status404.php" 2>/dev/null || echo 0)
check "404 fixture really answers 404" "404" "$STATUS"

# Redirects are followed - the final 200 counts.
STATUS=$(post -X POST "$ENDPOINT_URL" --data-urlencode "source=$SOURCE_URL/redirect.php" --data-urlencode "target=$TARGET_URL")
check "redirecting source resolving to 200 is accepted" "202" "$STATUS"

# Archiving is off by default - no save request may have reached the
# stub so far.
COUNT=$((COUNT + 1))
if [ ! -f "$TMP/source/archive-calls.log" ]; then
  echo "ok: no archive request when archiving is disabled"
else
  fail "no archive request when archiving is disabled ('$(cat "$TMP/source/archive-calls.log" 2>/dev/null)')"
fi

# --- Storage checks ------------------------------------------------------

python3 - "$TMP/data" "$TARGET_URL" <<'PY'
import json
import sys
from pathlib import Path

failures = 0


def fail(msg):
    global failures
    print(f"FAIL: {msg}")
    failures += 1


files = sorted(Path(sys.argv[1]).glob("*.json"))
if not files:
    fail(f"no data files in {sys.argv[1]}")
    sys.exit(1)
doc = json.loads(files[0].read_text())
mentions = doc.get("mentions", [])
if len(mentions) != 3:
    # reply (webmention) + mention (pingback) + redirected source; the
    # honeypot request is not stored, 404/500/missing/evil and the
    # nolink requests are rejected.
    fail(f"expected 3 stored mentions, got {len(mentions)}")
    sys.exit(1)
reply = next((m for m in mentions if m.get("type") == "reply"), None)
mention = next((m for m in mentions if m.get("source", "").endswith("link-ping.html")), None)
redirected = next((m for m in mentions if m.get("source", "").endswith("redirect.php")), None)
if redirected is None:
    fail("redirecting source was not stored")
if reply is None:
    fail("no 'reply' entry stored (type detection failed)")
else:
    for key in ("source", "target", "received", "title", "content", "author"):
        if key not in reply:
            fail(f"reply entry misses '{key}'")
    if reply.get("title") != "My Reply":
        fail(f"title extraction failed: {reply.get('title')!r}")
    author = reply.get("author", {})
    if author.get("name") != "Test Author":
        fail(f"author extraction failed: {author!r}")
    if reply.get("content") != "Great post, see the post.":
        fail(f"content extraction failed: {reply.get('content')!r}")
if mention is None:
    fail("no stored entry for the pingback source")
sys.exit(1 if failures else 0)
PY
if [ $? -eq 0 ]; then
  COUNT=$((COUNT + 1))
  echo "ok: storage contains the verified and extracted entries"
else
  COUNT=$((COUNT + 1))
  FAILURES=$((FAILURES + 1))
fi

# --- Archiving (separate instances) ---------------------------------------

kill_endpoint() {
  kill "$ENDPOINT_PID" 2>/dev/null
  wait "$ENDPOINT_PID" 2>/dev/null
  ENDPOINT_PID=""
}

start_endpoint() {
  local data_dir="$1" rate_limit="$2"; shift 2
  (
    cd "$ENDPOINT_DIR"
    exec env \
      WEBMENTION_DATA_DIR="$data_dir" \
      WEBMENTION_ALLOWED_DOMAINS='["example.org"]' \
      WEBMENTION_ALLOW_PRIVATE=1 \
      WEBMENTION_RATE_LIMIT="$rate_limit" \
      "$@" \
      php -S "127.0.0.1:$ENDPOINT_PORT" webmention.php >/dev/null 2>&1
  ) &
  ENDPOINT_PID=$!
}

wait_endpoint_up() {
  for _ in $(seq 1 30); do
    UP=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$ENDPOINT_URL" 2>/dev/null || echo 0)
    [ "$UP" = "400" ] && break
    sleep 0.2
  done
}

delete_stale_endpoint() {
  kill "$ENDPOINT_PID" 2>/dev/null
  wait "$ENDPOINT_PID" 2>/dev/null
  ENDPOINT_PID=""
  rm -f "$TMP/source/archive-calls.log"
}

delete_stale_endpoint

# SPN2 credentials mode: the save API stub must have recorded the POST
# with the Authorization header and the source URL.
start_endpoint "$TMP/data-archive" 1000 \
  WEBMENTION_ARCHIVE=1 \
  "WEBMENTION_ARCHIVE_URL=$SOURCE_URL/archive.php" \
  WEBMENTION_ARCHIVE_ACCESS_KEY=test-access \
  WEBMENTION_ARCHIVE_SECRET_KEY=test-secret
wait_endpoint_up
STATUS=$(post -X POST "$ENDPOINT_URL" --data-urlencode "source=$SOURCE_URL/link.html" --data-urlencode "target=$TARGET_URL")
check "archiving instance accepts mention" "202" "$STATUS"
COUNT=$((COUNT + 1))
ARCHIVE_LOG=$(cat "$TMP/source/archive-calls.log" 2>/dev/null)
if echo "$ARCHIVE_LOG" | grep -q '^POST' \
  && echo "$ARCHIVE_LOG" | grep -q 'LOW test-access:test-secret' \
  && echo "$ARCHIVE_LOG" | grep -q 'link.html'; then
  echo "ok: credentialed archive save request recorded"
else
  fail "credentialed archive save request recorded ('$ARCHIVE_LOG')"
fi
delete_stale_endpoint

# Anonymous mode: a plain GET on '<archive URL>/<source>', no
# Authorization header.
start_endpoint "$TMP/data-archive-anon" 1000 \
  WEBMENTION_ARCHIVE=1 \
  "WEBMENTION_ARCHIVE_URL=$SOURCE_URL/archive.php"
wait_endpoint_up
STATUS=$(post -X POST "$ENDPOINT_URL" --data-urlencode "source=$SOURCE_URL/link.html" --data-urlencode "target=$TARGET_URL")
check "anonymous archiving instance accepts mention" "202" "$STATUS"
COUNT=$((COUNT + 1))
ARCHIVE_LOG=$(cat "$TMP/source/archive-calls.log" 2>/dev/null)
if echo "$ARCHIVE_LOG" | grep -q '^GET' \
  && echo "$ARCHIVE_LOG" | grep -q 'archive.php/http' \
  && echo "$ARCHIVE_LOG" | grep -q 'link.html' \
  && echo "$ARCHIVE_LOG" | grep -q 'auth: none'; then
  echo "ok: anonymous archive save request recorded"
else
  fail "anonymous archive save request recorded ('$ARCHIVE_LOG')"
fi
delete_stale_endpoint

# Failing archive endpoint: the mention must still be accepted.
start_endpoint "$TMP/data-archive-fail" 1000 \
  WEBMENTION_ARCHIVE=1 \
  "WEBMENTION_ARCHIVE_URL=$SOURCE_URL/archivefail.php"
wait_endpoint_up
STATUS=$(post -X POST "$ENDPOINT_URL" --data-urlencode "source=$SOURCE_URL/link.html" --data-urlencode "target=$TARGET_URL")
check "mention still accepted when archive save fails" "202" "$STATUS"
COUNT=$((COUNT + 1))
if grep -q 'archivefail.php' "$TMP/source/archive-calls.log" 2>/dev/null; then
  echo "ok: failing archive endpoint was attempted"
else
  fail "failing archive endpoint was attempted"
fi
delete_stale_endpoint

# Half-configured credentials (access key set, secret missing): the
# mention is still accepted via the anonymous fallback and the
# misconfiguration is reported on stderr.
(
  cd "$ENDPOINT_DIR"
  exec env \
    WEBMENTION_DATA_DIR="$TMP/data-archive-half" \
    WEBMENTION_ALLOWED_DOMAINS='["example.org"]' \
    WEBMENTION_ALLOW_PRIVATE=1 \
    WEBMENTION_RATE_LIMIT=1000 \
    WEBMENTION_ARCHIVE=1 \
    "WEBMENTION_ARCHIVE_URL=$SOURCE_URL/archive.php" \
    WEBMENTION_ARCHIVE_ACCESS_KEY=test-access \
    php -S "127.0.0.1:$ENDPOINT_PORT" webmention.php > "$TMP/half-config-stderr.log" 2>&1
) &
ENDPOINT_PID=$!
wait_endpoint_up
STATUS=$(post -X POST "$ENDPOINT_URL" --data-urlencode "source=$SOURCE_URL/link.html" --data-urlencode "target=$TARGET_URL")
check "half-configured archiving instance accepts mention" "202" "$STATUS"
COUNT=$((COUNT + 1))
if grep -q 'must both be set' "$TMP/half-config-stderr.log" 2>/dev/null; then
  echo "ok: half-configured archive credentials warn on stderr"
else
  fail "half-configured archive credentials warn on stderr ('$(cat "$TMP/half-config-stderr.log" 2>/dev/null | head -3)')"
fi
COUNT=$((COUNT + 1))
ARCHIVE_LOG=$(cat "$TMP/source/archive-calls.log" 2>/dev/null)
if echo "$ARCHIVE_LOG" | grep -q '^GET' \
  && echo "$ARCHIVE_LOG" | grep -q 'auth: none' \
  && ! echo "$ARCHIVE_LOG" | grep -q '^POST'; then
  echo "ok: half-configured credentials fall back to anonymous save"
else
  fail "half-configured credentials fall back to anonymous save ('$ARCHIVE_LOG')"
fi
delete_stale_endpoint

# --- Rate limiting (separate instance) -----------------------------------

start_endpoint "$TMP/data-rl" 1 WEBMENTION_RATE_WINDOW=3600

# GET is answered with 405 before any rate limit counting.
for _ in $(seq 1 30); do
  UP=$(curl -s -o /dev/null -w '%{http_code}' "$ENDPOINT_URL" 2>/dev/null || echo 0)
  [ "$UP" = "405" ] && break
  sleep 0.2
done

STATUS=$(post -X POST "$ENDPOINT_URL" --data-urlencode "source=$SOURCE_URL/link.html" --data-urlencode "target=$TARGET_URL")
check "rate limited instance accepts first request" "202" "$STATUS"
STATUS=$(post -X POST "$ENDPOINT_URL" --data-urlencode "source=$SOURCE_URL/link.html" --data-urlencode "target=$TARGET_URL")
check "rate limited instance rejects further requests" "429" "$STATUS"

echo
if [ "$FAILURES" -gt 0 ]; then
  echo "$FAILURES of $COUNT checks failed"
  exit 1
fi
echo "All $COUNT checks passed"
exit 0
