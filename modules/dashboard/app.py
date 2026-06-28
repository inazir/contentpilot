# modules/dashboard/app.py
"""
ContentPilot Dashboard — Phase 13C Step 2.

Read-only skeleton: shows one brand's profile, social targets, and
content config. No auth yet (Step 3), no writes yet (Step 5).

Run directly for local dev:
    python3 app.py
Or via Docker (see docker-compose.yml dashboard service).
"""
import os
import sys

sys.path.insert(0, "/app")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from shared.brands import (
    get_brand_context_by_slug,
    get_all_content_config,
)

app = FastAPI(title="ContentPilot Dashboard")


@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html><body style="font-family: sans-serif; padding: 2rem;">
        <h1>ContentPilot Dashboard</h1>
        <p>Try <a href="/brands/germanysupport">/brands/germanysupport</a></p>
    </body></html>
    """


@app.get("/brands/{slug}", response_class=HTMLResponse)
def brand_view(slug: str):
    try:
        ctx = get_brand_context_by_slug(slug)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    configs = get_all_content_config(ctx.brand_id)

    config_html = ""
    if configs:
        for cfg in configs:
            data = cfg.as_dict()
            rows = "".join(
                f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in data.items()
            )
            config_html += f"""
            <h3>{cfg.platform}</h3>
            <table border="1" cellpadding="6">{rows}</table>
            """
    else:
        config_html = "<p><em>No content config saved yet for this brand.</em></p>"

    targets_html = ", ".join(ctx.social_targets) if ctx.social_targets else "(none)"

    return f"""
    <html><body style="font-family: sans-serif; padding: 2rem;">
        <h1>{ctx.brand_name}</h1>
        <p><strong>Slug:</strong> {ctx.brand_slug}</p>
        <p><strong>Website:</strong> {ctx.website_url or "(none)"}</p>
        <p><strong>Social targets:</strong> {targets_html}</p>
        <p><strong>Publish mode:</strong> {ctx.publish_mode}</p>
        <h2>Content Config</h2>
        {config_html}
    </body></html>
    """


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
