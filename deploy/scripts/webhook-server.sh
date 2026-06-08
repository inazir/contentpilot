#!/usr/bin/env bash
# ContentPilot Webhook Server
# Listens for GitHub push events and triggers deployment
# Runs as systemd service: contentpilot-webhook

set -euo pipefail

LOG_DIR="/var/log/contentpilot"
LOG_FILE="$LOG_DIR/webhook.log"

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "Starting ContentPilot webhook server..."

# Run Python webhook server
python3 << 'PYTHON_SCRIPT'
import http.server
import hmac
import hashlib
import os
import subprocess
import json
import sys
from datetime import datetime

WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '').encode()
DEPLOY_SCRIPT = '/home/deployer/repos/contentpilot/deploy/scripts/deploy.sh'
LOG_FILE = '/var/log/contentpilot/webhook.log'
PORT = 9000

if not WEBHOOK_SECRET:
    print("ERROR: WEBHOOK_SECRET environment variable not set", file=sys.stderr)
    sys.exit(1)

def log_message(msg):
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def send_forbidden(self, message=b'Forbidden'):
        self.send_response(403)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(message)

    def do_GET(self):
        """Reject GET requests to the webhook endpoint."""
        if self.path == '/deploy':
            log_message('Rejected request: GET method not allowed')
            self.send_forbidden(b'Forbidden')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not found')

    def do_HEAD(self):
        self.do_GET()

    def do_POST(self):
        """Handle POST requests from GitHub."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Verify signature
            signature_header = self.headers.get('X-Hub-Signature-256', '')
            
            if not signature_header:
                log_message("Rejected request: missing X-Hub-Signature-256 header")
                self.send_response(403)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Missing signature header')
                return
            
            # Calculate expected signature
            expected_sig = 'sha256=' + hmac.new(WEBHOOK_SECRET, body, hashlib.sha256).hexdigest()
            
            # Compare signatures (timing-safe)
            if not hmac.compare_digest(expected_sig, signature_header):
                log_message("Rejected request: invalid signature")
                self.send_response(403)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Invalid signature')
                return
            
            # Parse JSON payload
            try:
                payload = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                log_message("Rejected request: invalid JSON")
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Invalid JSON')
                return
            
            # Only process push events
            if self.headers.get('X-GitHub-Event', '') != 'push':
                log_message(f"Ignored event: {self.headers.get('X-GitHub-Event', 'unknown')}")
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Event ignored (not a push event)')
                return
            
            # Extract branch from ref (refs/heads/main -> main)
            ref = payload.get('ref', '')
            branch = ref.split('/')[-1] if '/' in ref else ref
            
            if branch != 'main':
                log_message(f"Ignored push to branch: {branch}")
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Push to non-main branch ignored')
                return
            
            # Valid webhook, trigger deployment
            log_message(f"Valid webhook received for branch: {branch}, triggering deployment...")
            
            # Spawn deploy script in background
            subprocess.Popen(
                ['/bin/bash', DEPLOY_SCRIPT],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
            
            log_message("Deploy script spawned in background")
            
            # Send success response
            self.send_response(202)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Deployment triggered')
            
        except Exception as e:
            log_message(f"Error processing webhook: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Internal server error')
    
    def log_message(self, format, *args):
        """Suppress default HTTP logging."""
        pass

# Start server
log_message("Webhook server starting on port 9000...")
server = http.server.HTTPServer(('', PORT), WebhookHandler)
log_message("Webhook server listening on 0.0.0.0:9000")

try:
    server.serve_forever()
except KeyboardInterrupt:
    log_message("Webhook server shutting down...")
    server.shutdown()

PYTHON_SCRIPT
