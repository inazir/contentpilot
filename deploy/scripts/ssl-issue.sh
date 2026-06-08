#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <domain>"
    exit 1
fi

DOMAIN="$1"
LOG_DIR="/var/log/contentpilot"
LOG_FILE="$LOG_DIR/ssl-issue.log"
LETSENCRYPT_PATH="/etc/letsencrypt/live/$DOMAIN"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Check if SSL certificate already exists
if [[ -d "$LETSENCRYPT_PATH" ]]; then
    echo "SSL already valid for $DOMAIN"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SSL already valid for $DOMAIN" >> "$LOG_FILE"
    exit 0
fi

echo "Issuing SSL certificate for $DOMAIN..."
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting SSL issuance for $DOMAIN" >> "$LOG_FILE"

# Run certbot
if certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m admin@mycontentpilot.de >> "$LOG_FILE" 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Successfully issued SSL certificate for $DOMAIN" >> "$LOG_FILE"
    echo "✓ SSL certificate issued successfully for $DOMAIN"
    exit 0
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Failed to issue SSL certificate for $DOMAIN" >> "$LOG_FILE"
    echo "✗ Failed to issue SSL certificate for $DOMAIN"
    exit 1
fi
