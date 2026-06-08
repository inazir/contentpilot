#!/usr/bin/env bash
set -euo pipefail

REPO="/home/deployer/repos/contentpilot"
COMPOSE_DIR="$REPO/deploy/compose"

echo "Starting all services..."

for compose_file in "$COMPOSE_DIR"/docker-compose*.yml; do
    if [[ -f "$compose_file" ]]; then
        echo "Starting services from $(basename "$compose_file")..."
        docker compose -f "$compose_file" up -d || {
            echo "ERROR: Failed to start services from $(basename "$compose_file")"
            exit 1
        }
    fi
done

echo "✓ All services started successfully"
