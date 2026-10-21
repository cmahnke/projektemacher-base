#!/usr/bin/env bash
#
# The single connection to the deployment host - the only place that
# knows how to reach it.
#
# Both the service deployment ('deploy.sh') and the data harvest
# ('collect.sh') route every ssh/rsync through this script, using the
# same variables as the deployment workflows:
#
#   DEPLOY_SERVER  hostname of the deployment host (required)
#   DEPLOY_USER    ssh user on the host (required)
#   DEPLOY_PATH    absolute base directory on the host (required) - the
#                  webmention service lives in the fixed subdirectory
#                  'projektemacher.org/services/webmentions'
#                  (see 'host.sh path')
#   DEPLOY_PASS    ssh password; when unset the local ssh agent/key
#                  setup is used (for interactive runs)
#
# There is deliberately no other transport to the host - the
# webmention service has no read API, its data is harvested over the
# same connection the service is deployed with. The host key is
# collected with ssh-keyscan once per session (trust on first use),
# the connection always runs on port 22.
#
# Subcommands:
#   host.sh exec '<command>'   run a command on the host
#   host.sh rsync <args ...>   run rsync over the connection, the
#                              destination is expected as
#                              '$DEPLOY_USER@$DEPLOY_SERVER:<service path>...'
#   host.sh path               print the service directory on the host
#                              ($DEPLOY_PATH + 'projektemacher.org/services/webmentions',
#                              the fixed layout used by deploy + harvest)
#
# See 'services/webmentions/README.md' for the full process.

set -e -o pipefail

# The service directory on the host is a fixed subdirectory of
# DEPLOY_PATH - the subpath carries its own leading slash.
SERVICE_SUBPATH='/projektemacher.org/services/webmentions'

for VAR in DEPLOY_SERVER DEPLOY_USER DEPLOY_PATH ; do
  if [ -z "${!VAR:-}" ] ; then
    echo "Error: $VAR is not set" >&2
    exit 1
  fi
done

if [ -n "${DEPLOY_PASS:-}" ] && ! command -v sshpass >/dev/null 2>&1 ; then
  echo "Error: DEPLOY_PASS is set but sshpass is not installed" >&2
  exit 1
fi

# Prepares the SSH environment - trust on first use: collect the host
# key once per session. A failed keyscan is tolerated here, the
# following connection attempt reports the real problem.
ensure_connection() {
  mkdir -p "$HOME/.ssh"
  chmod 700 "$HOME/.ssh"
  touch "$HOME/.ssh/known_hosts"
  chmod 600 "$HOME/.ssh/known_hosts"
  if ! ssh-keygen -F "$DEPLOY_SERVER" -f "$HOME/.ssh/known_hosts" >/dev/null 2>&1 ; then
    ssh-keyscan -T 10 -H "$DEPLOY_SERVER" >> "$HOME/.ssh/known_hosts" 2>/dev/null || true
  fi
}

# Runs a command on the host over the deployment connection.
exec_remote() {
  if [ -n "${DEPLOY_PASS:-}" ] ; then
    SSHPASS="$DEPLOY_PASS" sshpass -e ssh "$DEPLOY_USER@$DEPLOY_SERVER" "$@"
  else
    ssh "$DEPLOY_USER@$DEPLOY_SERVER" "$@"
  fi
}

# Runs rsync over the deployment connection.
exec_rsync() {
  if [ -n "${DEPLOY_PASS:-}" ] ; then
    SSHPASS="$DEPLOY_PASS" sshpass -e rsync "$@"
  else
    rsync "$@"
  fi
}

case "${1:-}" in
  exec)
    shift
    ensure_connection
    exec_remote "$@"
    ;;
  rsync)
    shift
    ensure_connection
    exec_rsync "$@"
    ;;
  path)
    echo "${DEPLOY_PATH%/}$SERVICE_SUBPATH"
    ;;
  *)
    echo "Usage: host.sh exec '<command>' | host.sh rsync <rsync args> | host.sh path" >&2
    exit 2
    ;;
esac
