#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/deployer/repos/contentpilot"
SITES_FILE="$REPO_ROOT/deploy/sites.yml"
TEMPLATE_FILE="$REPO_ROOT/deploy/nginx/sites/_template.conf.tpl"
NGINX_SITES_AVAILABLE="/etc/nginx/sites-available"
NGINX_SITES_ENABLED="/etc/nginx/sites-enabled"

if [[ ! -f "$SITES_FILE" ]]; then
    echo "ERROR: sites.yml not found at $SITES_FILE"
    exit 1
fi

# Check if python3 is available for YAML parsing
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 is required but not installed"
    exit 1
fi

# Export variables for Python script
export SITES_FILE
export TEMPLATE_FILE
export NGINX_SITES_AVAILABLE
export NGINX_SITES_ENABLED

# Parse YAML and extract hosts and ports
echo "Syncing nginx vhosts from sites.yml..."

python3 << 'PYTHON_SCRIPT'
import yaml
import os
import subprocess

SITES_FILE = os.environ.get('SITES_FILE')
TEMPLATE_FILE = os.environ.get('TEMPLATE_FILE')
NGINX_SITES_AVAILABLE = os.environ.get('NGINX_SITES_AVAILABLE')
NGINX_SITES_ENABLED = os.environ.get('NGINX_SITES_ENABLED')

try:
    with open(SITES_FILE, 'r') as f:
        config = yaml.safe_load(f)
except Exception as e:
    print(f"ERROR parsing sites.yml: {e}")
    exit(1)

if not config or 'sites' not in config:
    print("ERROR: sites.yml must contain 'sites' key")
    exit(1)

created_count = 0
updated_count = 0

for site in config['sites']:
    host = site.get('host')
    port = site.get('port')
    
    if not host or not port:
        print(f"WARNING: Skipping site with missing host or port: {site}")
        continue
    
    # Read template
    try:
        with open(TEMPLATE_FILE, 'r') as f:
            template_content = f.read()
    except Exception as e:
        print(f"ERROR reading template: {e}")
        exit(1)
    
    # Substitute variables
    vhost_content = template_content.replace('${HOST}', host).replace('${PORT}', str(port))
    
    # Write vhost file
    vhost_file = os.path.join(NGINX_SITES_AVAILABLE, f"{host}.conf")
    
    try:
        # Check if file already exists
        file_exists = os.path.exists(vhost_file)
        
        with open(vhost_file, 'w') as f:
            f.write(vhost_content)
        
        if file_exists:
            print(f"✓ Updated {host}")
            updated_count += 1
        else:
            print(f"✓ Created {host}")
            created_count += 1
        
        # Create symlink in sites-enabled
        symlink_path = os.path.join(NGINX_SITES_ENABLED, f"{host}.conf")
        
        # Remove old symlink if it exists
        if os.path.islink(symlink_path):
            os.remove(symlink_path)
        elif os.path.exists(symlink_path):
            os.remove(symlink_path)
        
        # Create new symlink
        os.symlink(vhost_file, symlink_path)
        
    except Exception as e:
        print(f"ERROR writing vhost file for {host}: {e}")
        exit(1)

print(f"\nSummary: {created_count} created, {updated_count} updated")

# Test nginx configuration
print("\nTesting nginx configuration...")
result = subprocess.run(['nginx', '-t'], capture_output=True, text=True)
if result.returncode != 0:
    print(f"ERROR: nginx configuration test failed:\n{result.stderr}")
    exit(1)

print("✓ nginx configuration is valid")

# Reload nginx
print("Reloading nginx...")
result = subprocess.run(['nginx', '-s', 'reload'], capture_output=True, text=True)
if result.returncode != 0:
    print(f"ERROR: Failed to reload nginx:\n{result.stderr}")
    exit(1)

print("✓ nginx reloaded successfully")

PYTHON_SCRIPT

export SITES_FILE TEMPLATE_FILE NGINX_SITES_AVAILABLE NGINX_SITES_ENABLED
