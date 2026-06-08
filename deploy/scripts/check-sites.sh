#!/usr/bin/env bash
set -euo pipefail

REPO="/home/deployer/repos/contentpilot"
SITES_FILE="${1:-$REPO/deploy/sites.yml}"

if [[ ! -f "$SITES_FILE" ]]; then
    echo "ERROR: sites.yml not found at $SITES_FILE"
    exit 1
fi

# Parse YAML and check each site
python3 - "$SITES_FILE" << 'PYTHON_SCRIPT'
import yaml
import subprocess
import sys

SITES_FILE = sys.argv[1] if len(sys.argv) > 1 else None

if not SITES_FILE:
    print("ERROR: sites.yml path required")
    exit(1)

try:
    with open(SITES_FILE, 'r') as f:
        config = yaml.safe_load(f)
except Exception as e:
    print(f"ERROR parsing sites.yml: {e}")
    exit(1)

if not config or 'sites' not in config:
    print("ERROR: sites.yml must contain 'sites' key")
    exit(1)

failed = False

for site in config['sites']:
    host = site.get('host')
    if not host:
        continue
    
    # Try to curl the HTTPS endpoint
    try:
        result = subprocess.run(
            ['curl', '-sf', f'https://{host}', '-o', '/dev/null'],
            timeout=5,
            capture_output=True
        )
        if result.returncode == 0:
            print(f"✓ {host} OK")
        else:
            print(f"✗ {host} FAIL (curl returned {result.returncode})")
            failed = True
    except subprocess.TimeoutExpired:
        print(f"✗ {host} TIMEOUT")
        failed = True
    except Exception as e:
        print(f"✗ {host} ERROR: {e}")
        failed = True

if failed:
    exit(1)

PYTHON_SCRIPT
