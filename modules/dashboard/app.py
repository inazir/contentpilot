# modules/dashboard/app.py
"""
ContentPilot Dashboard — Phase 13C Step 4.

Adds a dedicated Facebook config view: merges brand_credentials
(facebook) with brand_content_config (facebook) into one page.
Still read-only — write path is Step 5.

Steps 2+3 routes (index, login, brand_view, healthz) unchanged.
"""
import os
import sys

sys.path.insert(0, "/app")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from shared.brands import (
    get_brand_context_by_slug,
    get_brand_by_slug,
    get_all_content_config,
    get_content_config,
    get_credentials,
    CRED_FACEBOOK,
)
from auth import (
    SESSION_COOKIE_NAME,
    create_session_token,
    verify_password,
    verify_session_token,
)

app = FastAPI(title="ContentPilot Dashboard")


def _require_session(request: Request) -> None:
    token = request.cookies.get(SESSION_COOKIE_NAME, "")
    if not verify_session_token(token):
        raise HTTPException(status_code=401, detail="Login required")


def _mask_token(token: str | None) -> str:
    """Never render a real access token in HTML. Show a masked preview only."""
    if not token:
        return "(not set)"
    if len(token) <= 8:
        return "****"
    return f"{token[:4]}...{token[-4:]}"


@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html><body style="font-family: sans-serif; padding: 2rem;">
        <h1>ContentPilot Dashboard</h1>
        <p><a href="/login">Login</a></p>
        <p>Once logged in, try <a href="/brands/germanysupport">/brands/germanysupport</a>
           or <a href="/brands/germanysupport/facebook">/brands/germanysupport/facebook</a></p>
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
            <h3><a href="/brands/{slug}/{cfg.platform}">{cfg.platform}</a></h3>
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


@app.get("/brands/{slug}/facebook", response_class=HTMLResponse)
def facebook_config_view(slug: str, request: Request):
    _require_session(request)

    brand = get_brand_by_slug(slug)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand not found: {slug!r}")

    cred = get_credentials(brand.id, CRED_FACEBOOK)
    cred_data = cred.as_dict() if cred else {}

    content = get_content_config(brand.id, "facebook")
    content_data = content.as_dict() if content else {}

    page_id = cred_data.get("page_id", "(not set)")
    masked_token = _mask_token(cred_data.get("access_token"))

    content_rows = "".join(
        f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in content_data.items()
    ) or "<tr><td colspan='2'><em>No content config saved yet.</em></td></tr>"

    return f"""
    <html><body style="font-family: sans-serif; padding: 2rem;">
        <p><a href="/brands/{slug}">&larr; back to {slug}</a> | <a href="/logout">Logout</a></p>
        <h1>{brand.name} — Facebook</h1>

        <h2>Connection</h2>
        <table border="1" cellpadding="6">
            <tr><td>Page ID</td><td>{page_id}</td></tr>
            <tr><td>Access Token</td><td>{masked_token}</td></tr>
        </table>

        <h2>Content Strategy</h2>
        <table border="1" cellpadding="6">
            {content_rows}
        </table>

        <p><em>Edit form coming in Step 5.</em></p>
    </body></html>
    """


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
