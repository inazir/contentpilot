# modules/dashboard/main.py
"""
Standardized entrypoint. Unlike daily_news (one-shot job), the dashboard
is a long-running web server, so this just starts uvicorn directly
rather than going through managed_run().
"""
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, "/app")

import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("DASHBOARD_PORT", "8090"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, log_level="info")
