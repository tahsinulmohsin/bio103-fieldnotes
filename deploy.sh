#!/usr/bin/env bash
set -euo pipefail

REMOTE_HOST="192.168.31.10"
REMOTE_USER="tahsinulmohsin"
REMOTE_DIR="/home/tahsinulmohsin/bio103"
SSH_KEY="$HOME/.ssh/id_ed25519"
PORT="3103"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================================="
echo "   BIO103 Fieldnotes — Homelab Deployment via SSH         "
echo "=========================================================="

echo "==> [1/4] Ensuring remote directory exists on ${REMOTE_HOST}..."
ssh -o BatchMode=yes -o ConnectTimeout=5 -i "$SSH_KEY" "${REMOTE_USER}@${REMOTE_HOST}" "mkdir -p '${REMOTE_DIR}'"

echo "==> [2/4] Syncing project files to ${REMOTE_HOST}:${REMOTE_DIR} via rsync..."
rsync -avz --delete \
  --exclude "node_modules" \
  --exclude ".next" \
  --exclude ".git" \
  --exclude "scratch" \
  --exclude "*.log" \
  --exclude ".DS_Store" \
  --exclude "playwright-report" \
  --exclude "test-results" \
  --exclude ".vercel" \
  -e "ssh -i $SSH_KEY" \
  "$SCRIPT_DIR/" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/"

echo "==> [3/4] Building and launching Docker container on remote host..."
ssh -o BatchMode=yes -o ConnectTimeout=10 -i "$SSH_KEY" "${REMOTE_USER}@${REMOTE_HOST}" \
  "cd '${REMOTE_DIR}' && docker compose down || true && docker compose up -d --build"

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
  ssh -i "$SSH_KEY" "${REMOTE_USER}@${REMOTE_HOST}" "cd '${REMOTE_DIR}' && docker compose logs --tail=40"
  exit 1
fi

echo "=========================================================="
echo "🎉 SUCCESS: BIO103 Fieldnotes is deployed on your homelab!"
echo "   Container:  bio103-fieldnotes-app"
echo "   LAN URL:    http://${REMOTE_HOST}:${PORT}/"
echo "   Health URL: http://${REMOTE_HOST}:${PORT}/api/health"
echo "=========================================================="
