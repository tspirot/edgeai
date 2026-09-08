#!/bin/bash
# Провери има ли нових комитова на main и, ако има, покрени deploy.
# Ради без webhook-а и без Apache proxy-ја — позива се из user crontab-а
# сваких пар минута. Алтернатива за webhook-server.js.
set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/edgeai}"
BRANCH="${DEPLOY_BRANCH:-main}"

cd "$REPO_DIR"
git fetch -q origin "$BRANCH"

LOCAL="$(git rev-parse HEAD)"
REMOTE="$(git rev-parse "origin/$BRANCH")"
if [ "$LOCAL" = "$REMOTE" ]; then
  exit 0
fi

echo "[poll $(date '+%Y-%m-%d %H:%M:%S')] нова верзија ${REMOTE:0:7} — деплојујем"
exec bash "$REPO_DIR/deploy/deploy.sh"
