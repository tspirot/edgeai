#!/usr/bin/env bash
# Повуци најновији main, изгради сајт, објави у public_html.
# Позива га webhook.php, или се покреће ручно на серверу.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# учитај REPO_DIR / PUBLIC_HTML из .env ако постоји
if [ -f "$HERE/.env" ]; then set -a; . "$HERE/.env"; set +a; fi

REPO_DIR="${REPO_DIR:-$HOME/edgeai}"
PUBLIC_HTML="${PUBLIC_HTML:-$HOME/domains/edgeai.tsp.edu.rs/public_html}"

echo "[deploy] $(date -Is)  repo=$REPO_DIR  ->  $PUBLIC_HTML"

cd "$REPO_DIR"
git fetch --quiet origin main
git reset --hard origin/main

cd "$REPO_DIR/web"
npm ci --no-audit --no-fund
npm run build

mkdir -p "$PUBLIC_HTML"
rsync -a --delete "$REPO_DIR/web/dist/" "$PUBLIC_HTML/"

echo "[deploy] готово: $(git -C "$REPO_DIR" rev-parse --short HEAD)"
