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

## Production via Docker (simple)

This flow runs only the API in Docker and uses an external PostgreSQL instance.

1. Prepare environment file:

```bash
cp .env.prod.example .env.prod
```

2. Fill real PostgreSQL values in `.env.prod`:

```bash
db_user=...
db_pass=...
db_name=...
db_host=...
db_port=5432
```

3. Build and run API:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

4. Verify health:

```bash
curl http://127.0.0.1:8000/health
```

5. One-command redeploy:

```bash
chmod +x deploy.sh
./deploy.sh
```

Notes:
- `deploy.sh` executes `alembic upgrade head` before starting the API service.
- Current setup is HTTP only (no TLS/HTTPS in this stage).

## Production systemd (hardened)

1. Create a dedicated system user:

```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin registration-api
```

2. Deploy app files to /opt and set ownership:

```bash
sudo mkdir -p /opt/registration-api
sudo rsync -a --delete ./ /opt/registration-api/
sudo chown -R registration-api:registration-api /opt/registration-api
```

3. Store environment variables outside app directory:

```bash
sudo mkdir -p /etc/registration-api
sudo cp /opt/registration-api/.env /etc/registration-api/registration-api.env
sudo chown root:registration-api /etc/registration-api/registration-api.env
sudo chmod 640 /etc/registration-api/registration-api.env
```

4. Install and start service:

```bash
sudo cp /opt/registration-api/registration-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now registration-api
sudo systemctl status registration-api
```

5. Verify via local health-check:

```bash
curl http://127.0.0.1:8000/health
```

## Nginx reverse proxy (external access)

1. Install Nginx and create ACME directory:

```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
sudo mkdir -p /var/www/certbot
```

2. Copy and enable bootstrap HTTP config from [nginx/registration-api.conf](nginx/registration-api.conf):

```bash
sudo cp /opt/registration-api/nginx/registration-api.conf /etc/nginx/sites-available/registration-api
sudo ln -sf /etc/nginx/sites-available/registration-api /etc/nginx/sites-enabled/registration-api
sudo nginx -t
sudo systemctl restart nginx
```

3. Ensure DNS points your domain to the server IP, then issue TLS certificate:

```bash
sudo certbot --nginx -d zobkov-server.ru -d www.zobkov-server.ru
```

4. Verify HTTPS from outside server:

```bash
curl -i https://zobkov-server.ru/health
```

If certificate is not issued yet, test HTTP first:

```bash
curl -i http://zobkov-server.ru/health
```

If nginx cannot start because port 80 is busy:

```bash
sudo ss -ltnp | grep :80
sudo lsof -iTCP:80 -sTCP:LISTEN -n -P
```
