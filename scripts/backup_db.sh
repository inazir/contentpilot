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

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ENV_FILE="$REPO_ROOT/.env"
if [[ -f "$ENV_FILE" ]]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

# If BACKUP_DIR or DATA_DIR point to the container's internal /app mount, 
# redirect them to the actual relative directories on the host filesystem.
# Use ${VAR:-} to prevent unbound variable crashes if they aren't defined in .env
if [[ "${DATA_DIR:-}" == /app/* ]]; then
    DATA_DIR="$REPO_ROOT/data"
fi

if [[ "${BACKUP_DIR:-}" == /app/* ]]; then
    BACKUP_DIR="$REPO_ROOT/data/backups"
fi

DATA_DIR="${DATA_DIR:-$REPO_ROOT/data}"
BACKUP_DIR="${BACKUP_DIR:-$DATA_DIR/backups}"
DB_DIR="$DATA_DIR/db"
KEEP_DAYS="${BACKUP_KEEP_DAYS:-7}"
TIMESTAMP="$(date -u '+%Y%m%dT%H%M%SZ')"

_log() { echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') [backup_db] $*"; }

# Check if sqlite3 is available; fall back to file copy if not (non-WAL-safe but functional)
HAS_SQLITE3=false
if command -v sqlite3 &>/dev/null; then
    HAS_SQLITE3=true
fi
if ! $HAS_SQLITE3; then
    _log "WARNING: sqlite3 not found on host — falling back to cp (backup may be inconsistent under WAL mode)"
fi

mkdir -p "$BACKUP_DIR"

BACKED_UP=0
FAILED=0

while IFS= read -r -d '' db_file; do
    db_name=$(basename "$db_file" .db)
    backup_file="$BACKUP_DIR/${db_name}_${TIMESTAMP}.db.gz"

    _log "Backing up $db_name..."

    # Skip if the source database file doesn't exist
    if [ ! -f "$db_file" ]; then
        _log "  SKIP: source file not found at $db_file"
        continue
    fi

    # Ensure the target directory exists for this backup file
    mkdir -p "$(dirname "$backup_file")"

    backup_dest="/tmp/${db_name}_backup_$$.db"
    backup_ok=false

    if $HAS_SQLITE3; then
        # Use sqlite3's online-safe .backup API (WAL-safe)
        if sqlite3 "$db_file" ".backup '$backup_dest'" 2>/dev/null; then
            backup_ok=true
        fi
    else
        # Fallback: simple file copy (not safe under WAL mode, but functional)
        if cp "$db_file" "$backup_dest" 2>/dev/null; then
            backup_ok=true
        fi
    fi

    if $backup_ok; then
        gzip -c "$backup_dest" > "$backup_file"
        rm -f "$backup_dest"
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
