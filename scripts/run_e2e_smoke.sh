#!/usr/bin/env bash
set -euo pipefail

API="http://localhost:5000"
API_KEY="${API_KEY:-changeme}"

echo "==> Smoke: /health"
curl -sf "${API}/health" | grep -q "OK"

echo "==> Smoke: /stats returns distribution"
DIST=$(curl -sf "${API}/stats" | python3 -c "import sys,json; d=json.load(sys.stdin); print(sum(d['distribution'].values()))")
[ "$DIST" -gt 0 ] || { echo "FAIL: /stats distribution empty"; exit 1; }

echo "==> Smoke: /sentiments returns items"
COUNT=$(curl -sf "${API}/sentiments?limit=1" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['items']))")
[ "$COUNT" -gt 0 ] || { echo "FAIL: /sentiments returned no items"; exit 1; }

echo "==> Smoke: /predict classifies text"
PRED=$(curl -sf -X POST "${API}/predict" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d '{"text":"excellent product very happy"}' | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print(d['prediction'])")
[[ "$PRED" =~ ^(positivo|negativo|neutral)$ ]] || { echo "FAIL: /predict returned invalid label: ${PRED}"; exit 1; }

echo "==> All smoke tests passed. prediction=${PRED}, mongo_count=${DIST}"
