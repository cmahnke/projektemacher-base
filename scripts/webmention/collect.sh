#!/usr/bin/env bash
#
# Harvests the collected mentions ('data/') from the deployment host
# into a local directory - over the single deployment connection
# ('host.sh', DEPLOY_SERVER/DEPLOY_USER/DEPLOY_PATH/DEPLOY_PASS). This
# is the first half of the collection pipeline; 'lint.py' and the
# branch commit run afterwards ('.github/workflows/webmentions-harvest.yaml').
#
# Usage: collect.sh <local-destination-directory>
#
# See 'services/webmentions/README.md' for the full process.

set -e -o pipefail

if [ "$#" -ne 1 ] || [ -z "$1" ] ; then
  echo "Usage: collect.sh <local-destination-directory>" >&2
  exit 2
fi
DEST="$1"

SCRIPT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd)"

mkdir -p "$DEST"
# The service directory on the host - DEPLOY_PATH + 'services/webmentions'
# (single place: 'host.sh path').
SERVICE_PATH="$("$SCRIPT_DIR/host.sh" path)"
"$SCRIPT_DIR/host.sh" rsync -a --delete \
  "$DEPLOY_USER@$DEPLOY_SERVER:$SERVICE_PATH/data/" \
  "$DEST/"
echo "Harvested webmention data into $DEST"
