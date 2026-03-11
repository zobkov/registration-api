#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8000}"
EMAIL="${2:-smoke.$(date +%s)@example.com}"

echo "[smoke] Health check: ${BASE_URL}/health"
curl --silent --show-error --fail \
  "${BASE_URL}/health" | cat

echo
echo "[smoke] POST ${BASE_URL}/api/v1/registrations (email=${EMAIL})"
curl --silent --show-error \
  -X POST "${BASE_URL}/api/v1/registrations" \
  -H "Content-Type: application/json" \
  -d "{
    \"fullName\": \"Smoke User\",
    \"status\": \"participant\",
    \"transport\": \"Общественный транспорт\",
    \"carNumber\": null,
    \"passport\": \"4010123456\",
    \"adult18\": \"Да\",
    \"region\": \"Moscow\",
    \"participantStatus\": \"Высшее образование\",
    \"email\": \"${EMAIL}\",
    \"track\": \"track_1\"
  }" | cat

echo
