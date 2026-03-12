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

2. Copy and enable config from [nginx/registration-api.conf](nginx/registration-api.conf):

```bash
sudo cp /opt/registration-api/nginx/registration-api.conf /etc/nginx/sites-available/registration-api
sudo ln -sf /etc/nginx/sites-available/registration-api /etc/nginx/sites-enabled/registration-api
sudo nginx -t
sudo systemctl reload nginx
```

3. Ensure DNS points your domain to the server IP, then issue TLS certificate:

```bash
sudo certbot --nginx -d forum-cbc.ru -d www.forum-cbc.ru
```

4. Verify from outside server:

```bash
curl -i https://forum-cbc.ru/health
```

If certificate is not issued yet, test HTTP first:

```bash
curl -i http://forum-cbc.ru/health
```
