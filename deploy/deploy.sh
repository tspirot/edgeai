#!/bin/bash
# =============================================================
# deploy.sh — atomic deploy сајта на edgeai.tsp.edu.rs
# Позива га deploy/webhook-server.js (или се покреће ручно).
#
# Сајт је статички (Vite build). Принцип као код tsp портала:
# backup старог садржаја пре објаве; ако build падне → rollback.
# public_html никад не остаје полупразан.
# =============================================================
set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/edgeai}"
BRANCH="${DEPLOY_BRANCH:-main}"

# document root: из env, иначе аутоматски (Virtualmin: обе варијанте су могуће)
PUBLIC_HTML="${PUBLIC_HTML:-}"
if [ -z "$PUBLIC_HTML" ]; then
  for c in "$HOME/domains/edgeai.tsp.edu.rs/public_html" "$HOME/public_html"; do
    [ -d "$c" ] && PUBLIC_HTML="$c" && break
  done
fi
: "${PUBLIC_HTML:?Постави PUBLIC_HTML (document root поддомена)}"
LOG_FILE="$REPO_DIR/deploy/logs/deploy.log"
BACKUP_DIR="$REPO_DIR/deploy/.public_html_backup"

mkdir -p "$(dirname "$LOG_FILE")"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

git config --global --add safe.directory "$REPO_DIR" 2>/dev/null || true

BUILD_OK=false
cleanup() {
  if [ "$BUILD_OK" = false ] && [ -d "$BACKUP_DIR" ]; then
    log "ROLLBACK: враћам претходни садржај у public_html"
    rsync -a --delete --exclude='.well-known' "$BACKUP_DIR"/ "$PUBLIC_HTML"/ || true
  fi
  rm -rf "$BACKUP_DIR" 2>/dev/null || true
}
trap cleanup EXIT

log "=========================================="
log "Почиње deploy (branch $BRANCH)"

if [ ! -d "$REPO_DIR/.git" ]; then
  log "ГРЕШКА: $REPO_DIR није git репо. Клонирај прво (види deploy/README.md)."
  exit 1
fi

# 1. повуци најновије
cd "$REPO_DIR"
git fetch origin
git reset --hard "origin/$BRANCH"
git clean -fd
log "commit: $(git log -1 --pretty='%h %s (%an)')"

# 2. build (devDeps су потребни)
cd "$REPO_DIR/web"
unset NODE_ENV
log "npm ci..."
npm ci --no-audit --no-fund
log "npm run build..."
npm run build

# 3. backup постојећег public_html
mkdir -p "$PUBLIC_HTML"
rm -rf "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
rsync -a "$PUBLIC_HTML"/ "$BACKUP_DIR"/ 2>/dev/null || true

# 4. објави нови build (.well-known остаје — ACME/Let's Encrypt)
rsync -a --delete --exclude='.well-known' "$REPO_DIR/web/dist"/ "$PUBLIC_HTML"/

BUILD_OK=true
log "Deploy УСПЕШНО завршен → $PUBLIC_HTML"
log "=========================================="
