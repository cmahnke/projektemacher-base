#!/usr/bin/env bash
#
# Deploys the webmention/pingback endpoint ('services/webmentions/')
# to the deployment host. Every connection detail is defined once in
# 'host.sh' (DEPLOY_SERVER/DEPLOY_USER/DEPLOY_PATH/DEPLOY_PASS) - this
# script only orchestrates the rsync.
#
# The collected data ('data/') on the host is preserved - only
# application files are synchronized. The tracked 'data/.htaccess' is
# kept in place, everything else inside 'data/' stays untouched by
# '--delete'.
#
# Options:
#   --dry-run   run rsync with --dry-run, nothing is written
#
# See 'services/webmentions/README.md' for the full process.

set -e -o pipefail

SCRIPT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd)"
SOURCE="$(cd "$SCRIPT_DIR/../../services/webmentions" && pwd)"
# The service directory on the host - DEPLOY_PATH +
# 'projektemacher.org/services/webmentions' (single place: 'host.sh path').
SERVICE_PATH="$("$SCRIPT_DIR/host.sh" path)"
TARGET="$DEPLOY_USER@$DEPLOY_SERVER:$SERVICE_PATH"

DRY_RUN=0
for ARG in "$@" ; do
  case "$ARG" in
    --dry-run) DRY_RUN=1 ;;
    *)
      echo "Usage: deploy.sh [--dry-run]" >&2
      exit 2
      ;;
  esac
done

RSYNC_ARGS=(-avz --delete
  --filter='+ /data/'
  --filter='+ /data/.htaccess'
  --filter='- /data/*'
  --exclude='.DS_Store'
  --exclude='.git*'
  # The host user lacks chown/chgrp rights - synchronize content only,
  # never user, group or modification time (rsync exit code 23).
  --no-owner --no-group --no-times
)
if [ "$DRY_RUN" = "1" ] ; then
  RSYNC_ARGS+=(--dry-run)
fi

# Make sure the storage directory exists and carries the deny rules.
"$SCRIPT_DIR/host.sh" exec "mkdir -p '$SERVICE_PATH/data'"

"$SCRIPT_DIR/host.sh" rsync "${RSYNC_ARGS[@]}" "$SOURCE/" "$TARGET/"

echo "Deployed webmention endpoint to $DEPLOY_SERVER:$SERVICE_PATH"
echo "Hint: the theme's default 'hugo.toml' points at static.projektemacher.org;"
echo "sites can override with:"
echo "  [params.webmentions]"
echo "    endpoint = 'https://<host>/<path>/webmention.php'"
