# Registration API

FastAPI service for forum registrations backed by PostgreSQL.

## Run

```bash
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

## Health Check

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## Smoke POST Check (curl)

```bash
./scripts/smoke_post_registration.sh
```

Optional arguments:

```bash
./scripts/smoke_post_registration.sh http://127.0.0.1:8000 custom.email@example.com
```
