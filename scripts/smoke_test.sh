#!/usr/bin/env bash
set -euo pipefail

API_URL=${1:-"http://localhost:8000"}

echo "== Health =="
curl -sS "${API_URL}/api/v1/health" | jq . || true
curl -sS "${API_URL}/api/v1/monitoring/health" | jq . || true

echo "\n== Test Chat (demo endpoint) =="
curl -sS -X POST "${API_URL}/api/v1/test-chat" \
  -H 'Content-Type: application/json' \
  -d '{"message":"Give me a brief SWOT for a SaaS startup"}' | jq . || true

echo "\nDone."

