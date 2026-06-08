# ContentPilot Architecture

## Monorepo Structure

```
contentpilot/
├── .github/
│   └── workflows/
│       └── deploy.yml                  # CI/CD placeholder (optional)
├── deploy/                             # All deployment infrastructure
│   ├── sites.yml                       # Site configuration (hosts, ports, compose files)
│   ├── nginx/
│   │   └── sites/
│   │       └── _template.conf.tpl      # Nginx reverse-proxy template
│   ├── docker/                         # Dockerfiles and build configs
│   │   ├── base.Dockerfile
│   │   └── .dockerignore
│   ├── compose/                        # Docker Compose configurations
│   │   ├── docker-compose.yml          # Main application compose
│   │   └── docker-compose.mietvertrag.yml
│   ├── cron/                           # Cron job definitions
│   │   └── crontabs/
│   │       ├── contentpilot
│   │       ├── daily_news.cron
│   │       └── social_tips.cron
│   ├── scripts/                        # Deployment and utility scripts
│   │   ├── deploy.sh                   # Main deployment handler (Git webhook target)
│   │   ├── nginx-sync.sh               # Generates nginx vhosts from sites.yml
│   │   ├── ssl-issue.sh                # Certbot wrapper for SSL provisioning
│   │   ├── webhook-server.sh           # Python webhook listener (systemd service)
│   │   ├── up.sh                       # Start all Docker services
│   │   ├── down.sh                     # Stop all Docker services
│   │   └── check-sites.sh              # Health check for deployed sites
│   └── backups/                        # Backup storage
├── frontend/
│   ├── wordpress/                      # WordPress plugins and theme
│   │   └── wp-content/
│   ├── mietvertrag/                    # Mietvertrag/Hermes Agent frontend (Node.js)
│   │   ├── src/
│   │   ├── public/
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   ├── package.json
│   │   └── vite.config.js
│   └── dashboard/                      # Reserved for future admin dashboard
├── modules/                            # Backend Python modules
│   ├── article_publisher/
│   ├── auto_publisher/
│   ├── daily_news/
│   ├── deals_engine/
│   ├── social_tips/
│   └── social_video/
├── data/                               # Data directories (gitignored)
│   ├── db/                             # Database files
│   ├── cache/                          # Application cache
│   ├── logs/                           # Application logs
│   ├── backups/                        # Database backups
│   ├── media/                          # User uploaded media
│   ├── runtime/                        # Runtime state files
│   └── locks/                          # Lock files
├── scripts/                            # Legacy scripts (kept for compatibility)
├── requirements/                       # Python dependencies
├── docs/                               # Documentation
├── .env.example                        # Environment variables template
├── .gitignore
├── README.md
└── docker-compose.yml                  # (Legacy, if present; use deploy/compose/)

```

## Deployment Pipeline

### Architecture Overview

```
GitHub Push Event
        │
        └─→ VPS Webhook Server (Port 9000)
             │
             ├─ Validates X-Hub-Signature-256
             └─ Executes: deploy/scripts/deploy.sh
                │
                ├─→ Git pull origin main
                ├─→ Check for new domains → SSL provisioning (ssl-issue.sh)
                ├─→ Sync nginx vhosts (nginx-sync.sh)
                ├─→ Detect changed services → docker compose up --build -d
                └─→ Send Telegram notification
```

### sites.yml Configuration

The `deploy/sites.yml` file is the source of truth for all deployed sites:

```yaml
sites:
  - host: mycontentpilot.de
    port: 8080
    compose: docker-compose.yml
    service: wordpress
  - host: mietvertrag.mycontentpilot.de
    port: 3010
    compose: docker-compose.mietvertrag.yml
    service: mietvertrag
```

**Fields:**
- `host`: Domain name
- `port`: Local port where service listens
- `compose`: Docker Compose file in `deploy/compose/`
- `service`: Service name in the compose file

### Nginx Reverse Proxy

The `nginx-sync.sh` script:
1. Parses `sites.yml`
2. Generates nginx server blocks from `_template.conf.tpl`
3. Writes vhost files to `/etc/nginx/sites-available/$HOST.conf`
4. Creates symlinks in `/etc/nginx/sites-enabled/`
5. Tests and reloads nginx

**Template variables:**
- `${HOST}`: Domain name from sites.yml
- `${PORT}`: Local port from sites.yml

### SSL Certificate Management

The `ssl-issue.sh` script:
1. Accepts a domain as argument
2. Checks if `/etc/letsencrypt/live/$DOMAIN` exists
3. If not, runs: `certbot --nginx -d $DOMAIN ...`
4. Logs to `/var/log/contentpilot/ssl-issue.log`

Called automatically by `deploy.sh` for new domains detected in `sites.yml`.

### Main Deployment Handler (deploy.sh)

The primary deployment script performs:
1. **Git sync**: `git pull origin main`
2. **Domain detection**: Checks for new hosts in sites.yml vs. existing nginx vhosts
3. **SSL provisioning**: Calls `ssl-issue.sh` for any missing certificates
4. **Nginx sync**: Calls `nginx-sync.sh` to update reverse-proxy configuration
5. **Change detection**: Uses `git diff HEAD~1 --name-only` to detect which services changed
6. **Service rebuild**: Runs `docker compose up --build -d` for affected compose files
7. **Notifications**: Sends Telegram message with commit message
8. **Logging**: All steps logged to `/var/log/contentpilot/deploy.log`

### Webhook Server

The `webhook-server.sh` runs as a systemd service (contentpilot-webhook):
- Listens on port 9000
- Validates GitHub webhook signature using `X-Hub-Signature-256` header
- Spawns `deploy.sh` in background on valid POST to `/deploy`
- Logs to `/var/log/contentpilot/webhook.log`

## Environment Configuration

All sensitive configuration is loaded from `.env` (gitignored template: `.env.example`).

**Required variables:**
- `WEBHOOK_SECRET`: Must match GitHub webhook secret
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`: For deployment notifications
- `WP_DB_PASSWORD`, `DB_*`: Database credentials
- `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`: AI service tokens

## Service Startup

### Local Development
```bash
bash deploy/scripts/up.sh      # Start all services
bash deploy/scripts/down.sh    # Stop all services
```

### Production Deployment
Services are deployed via `deploy.sh`, which:
1. Detects changes in git history
2. Rebuilds only affected services
3. Restarts via `docker compose up --build -d`

## Health Checks

```bash
bash deploy/scripts/check-sites.sh
```

Curls each site in `sites.yml` and reports health status.

## Data Management

### Ignored Directories
All data directories are gitignored:
- `data/db/*`: Database files (`.gitkeep` tracked)
- `data/cache/*`: Application cache
- `data/logs/*`: Application logs
- `data/backups/*`: Database backups
- `data/media/*`: User uploads
- `data/runtime/*`: Runtime state
- `data/locks/*`: Lock files

## Logging

### Deployment Logs
- `/var/log/contentpilot/deploy.log` - Main deployment logs
- `/var/log/contentpilot/webhook.log` - Webhook server logs
- `/var/log/contentpilot/ssl-issue.log` - SSL certificate issuance logs

### Application Logs
- `data/logs/` - Application runtime logs

## Future Enhancements

- GitHub Actions CI/CD integration (see `.github/workflows/deploy.yml`)
- Automated testing in CI pipeline
- Database backup automation
- Enhanced monitoring and alerting
- Blue-green deployment strategy
- Rollback capabilities
