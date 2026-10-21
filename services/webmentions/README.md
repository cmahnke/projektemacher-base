# Webmentions / Pingback

The theme ships a self-contained collector service for
[Webmentions](https://www.w3.org/TR/webmention/) (and classic
[Pingbacks](https://www.hixie.ch/specs/pingback/pingback)) built to run
on cheap, PHP-only shared hosting. There is no database and no read
API: mentions arrive via HTTP POST, land in flat JSON files on the web
host, and reach the Hugo build as a single JSON document through a git
branch of the theme repository.

This document describes the complete pipeline and how to operate it.

# Process overview

```
sender (other website)
   |
   | POST source + target                POST XML-RPC pingback.ping
   v
endpoint.php (web host)  -- verifies + stores -->  data/<sha1(target)>.json
   |                                                     (web host)
   |  scheduled GitHub Action (cron) - one connection, one workflow
   |    1. deploy: checks + php -l + test suite + rsync deployment
   |    2. collect: rsync data/ back over the same connection
   |    3. lint.py (drops broken entries, dedupes, merges)
   v
site repository main branch: data/webmentions/mentions.json
   |
   |  Hugo reads it directly (hugo.Data.webmentions.mentions)
   v
- <link rel="webmention"> in the document head (advertisement)
- list rendered by partials/webmentions/list.html / {{< webmentions >}}
```

The web host holds no build credentials; the build machine holds no
web host credentials - only this repository's GitHub Action talks to
both sides, and the collected data lands on the site repository's
`main` branch as an ordinary Hugo data file (`data/webmentions/mentions.json`,
committed with `[skip ci]`).

# 1. The PHP collector (this repository, `services/webmentions/`)

| File             | Purpose                                                    |
|------------------|------------------------------------------------------------|
| `endpoint.php`   | POST-only front controller: Webmention (form fields `source`/`target`) and Pingback (XML-RPC `pingback.ping`) in one endpoint |
| `config.php`     | Configuration, all values overridable via environment variables |
| `lib/verify.php` | Source verification: fetch (5s timeout, 1 MB cap), SSRF guard, backlink check, basic microformats extraction (`h-entry`, `p-name`, `p-author`, `u-like-of`/`u-repost-of`/`u-in-reply-to`), sanitization |
| `lib/store.php`  | Flat file storage and rate limiting                        |
| `data/.htaccess` | Denies direct HTTP access to the stored data               |

Behaviour:

- Only POST is accepted, GET returns 405. There is **no read API**.
- Every mention is verified before storing: the target must belong to
  the configured domains and the source document must link back to it.
- Mentions are published automatically - no moderation queue. Incoming
  spam is handled with: domain allowlist, per-IP rate limit, a
  honeypot form field (`url2` - bots filling it get an invisible 202
  but nothing is stored), strict timeout/size limits and text
  sanitization (tags stripped, lengths capped).
- Re-pings from the same source replace the previous entry (dedup).

## Storage format

One JSON document per target at `data/<sha1(normalized target)>.json`:

```json
{
  "target": "https://example.org/blog/post/",
  "mentions": [
    {
      "source": "https://other.org/replies/1",
      "target": "https://example.org/blog/post/",
      "type": "reply",
      "received": "2026-10-20T09:15:00Z",
      "title": "My reply",
      "content": "Plain text, sanitized and capped at 500 chars",
      "author": { "name": "Anna Example", "url": "https://other.org/~anna" }
    }
  ]
}
```

All writes are atomic (temp file + rename), so the files are always
complete - the storage cannot "break".

## Configuration (`config.php` / environment)

| Variable                     | Default        | Meaning                                     |
|------------------------------|----------------|---------------------------------------------|
| `WEBMENTION_ALLOWED_DOMAINS` | `["example.org"]` | JSON array of hostnames accepted as targets |
| `WEBMENTION_DATA_DIR`        | `./data`       | Storage directory (see nginx note below)    |
| `WEBMENTION_RATE_LIMIT`      | `20`           | Requests per IP per window                  |
| `WEBMENTION_RATE_WINDOW`     | `3600`         | Window length in seconds                    |
| `WEBMENTION_HONEYPOT_FIELD`  | `url2`         | Honeypot field name (`''` disables)         |
| `WEBMENTION_ALLOW_PRIVATE`   | off            | Allow private/reserved source IPs (testing only!) |
| `WEBMENTION_ARCHIVE`         | off            | `'1'` enables the optional Internet Archive save (see below) |
| `WEBMENTION_ARCHIVE_URL`     | `https://web.archive.org/save/` | Base URL of the save endpoint (stub-able for tests) |
| `WEBMENTION_ARCHIVE_ACCESS_KEY` | unset       | SPN2 API access key (optional)              |
| `WEBMENTION_ARCHIVE_SECRET_KEY` | unset       | SPN2 API secret key (optional)              |
| `WEBMENTION_ARCHIVE_TIMEOUT` | `15`           | Seconds before the archive request gives up |

If your form embeds the endpoint directly, carry the honeypot field as
a hidden input named `url2` and leave it empty.

## Reachability and archiving

Before a mention is added, the source URL is fetched and must answer
with **HTTP 200 after redirects** - dead pages, `4xx`/`5xx` responses
and redirects that never end on a 200 are rejected (HTTP 400, the
mention is not stored). This applies to webmention and pingback
requests alike.

After a mention was stored, the service can send the source URL to
the Internet Archive so the cited content survives site changes. This
is **optional, off by default** (set `WEBMENTION_ARCHIVE=1`), runs
after the response was already released to the client (`fastcgi_finish_request`
on FPM) and is **allowed to fail**: transport errors, rate limits and
HTTP errors are only written to the server error log, never to the
mention outcome. Two modes:

- With both SPN2 keys set, a `POST` to the save API with
  `Authorization: LOW <access>:<secret>` creates a save job (no
  polling - one cheap request).
- Without keys, an anonymous `GET` on `<URL of the save endpoint>/<source>`
  is issued. Anonymous saves are subject to archive.org IP rate
  limiting, so credentialed mode is preferred for busy endpoints.

The keys are optional - archiving runs without them. When exactly one
of the two keys is set (half-configured credentials), the service logs
a warning and keeps using the anonymous fallback.

## Local testing

The easy way is the bundled integration test, which starts two PHP
built-in servers (source site and endpoint) and runs 25 checks
(acceptance, rejection, backlink verification, reachability gate,
honeypot, archiving modes, rate limit, XML-RPC fault codes, stored
content):

```
./scripts/webmention/test-endpoint.sh
```

# 2. Deploying to the web host

The host needs PHP >= 8 (ideally with curl) and HTTPS. Apache hosts
get `data/.htaccess` deployed automatically; on nginx give the data
directory no HTTP exposure either by pointing `WEBMENTION_DATA_DIR`
outside the document root or by adding a location block:

```nginx
location ^~ /webmentions/data/ {
    deny all;
}
```

Deployment (rsync over SSH, all paths configured via environment
variables):

```
export DEPLOY_SERVER=webhost.example.org   # or set in the workflow secrets
export DEPLOY_USER=deploy
export DEPLOY_PATH=/home/deploy            # absolute base dir, no trailing
                                           # slash - the service lives in the
                                           # fixed 'services/webmentions' subdir
export DEPLOY_PASS=…                       # password auth via sshpass;
                                           # unset = local ssh agent/key
./scripts/webmention/deploy.sh [--dry-run]
```

The connection usage is defined **exactly once** in
`scripts/webmention/host.sh`: the four variables above are the only
ones it understands (there is no port or host-key variable - the
connection always uses port 22, host keys are collected with
`ssh-keyscan`). `deploy.sh` and the data harvest behind the workflow
(see below) go through the identical connection. Only application
files are synchronized - the collected `data/` on the host is
protected from `rsync --delete` (only the tracked `data/.htaccess` is
kept in place). Use `--dry-run` to preview. Point the site's endpoint
parameter at the deployed `endpoint.php`.

# 3. Deploying and collecting - two workflows, one connection

Two workflows handle the two directions over the same deployment
connection:

- `.github/workflows/webmentions-deploy.yaml` - deploy on commits, no
  schedule. Runs on push to `main` (`services/webmentions/**`,
  `scripts/webmention/**`, the workflow file itself) and on manual
  *workflow_dispatch*:
  - job `deploy`: variable check + connection test via `host.sh`,
    `php -l` on every service PHP file, the full `test-endpoint.sh`
    suite, the rsync deployment, and the post-deploy check of the
    endpoint file layout over the same connection
  - job `harvest` (needs `deploy`, calls the reusable harvest
    workflow below): chain a collection run onto the fresh deployment
- `.github/workflows/webmentions-harvest.yaml` - one reusable harvest
  pipeline, running on the hourly cron, on manual *workflow_dispatch*,
  and on `workflow_call` from the deploy workflow:
  1. harvest the host's `data/` through the same connection
     (`scripts/webmention/collect.sh`)
  2. `scripts/webmention/lint.py` validates and merges the entries
  3. The result is committed straight to `main`
     (`$WEBMENTIONS_DATA_DIR`/`mentions.json`, default
     `data/webmentions`), commits carry `[skip ci]` and only happen
     when something changed

| Trigger                        | deploy | harvest |
|--------------------------------|--------|---------|
| commit (`push` to `main`)       | yes    | chained |
| hourly cron (`schedule`)        | no     | yes     |
| dispatch of the deploy workflow | yes    | chained |
| dispatch of the harvest workflow| no     | yes     |

Required **repository Actions secrets** (the deployment connection,
used by both jobs):

| Secret             | Meaning                                     |
|--------------------|---------------------------------------------|
| `DEPLOY_SERVER`    | web host hostname                           |
| `DEPLOY_USER`      | SSH user                                    |
| `DEPLOY_PATH`      | absolute base directory on the host - the service lives in the fixed subdirectory `services/webmentions` |
| `DEPLOY_PASS`      | SSH password (sshpass); without a private SSH key |

The former `WEBMENTION_SSH_KEY` private-key setup and the
`WEBMENTION_HOST/USER/PATH/PORT` variables are gone - the credential
is the deployment password, the host key is collected fresh by
`ssh-keyscan` per run.

## lint.py

The linter is the only quality gate - the web host may accumulate
truncated or outdated files, and the pipeline must not choke on them.
It drops: unparsable JSON files, documents without a valid `target`,
entries missing `source`/`received`, malformed URLs, unparsable
timestamps, duplicates (same source: newest wins), and content that
exceeds the length caps. It merges everything into `mentions.json`
grouped by target, keyed in several normalized forms (lowercase scheme
and host, with and without trailing slash) so the templates can match
page permalinks without URL parsing. Structural checks only - no HTTP
verification of sources (entries stay as they arrived; a later,
verified re-ping replaces them).

Run it manually against any directory of store files:

```
python3 scripts/webmention/lint.py <raw-dir> <output.json>
```

# 4. Getting mentions into a Hugo build

No fetch step, no HTTP, no SSH at build time: the collected data is an
ordinary file on the `main` branch
(`$WEBMENTIONS_DATA_DIR`/`mentions.json`, default `data/webmentions`,
see the workflow above). Hugo mounts it as build data with the lookup
path `data → webmentions → mentions`:

- the list partial reads `hugo.Data.webmentions.mentions.mentions` (a
  map from target URL to entries; `data/webmentions/mentions.json` on
  disk)
- pages are matched against the normalized key variants written by
  lint.py, so `canonifyURLs` path prefixes and trailing slashes work
  without further configuration

Because the data lives in the site repository, every data commit can
rebuild the site on the next push-triggered run; hourly freshness
comes from the workflow's own commit cadence.

Note for sites with an `[module.mounts]` section in their config:
explicit mounts replace Hugo's implicit defaults - keep the site's
data directory mounted (`source = 'data'`, `target = 'data'`),
otherwise `data/webmentions/` is silently ignored. The example site's
`hugo.toml` shows the pattern.

# 5. Site configuration

```toml
[params.webmentions]
  endpoint = 'https://webhost.example.org/webmentions/endpoint.php'
  advertisePingback = true
```

With `endpoint` set:

- every page advertises the endpoints in the document head
  (`<link rel="webmention">`, plus `<link rel="pingback">` when
  `advertisePingback` is true) - see
  `layouts/_partials/html/head/webmention.html`
- received mentions render below the current page's content via
  `layouts/_partials/webmentions/list.html`. Include it from your
  layouts or place it with the `{{< webmentions >}}` shortcode; it
  only renders when entries exist for that page

## Head advertisement with availability check

The head partial verifies the endpoint URL once per build before
emitting the `<link>` elements (the partial is cached, so the check
runs exactly one HTTP GET per build). Since the collector answers GET
with 405, any HTTP status proves the endpoint is alive - only
transport failures (or a security policy denial) lead to a build
warning and **no advertisement in that build**:

```
WARN [partials/html/head/webmention.html] Webmention endpoint … is not
reachable (dial tcp …: connection refused). Not advertising the
endpoints in the document head of this build.
```

Note that Hugo's own security policy decides whether the check may
leave the build at all. The default `security.http.urls` policy allows
normal domain URLs but denies URLs starting with an IP address,
`localhost` URLs and URLs with credentials. Endpoints on such hosts
need a whitelist entry in the **site** config:

```toml
[security.http]
  # Only needed when the collector's host matches one of Hugo's
  # default denials (IP address, localhost, credentials) - the list
  # REPLACES the default policy, so include the default allowances:
  urls = ['(?i)^https?://[a-z0-9]', '^(?i)https?://127\.0\.0\.1']
```

A policy denial is reported with its own warning pointing here. The
check is display-only: failing it never fails the build.

The data lookup uses the nesting produced by the
`data/webmentions/mentions.json` path:
`hugo.Data.webmentions.mentions.mentions` - a map from target URL to
entries. Pages are matched against the normalized key variants written
by lint.py, so `canonifyURLs` path prefixes and trailing slashes work
without further configuration.

# 6. Operations

- **Removing spam:** delete the offending entry/host file on the web
  host and trigger the workflow (or wait for the next scheduled run) -
  the data directory reconciles itself; for a quick fix, remove the
  entry from `data/webmentions/mentions.json` in the site repository
  as well.
- **Forcing a run:** Actions -> "Deploy webmentions" (deploys first,
  then chain-harvests) or "Harvest webmentions" (harvest only) ->
  `workflow_dispatch`.
- **Rate limit hit accidentally:** raise `WEBMENTION_RATE_LIMIT` via
  the environment variable, or clear `data/.ratelimit/` on the host.
- **Broken storage:** the store is a plain directory; files are only
  ever replaced atomically. Worst case: delete a file, the next valid
  mention rebuilds it.

# 7. Tests

| Script                                     | Covers                        |
|--------------------------------------------|-------------------------------|
| `scripts/webmention/test-endpoint.sh`       | Endpoint behaviour, storage, reachability gate, archiving, rate limit (25 checks) |
| `scripts/webmention/test-lint.sh`           | lint.py: dropping broken data, dedup, grouping, key variants |
| `hugo --themesDir ../.. --environment tests` (in `exampleSite/`) | Head advertisement and list rendering with demo data |
