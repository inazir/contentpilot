# modules/dashboard/app.py
"""
ContentPilot Dashboard — Phase 13C Step 5.

Adds the editable Facebook config form:
  GET  /brands/{slug}/facebook/edit   — render form (token field always blank)
  POST /brands/{slug}/facebook/edit   — validate, merge, save

The read-only view from Step 4 (/brands/{slug}/facebook) stays as-is
and now links to the edit form.
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
    upsert_credential,
    upsert_content_config,
    CRED_FACEBOOK,
)
from auth import (
    SESSION_COOKIE_NAME,
    create_session_token,
    verify_password,
    verify_session_token,
)
from facebook_form import (
    parse_list_field,
    list_field_to_text,
    build_content_config,
    merge_credential_update,
    validate_content_config,
)

app = FastAPI(title="ContentPilot Dashboard")


def _require_session(request: Request) -> None:
    token = request.cookies.get(SESSION_COOKIE_NAME, "")
    if not verify_session_token(token):
        raise HTTPException(status_code=401, detail="Login required")


def _mask_token(token: str | None) -> str:
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
            rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in data.items())
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
        <p><a href="/brands/{slug}/facebook/edit"><strong>Edit settings &rarr;</strong></a></p>

        <h2>Connection</h2>
        <table border="1" cellpadding="6">
            <tr><td>Page ID</td><td>{page_id}</td></tr>
            <tr><td>Access Token</td><td>{masked_token}</td></tr>
        </table>

        <h2>Content Strategy</h2>
        <table border="1" cellpadding="6">
            {content_rows}
        </table>
    </body></html>
    """


def _render_facebook_edit_form(
    slug: str, page_id: str, content_data: dict, errors: list[str] | None = None
) -> str:
    error_html = ""
    if errors:
        items = "".join(f"<li>{e}</li>" for e in errors)
        error_html = f'<ul style="color:red;">{items}</ul>'

    return f"""
    <html><body style="font-family: sans-serif; padding: 2rem; max-width: 700px;">
        <p><a href="/brands/{slug}/facebook">&larr; cancel</a> | <a href="/logout">Logout</a></p>
        <h1>Edit Facebook Settings</h1>
        {error_html}
        <form method="post" action="/brands/{slug}/facebook/edit">

            <h2>Connection</h2>
            <label>Page ID<br>
                <input type="text" name="page_id" value="{page_id}" style="width:100%;">
            </label><br><br>
            <label>Access Token <small>(leave blank to keep the current token)</small><br>
                <input type="password" name="access_token" value="" style="width:100%;"
                       placeholder="Leave blank to keep existing token">
            </label>

            <h2>Content Strategy</h2>
            <label>Caption topics <small>(comma-separated)</small><br>
                <input type="text" name="caption_topics"
                       value="{list_field_to_text(content_data.get('caption_topics'))}"
                       style="width:100%;">
            </label><br><br>
            <label>Hashtags <small>(comma-separated)</small><br>
                <input type="text" name="hashtags"
                       value="{list_field_to_text(content_data.get('hashtags'))}"
                       style="width:100%;">
            </label><br><br>
            <label>Excluded keywords <small>(comma-separated)</small><br>
                <input type="text" name="excluded_keywords"
                       value="{list_field_to_text(content_data.get('excluded_keywords'))}"
                       style="width:100%;">
            </label><br><br>
            <label>Location text<br>
                <input type="text" name="location_text"
                       value="{content_data.get('location_text', '')}" style="width:100%;">
            </label><br><br>
            <label>CTA text<br>
                <input type="text" name="cta_text"
                       value="{content_data.get('cta_text', '')}" style="width:100%;">
            </label><br><br>
            <label>Image source<br>
                <select name="image_source" style="width:100%;">
                    {"".join(
                        f'<option value="{s}" {"selected" if content_data.get("image_source") == s else ""}>{s}</option>'
                        for s in ["pexels", "pixabay", "unsplash"]
                    )}
                </select>
            </label><br><br>
            <label>Image title template<br>
                <input type="text" name="image_title_template"
                       value="{content_data.get('image_title_template', '')}" style="width:100%;">
            </label><br><br>
            <label>Image subtitle template<br>
                <input type="text" name="image_subtitle_template"
                       value="{content_data.get('image_subtitle_template', '')}" style="width:100%;">
            </label><br><br>
            <label>First comment template<br>
                <textarea name="first_comment_template" style="width:100%;" rows="3">{content_data.get('first_comment_template', '')}</textarea>
            </label><br><br>
            <label>Tone<br>
                <input type="text" name="tone"
                       value="{content_data.get('tone', '')}" style="width:100%;">
            </label><br><br>

            <button type="submit">Save</button>
        </form>
    </body></html>
    """


@app.get("/brands/{slug}/facebook/edit", response_class=HTMLResponse)
def facebook_edit_form(slug: str, request: Request):
    _require_session(request)

    brand = get_brand_by_slug(slug)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand not found: {slug!r}")

    cred = get_credentials(brand.id, CRED_FACEBOOK)
    cred_data = cred.as_dict() if cred else {}

    content = get_content_config(brand.id, "facebook")
    content_data = content.as_dict() if content else {}

    return _render_facebook_edit_form(
        slug=slug,
        page_id=cred_data.get("page_id", ""),
        content_data=content_data,
    )


@app.post("/brands/{slug}/facebook/edit", response_class=HTMLResponse)
def facebook_edit_submit(
    slug: str,
    request: Request,
    page_id: str = Form(""),
    access_token: str = Form(""),
    caption_topics: str = Form(""),
    hashtags: str = Form(""),
    excluded_keywords: str = Form(""),
    location_text: str = Form(""),
    cta_text: str = Form(""),
    image_source: str = Form("pexels"),
    image_title_template: str = Form(""),
    image_subtitle_template: str = Form(""),
    first_comment_template: str = Form(""),
    tone: str = Form(""),
):
    _require_session(request)

    brand = get_brand_by_slug(slug)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand not found: {slug!r}")

    form = {
        "caption_topics": caption_topics,
        "hashtags": hashtags,
        "excluded_keywords": excluded_keywords,
        "location_text": location_text,
        "cta_text": cta_text,
        "image_source": image_source,
        "image_title_template": image_title_template,
        "image_subtitle_template": image_subtitle_template,
        "first_comment_template": first_comment_template,
        "tone": tone,
    }
    new_content_config = build_content_config(form)

    errors = validate_content_config(new_content_config)
    if errors:
        return HTMLResponse(
            _render_facebook_edit_form(
                slug=slug,
                page_id=page_id,
                content_data=new_content_config,
                errors=errors,
            ),
            status_code=400,
        )

    # Merge credential update — blank access_token means "keep existing"
    existing_cred = get_credentials(brand.id, CRED_FACEBOOK)
    existing_cred_data = existing_cred.as_dict() if existing_cred else {}
    merged_cred = merge_credential_update(existing_cred_data, page_id, access_token)

    upsert_credential(brand.id, CRED_FACEBOOK, merged_cred)
    upsert_content_config(brand.id, "facebook", new_content_config)

    return RedirectResponse(url=f"/brands/{slug}/facebook", status_code=303)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
