#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"
HEALTH_URL="http://127.0.0.1:8000/health"

if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker is not installed"
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Error: docker compose plugin is not available"
  exit 1
fi

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Error: missing $COMPOSE_FILE"
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: missing $ENV_FILE"
  echo "Hint: copy .env.prod.example to .env.prod and fill real values"
  exit 1
fi

echo "Validating docker compose config..."
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config >/dev/null

echo "Pulling latest code..."
git pull --ff-only

echo "Building and starting containers..."
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --build

echo "Waiting for API health..."
if command -v curl >/dev/null 2>&1; then
  for _ in {1..30}; do
    if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
      echo "Deploy successful: $HEALTH_URL"
      exit 0
    fi
    sleep 2
  done
else
  echo "curl is not available, checking container health status"
  for _ in {1..30}; do
    container_id=$(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps -q api)
    if [[ -n "$container_id" ]]; then
      status=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container_id")
      if [[ "$status" == "healthy" || "$status" == "running" ]]; then
        echo "Deploy successful: api container is $status"
        exit 0
      fi
    fi
    sleep 2
  done
fi

echo "Health check failed after deploy. Showing last logs:"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs --tail=200 api
exit 1
