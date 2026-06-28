# modules/dashboard/app.py
"""
ContentPilot Dashboard — Phase 13C Step 3.

Step 2 (read-only brand view) + Step 3 (single-admin session auth).
Brand routes now require a valid session; /login, /logout, /healthz
stay open.
"""
import os
import sys

sys.path.insert(0, "/app")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from shared.brands import (
    get_brand_context_by_slug,
    get_all_content_config,
)
from auth import (
    SESSION_COOKIE_NAME,
    create_session_token,
    verify_password,
    verify_session_token,
)

app = FastAPI(title="ContentPilot Dashboard")


def _require_session(request: Request) -> None:
    """Raise 401 if the request has no valid session cookie."""
    token = request.cookies.get(SESSION_COOKIE_NAME, "")
    if not verify_session_token(token):
        raise HTTPException(status_code=401, detail="Login required")


@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html><body style="font-family: sans-serif; padding: 2rem;">
        <h1>ContentPilot Dashboard</h1>
        <p><a href="/login">Login</a></p>
        <p>Once logged in, try <a href="/brands/germanysupport">/brands/germanysupport</a></p>
    </body></html>
    """


@app.get("/login", response_class=HTMLResponse)
def login_form(error: str | None = None):
    error_html = f'<p style="color:red;">{error}</p>' if error else ""
    return f"""
    <html><body style="font-family: sans-serif; padding: 2rem;">
        <h1>Dashboard Login</h1>
        {error_html}
        <form method="post" action="/login">
            <input type="password" name="password" placeholder="Password" autofocus>
            <button type="submit">Login</button>
        </form>
    </body></html>
    """


@app.post("/login")
def login_submit(password: str = Form(...)):
    if not verify_password(password):
        return RedirectResponse(url="/login?error=Invalid+password", status_code=303)

    token = create_session_token()
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=os.getenv("DASHBOARD_COOKIE_SECURE", "true").lower() == "true",
        max_age=60 * 60 * 12,
    )
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response


@app.get("/brands/{slug}", response_class=HTMLResponse)
def brand_view(slug: str, request: Request):
    _require_session(request)

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
        <p><a href="/logout">Logout</a></p>
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
