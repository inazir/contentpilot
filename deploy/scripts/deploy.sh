#!/usr/bin/env bash
set -euo pipefail

REPO="/home/deployer/repos/contentpilot"
DEPLOY_DIR="$REPO/deploy"
SITES_FILE="$DEPLOY_DIR/sites.yml"
LOG_DIR="/var/log/contentpilot"
LOG_FILE="$LOG_DIR/deploy.log"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "Starting deployment process..."

cd "$REPO"

# Pull latest changes from git
log "Pulling latest changes from origin/main..."
git pull origin main >> "$LOG_FILE" 2>&1 || {
    log "ERROR: git pull failed"
    exit 1
}

log "Git pull completed successfully"

# Get the latest commit message for notification
COMMIT_MSG=$(git log -1 --format='%s')
log "Latest commit: $COMMIT_MSG"

# Parse sites.yml and check for SSL certificates
log "Checking SSL certificates..."

python3 << 'PYTHON_SCRIPT'
import yaml
import os
import subprocess

SITES_FILE = os.path.join(os.environ['REPO'], 'deploy', 'sites.yml')
SSL_ISSUE_SCRIPT = os.path.join(os.environ['REPO'], 'deploy', 'scripts', 'ssl-issue.sh')

try:
    with open(SITES_FILE, 'r') as f:
        config = yaml.safe_load(f)
except Exception as e:
    print(f"ERROR parsing sites.yml: {e}")
    exit(1)

if config and 'sites' in config:
    for site in config['sites']:
        host = site.get('host')
        if host:
            # Check if nginx vhost exists
            nginx_vhost = f"/etc/nginx/sites-available/{host}.conf"
            if not os.path.exists(nginx_vhost):
                print(f"New domain detected: {host}")
                # Run ssl-issue script for this domain
                result = subprocess.run([SSL_ISSUE_SCRIPT, host], cwd=os.environ['REPO'])
                if result.returncode != 0:
                    print(f"WARNING: Failed to issue SSL for {host}")

PYTHON_SCRIPT

# Sync nginx configuration
log "Syncing nginx configuration..."
bash "$DEPLOY_DIR/scripts/nginx-sync.sh" >> "$LOG_FILE" 2>&1 || {
    log "ERROR: nginx-sync.sh failed"
    exit 1
}

# Detect changes and rebuild services
log "Checking for service changes..."

# Get list of changed files
if git rev-parse HEAD~1 > /dev/null 2>&1; then
    CHANGED_FILES=$(git diff HEAD~1 --name-only || echo "")
else
    CHANGED_FILES=$(git ls-files)
fi

log "Changed files: $CHANGED_FILES"

# Determine which compose files need rebuilding
REBUILD_SERVICES=()

if echo "$CHANGED_FILES" | grep -q "^frontend/mietvertrag/"; then
    REBUILD_SERVICES+=("deploy/compose/docker-compose.mietvertrag.yml")
fi

if echo "$CHANGED_FILES" | grep -q "^frontend/wordpress/" || echo "$CHANGED_FILES" | grep -q "^modules/"; then
    REBUILD_SERVICES+=("deploy/compose/docker-compose.yml")
fi

# Rebuild and restart services
if [[ ${#REBUILD_SERVICES[@]} -gt 0 ]]; then
    for compose_file in "${REBUILD_SERVICES[@]}"; do
        log "Rebuilding and restarting services from $compose_file..."
        cd "$REPO"
        docker compose -f "$compose_file" up --build -d >> "$LOG_FILE" 2>&1 || {
            log "ERROR: docker compose up failed for $compose_file"
            exit 1
        }
        log "Successfully rebuilt and restarted services from $compose_file"
    done
else
    log "No service changes detected"
fi

# Send Telegram notification if environment variables are set
if [[ -n "${TELEGRAM_BOT_TOKEN:-}" && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
    log "Sending Telegram notification..."
    MESSAGE="✅ ContentPilot deployed — $COMMIT_MSG"
    TELEGRAM_URL="https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage"
    curl -s -X POST "$TELEGRAM_URL" \
        -H "Content-Type: application/json" \
        -d "{\"chat_id\": \"$TELEGRAM_CHAT_ID\", \"text\": \"$MESSAGE\"}" >> "$LOG_FILE" 2>&1 || {
        log "WARNING: Failed to send Telegram notification"
    }
fi

log "Deployment completed successfully!"
