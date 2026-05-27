#!/usr/bin/env bash
# scripts/run_job.sh
#
# Universal job entrypoint for ContentPilot.
# All cron jobs and manual runs go through this script.
#
# Usage:
#   ./scripts/run_job.sh <module_name> [extra docker args]
#
# Examples:
#   ./scripts/run_job.sh daily_news
#   ./scripts/run_job.sh daily_news --dry-run
#
# Environment:
#   COMPOSE_FILE   path to docker-compose.yml (default: infra/compose/docker-compose.yml)
#   NOTIFY_ON_FAIL set to "true" to send failure notifications

set -euo pipefail

# ---------------------------------------------------------------------------
# Resolve repo root regardless of where cron calls this from
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ---------------------------------------------------------------------------
# Args
# ---------------------------------------------------------------------------
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <module_name> [extra args]"
    exit 1
fi

MODULE="$1"
shift
EXTRA_ARGS=("$@")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
COMPOSE_FILE="${COMPOSE_FILE:-$REPO_ROOT/infra/compose/docker-compose.yml}"
LOG_DIR="$REPO_ROOT/data/runtime"
LOG_FILE="$LOG_DIR/${MODULE}.log"
ENV_FILE="$REPO_ROOT/.env"

mkdir -p "$LOG_DIR"

# ---------------------------------------------------------------------------
# Load .env if it exists (so cron picks up variables without exporting)
# ---------------------------------------------------------------------------
if [[ -f "$ENV_FILE" ]]; then
    while IFS='=' read -r key value; do
        if [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]]; then
            continue
        fi
        export "$key=$value"
    done < "$ENV_FILE"
fi

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
_ts()  { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
_log() { echo "$(_ts) [run_job] $*" | tee -a "$LOG_FILE"; }

# Rotate log if over 5MB
if [[ -f "$LOG_FILE" ]] && [[ $(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt 5242880 ]]; then
    mv "$LOG_FILE" "${LOG_FILE}.$(date -u +%Y%m%d%H%M%S).bak"
fi

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
_log "START module=$MODULE args=${EXTRA_ARGS[*]:-none}"

START_TS=$(date +%s)
EXIT_CODE=0

docker compose \
    -f "$COMPOSE_FILE" \
    run --rm \
    "$MODULE" \
    python main.py "${EXTRA_ARGS[@]}" \
    >> "$LOG_FILE" 2>&1 || EXIT_CODE=$?

END_TS=$(date +%s)
DURATION=$(( END_TS - START_TS ))

if [[ $EXIT_CODE -eq 0 ]]; then
    _log "END module=$MODULE exit=0 duration=${DURATION}s status=SUCCESS"
else
    _log "END module=$MODULE exit=$EXIT_CODE duration=${DURATION}s status=FAILED"

    if [[ "${NOTIFY_ON_FAIL:-false}" == "true" ]]; then
        docker compose \
            -f "$COMPOSE_FILE" \
            run --rm \
            "$MODULE" \
            python -c "import sys; sys.path.insert(0,'/app'); from shared.notify import notify_failure; notify_failure('$MODULE', 'exit code $EXIT_CODE', '')" \
            >> "$LOG_FILE" 2>&1 || true
    fi
fi

exit $EXIT_CODE
