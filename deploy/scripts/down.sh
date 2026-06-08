#!/usr/bin/env bash
set -euo pipefail

REPO="/home/deployer/repos/contentpilot"
COMPOSE_DIR="$REPO/deploy/compose"

echo "Stopping all services..."

for compose_file in "$COMPOSE_DIR"/docker-compose*.yml; do
    if [[ -f "$compose_file" ]]; then
        echo "Stopping services from $(basename "$compose_file")..."
        docker compose -f "$compose_file" down || {
            echo "ERROR: Failed to stop services from $(basename "$compose_file")"
            exit 1
        }
    fi
done

echo "✓ All services stopped successfully"
