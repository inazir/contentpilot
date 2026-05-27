#!/usr/bin/env bash
# scripts/backup_db.sh
#
# Backs up all ContentPilot SQLite databases with timestamped gzip files.
#
# Usage:
#   ./scripts/backup_db.sh
#   BACKUP_DIR=/mnt/backups ./scripts/backup_db.sh
#
# Cron example (daily at 03:00):
#   0 3 * * * /home/deployer/repos/contentpilot/scripts/backup_db.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ENV_FILE="$REPO_ROOT/.env"
if [[ -f "$ENV_FILE" ]]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

DATA_DIR="${DATA_DIR:-$REPO_ROOT/data}"
BACKUP_DIR="${BACKUP_DIR:-$DATA_DIR/backups}"
DB_DIR="$DATA_DIR/db"
KEEP_DAYS="${BACKUP_KEEP_DAYS:-7}"
TIMESTAMP="$(date -u '+%Y%m%dT%H%M%SZ')"

mkdir -p "$BACKUP_DIR"

_log() { echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') [backup_db] $*"; }

BACKED_UP=0
FAILED=0

while IFS= read -r -d '' db_file; do
    db_name=$(basename "$db_file" .db)
    backup_file="$BACKUP_DIR/${db_name}_${TIMESTAMP}.db.gz"

    _log "Backing up $db_name..."

    if sqlite3 "$db_file" ".backup /tmp/${db_name}_backup_$$.db" 2>/dev/null; then
        gzip -c "/tmp/${db_name}_backup_$$.db" > "$backup_file"
        rm -f "/tmp/${db_name}_backup_$$.db"
        size=$(du -h "$backup_file" | cut -f1)
        _log "  OK: $backup_file ($size)"
        BACKED_UP=$((BACKED_UP + 1))
    else
        _log "  FAILED: $db_file"
        FAILED=$((FAILED + 1))
    fi
 done < <(find "$DB_DIR" -name "*.db" -print0 2>/dev/null)

_log "Removing backups older than ${KEEP_DAYS} days..."
find "$BACKUP_DIR" -name "*.db.gz" -mtime "+${KEEP_DAYS}" -delete 2>/dev/null || true

REMAINING=$(find "$BACKUP_DIR" -name "*.db.gz" 2>/dev/null | wc -l)
_log "Backup complete | backed_up=$BACKED_UP | failed=$FAILED | kept_files=$REMAINING"

if [[ $FAILED -gt 0 ]]; then
    exit 1
fi
