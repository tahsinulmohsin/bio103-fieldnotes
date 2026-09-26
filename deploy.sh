#!/usr/bin/env bash
# Deploy to the production server over SSH: sync the project, build the image there,
# keep the running image as bio103-fieldnotes:previous for rollback, then wait for /api/health.
# Server settings come from .deploy.env (not committed); copy .deploy.env.example to start.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/.deploy.env" ]; then
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/.deploy.env"
fi

REMOTE_HOST="${DEPLOY_HOST:?Set DEPLOY_HOST in .deploy.env (see .deploy.env.example)}"
REMOTE_USER="${DEPLOY_USER:?Set DEPLOY_USER in .deploy.env}"
REMOTE_DIR="${DEPLOY_DIR:-/home/${REMOTE_USER}/bio103}"
SSH_KEY="${DEPLOY_SSH_KEY:-$HOME/.ssh/id_ed25519}"
PORT="${DEPLOY_PORT:-3103}"
PUBLIC_URL="${PUBLIC_URL:-https://fieldnotes.tahsinulmohsin.me}"

# DEPLOY_PROXY_NETWORK=1 also joins the app to the shared bio103-ingress network, which the
# Nginx Proxy Manager route in deployment/ uses to reach it (see deployment/README.md).
COMPOSE_FILES="compose.yaml"
PREPARE=""
if [ "${DEPLOY_PROXY_NETWORK:-0}" = "1" ]; then
  COMPOSE_FILES="compose.yaml:deployment/compose.proxy.yaml"
  PREPARE="(docker network inspect bio103-ingress >/dev/null 2>&1 || docker network create bio103-ingress >/dev/null) && "
fi

echo "=========================================================="
echo "   BIO103 Fieldnotes: production deployment via SSH"
echo "=========================================================="

echo "==> [1/4] Ensuring remote directory exists on ${REMOTE_HOST}..."
ssh -o BatchMode=yes -o ConnectTimeout=5 -i "$SSH_KEY" "${REMOTE_USER}@${REMOTE_HOST}" "mkdir -p '${REMOTE_DIR}'"

echo "==> [2/4] Syncing project files to ${REMOTE_HOST}:${REMOTE_DIR} via rsync..."
rsync -avz --delete \
  --exclude "node_modules" \
  --exclude ".cache" \
  --exclude "__pycache__" \
  --exclude ".next" \
  --exclude ".git" \
  --exclude ".deploy.env" \
  --exclude "deployment/private" \
  --exclude "scratch" \
  --exclude "*.log" \
  --exclude ".DS_Store" \
  --exclude "playwright-report" \
  --exclude "test-results" \
  --exclude ".vercel" \
  --exclude ".impeccable/review" \
  -e "ssh -i $SSH_KEY" \
  "$SCRIPT_DIR/" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/"

echo "==> [3/4] Building and launching the Docker container on the server..."
ssh -o BatchMode=yes -o ConnectTimeout=10 -i "$SSH_KEY" "${REMOTE_USER}@${REMOTE_HOST}" \
  "cd '${REMOTE_DIR}' && export COMPOSE_FILE='${COMPOSE_FILES}' && ${PREPARE}(docker image tag bio103-fieldnotes:latest bio103-fieldnotes:previous 2>/dev/null || true) && docker compose build && docker compose up -d"

echo "==> [4/4] Verifying healthcheck at http://${REMOTE_HOST}:${PORT}/api/health..."
MAX_ATTEMPTS=45
ATTEMPT=0
HEALTHY=false

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://${REMOTE_HOST}:${PORT}/api/health" || true)
  if [ "$HTTP_STATUS" = "200" ]; then
    HEALTHY=true
    break
  fi
  echo "    Waiting for container... (Attempt $((ATTEMPT + 1))/${MAX_ATTEMPTS}, HTTP: ${HTTP_STATUS})"
  sleep 3
  ATTEMPT=$((ATTEMPT + 1))
done

if [ "$HEALTHY" = false ]; then
  echo "❌ ERROR: Container failed to respond with HTTP 200 within timeout."
  echo "==> Recent container logs:"
  ssh -i "$SSH_KEY" "${REMOTE_USER}@${REMOTE_HOST}" "cd '${REMOTE_DIR}' && COMPOSE_FILE='${COMPOSE_FILES}' docker compose logs --tail=40"
  exit 1
fi

echo "=========================================================="
echo "🎉 SUCCESS: BIO103 Fieldnotes is deployed."
echo "   Container:  bio103-fieldnotes-app"
echo "   Origin:     http://${REMOTE_HOST}:${PORT}/api/health"
echo "   Public:     ${PUBLIC_URL}"
echo "   Version:    $(curl -s -m 10 "http://${REMOTE_HOST}:${PORT}/api/health" || true)"
echo "=========================================================="
