# modules/dashboard/app.py
"""
ContentPilot Dashboard — Phase 13C Step 8.

Adds hostname-based brand scoping: hitting
germanysupport.mycontentpilot.de auto-resolves to the germanysupport
brand, so /brands/{slug}/... routes are no longer needed from the
subdomain — the slug is inferred from the Host header.

Subdomain pattern: {slug}.mycontentpilot.de
Fallback: if the host header doesn't match a known brand subdomain
(e.g. direct IP access, localhost, healthz from a load balancer),
all existing routes still work exactly as before — slug must be
provided explicitly in the URL path.

Steps 2–7 routes are unchanged; subdomain resolution is purely
additive.
"""
import os
import sys
import logging
logger = logging.getLogger(__name__)

sys.path.insert(0, "/app")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "shared", "scheduler"))

from fastapi import FastAPI, HTTPException, Request, Form, UploadFile, File
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
    list_field_to_text,
    build_content_config,
    merge_credential_update,
    validate_content_config,
)
from facebook_preview import build_preview_plan
from facebook_schedule import (
    parse_schedule_form,
    validate_schedule,
    schedule_to_display,
    merge_schedule_into_config,
)
from facebook_csv import parse_csv_bytes, merge_topics, validate_topics_list
from schedule_config import (
    sync_schedule_to_db,
    get_active_schedules_for_brand,
    disable_schedules_for_brand,
)
from hostname import slug_from_host
from admin_auth import (
    ADMIN_COOKIE_NAME,
    verify_admin_password,
    create_admin_session_token,
    verify_admin_session_token,
)
from admin_views import (
    validate_brand_form,
    render_admin_brand_list,
    render_admin_brand_create_form,
    render_admin_brand_created,
    render_admin_brand_detail,
)
from shared.ai import get_ai_config, ai_complete, AIClientError

app = FastAPI(title="ContentPilot Dashboard")

class RedirectLoginException(Exception):
    pass

@app.exception_handler(RedirectLoginException)
async def redirect_login_handler(request: Request, exc: RedirectLoginException):
    return RedirectResponse(url="/login", status_code=303)


# ---------------------------------------------------------------------------
# Session + token helpers
# ---------------------------------------------------------------------------


def _require_session(request: Request) -> None:
    token = request.cookies.get(SESSION_COOKIE_NAME, "")
    if not verify_session_token(token):
        raise RedirectLoginException()


def _mask_token(token: str | None) -> str:
    if not token:
        return "(not set)"
    if len(token) <= 8:
        return "****"
    return f"{token[:4]}...{token[-4:]}"


# ---------------------------------------------------------------------------
# Subdomain-aware root redirect
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    slug = slug_from_host(request.headers.get("host", ""))
    if slug:
        # Hitting germanysupport.mycontentpilot.de/ → redirect to brand view
        return RedirectResponse(url=f"/brands/{slug}", status_code=302)

    return """
    <html><body style="font-family: sans-serif; padding: 2rem;">
        <h1>ContentPilot Dashboard</h1>
        <p><a href="/login">Login</a></p>
        <p>Once logged in, try
           <a href="/brands/germanysupport">/brands/germanysupport</a></p>
    </body></html>
    """


# ---------------------------------------------------------------------------
# Auth routes (unchanged)
# ---------------------------------------------------------------------------

@app.get("/login", response_class=HTMLResponse)
def login_form(error: str | None = None):
    error_html = f'<p style="color:red;">{error}</p>' if error else ""
    return f"""
    <html><body style="font-family: sans-serif; padding: 2rem;">
        <h1>Dashboard Login</h1>
        {error_html}
        <form method="post" action="/login">
            <input type="password" name="password"
                   placeholder="Password" autofocus>
            <button type="submit">Login</button>
        </form>
    </body></html>
    """


@app.post("/login")
def login_submit(password: str = Form(...)):
    if not verify_password(password):
        return RedirectResponse(
            url="/login?error=Invalid+password", status_code=303
        )
    token = create_session_token()
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=os.getenv(
            "DASHBOARD_COOKIE_SECURE", "true"
        ).lower() == "true",
        max_age=60 * 60 * 12,
    )
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response


# ---------------------------------------------------------------------------
# Brand overview
# ---------------------------------------------------------------------------

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
                f"<tr><td>{k}</td><td>{v}</td></tr>"
                for k, v in data.items()
            )
            config_html += f"""
            <h3>
              <a href="/brands/{slug}/{cfg.platform}">{cfg.platform}</a>
            </h3>
            <table border="1" cellpadding="6">{rows}</table>
            """
    else:
        config_html = (
            "<p><em>No content config saved yet for this brand.</em></p>"
        )

    targets_html = (
        ", ".join(ctx.social_targets) if ctx.social_targets else "(none)"
    )

    return f"""
    <html><body style="font-family: sans-serif; padding: 2rem;">
        <p><a href="/logout">Logout</a></p>
        <h1>{ctx.brand_name}</h1>
        <p><strong>Slug:</strong> {ctx.brand_slug}</p>
        <p><strong>Website:</strong> {ctx.website_url or "(none)"}</p>
        <p><strong>Social targets:</strong> {targets_html}</p>
        <p><strong>Publish mode:</strong> {ctx.publish_mode}</p>
        <p><a href="/brands/{slug}/history">📋 View post history</a></p>
        <h2>Content Config</h2>
        {config_html}
    </body></html>
    """


# ---------------------------------------------------------------------------
# Facebook — read, edit, preview (unchanged from Steps 4-6)
# ---------------------------------------------------------------------------

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
        f"<tr><td>{k}</td><td>{v}</td></tr>"
        for k, v in content_data.items()
    ) or "<tr><td colspan='2'><em>No content config saved yet.</em></td></tr>"

    # Phase 13D-Ext: show active schedule rows
    active_schedules = get_active_schedules_for_brand(brand.id, "daily_news")
    if active_schedules:
        sched_rows = "".join(
            f"<tr><td>{r['cron_expression']}</td>"
            f"<td style='color:green;'>active</td></tr>"
            for r in active_schedules
        )
        sched_html = f"""
        <table border="1" cellpadding="6">
            <tr><th>Cron expression (UTC)</th><th>Status</th></tr>
            {sched_rows}
        </table>
        <form method="post"
              action="/brands/{slug}/facebook/schedule/pause"
              style="display:inline;">
            <button type="submit"
                    style="margin-top:0.5rem;color:red;">
                ⏸ Pause scheduling
            </button>
        </form>
        """
    else:
        sched_html = (
            "<p><em>No active schedule. Save settings to activate.</em></p>"
        )

    return f"""
    <html><body style="font-family: sans-serif; padding: 2rem;">
        <p><a href="/brands/{slug}">&larr; back to {slug}</a>
           | <a href="/logout">Logout</a></p>
        <h1>{brand.name} — Facebook</h1>
        <p>
          <a href="/brands/{slug}/facebook/edit">
            <strong>Edit settings &rarr;</strong></a>
          | <a href="/brands/{slug}/facebook/preview">
              <strong>Generate preview &rarr;</strong></a>
        </p>
        <h2>Connection</h2>
        <table border="1" cellpadding="6">
            <tr><td>Page ID</td><td>{page_id}</td></tr>
            <tr><td>Access Token</td><td>{masked_token}</td></tr>
        </table>
        <h2>Content Strategy</h2>
        <table border="1" cellpadding="6">{content_rows}</table>
        <h2>Posting Schedule</h2>
        {sched_html}
    </body></html>
    """


def _render_facebook_edit_form(
    slug: str,
    page_id: str,
    content_data: dict,
    errors: list[str] | None = None,
) -> str:
    error_html = ""
    if errors:
        items = "".join(f"<li>{e}</li>" for e in errors)
        error_html = f'<ul style="color:red;">{items}</ul>'

    sched = schedule_to_display(content_data.get("schedule"))

    freq_options = "".join(
        f'<option value="{v}" {"selected" if sched["frequency"] == v else ""}>{l}</option>'
        for v, l in [("daily","Once daily"),("twice_daily","Twice daily"),("weekly","Weekly")]
    )

    day_checkboxes = "".join(
        f'<label style="margin-right:1rem;">'
        f'<input type="checkbox" name="schedule_active_days_cb" value="{i}" '
        f'{"checked" if i in (content_data.get("schedule") or {}).get("active_days", [0,1,2,3,4]) else ""}>'
        f' {d}</label>'
        for i, d in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
    )

    return f"""
    <html><body style="font-family:sans-serif;padding:2rem;max-width:700px;">
        <p><a href="/brands/{slug}/facebook">&larr; cancel</a>
           | <a href="/logout">Logout</a></p>
        <h1>Edit Facebook Settings</h1>
        {error_html}
        <form method="post" action="/brands/{slug}/facebook/edit">
            <h2>Connection</h2>
            <label>Page ID<br>
                <input type="text" name="page_id"
                       value="{page_id}" style="width:100%;"></label><br><br>
            <label>Access Token
                   <small>(leave blank to keep the current token)</small><br>
                <input type="password" name="access_token" value=""
                       style="width:100%;"
                       placeholder="Leave blank to keep existing token">
            </label>

            <h2>Content Strategy</h2>
            <label>Caption topics <small>(comma-separated, or upload CSV below)</small><br>
                <input type="text" name="caption_topics"
                       value="{list_field_to_text(content_data.get('caption_topics'))}"
                       style="width:100%;"></label><br><br>
            <label>Hashtags <small>(comma-separated)</small><br>
                <input type="text" name="hashtags"
                       value="{list_field_to_text(content_data.get('hashtags'))}"
                       style="width:100%;"></label><br><br>
            <label>Excluded keywords <small>(comma-separated)</small><br>
                <input type="text" name="excluded_keywords"
                       value="{list_field_to_text(content_data.get('excluded_keywords'))}"
                       style="width:100%;"></label><br><br>
            <label>Location text<br>
                <input type="text" name="location_text"
                       value="{content_data.get('location_text', '')}"
                       style="width:100%;"></label><br><br>
            <label>CTA text<br>
                <input type="text" name="cta_text"
                       value="{content_data.get('cta_text', '')}"
                       style="width:100%;"></label><br><br>
            <label>Image source<br>
                <select name="image_source" style="width:100%;">
                    {"".join(
                        f'<option value="{s}" {"selected" if content_data.get("image_source") == s else ""}>{s}</option>'
                        for s in ["pexels", "pixabay", "unsplash"]
                    )}
                </select></label><br><br>
            <label>Image title template<br>
                <input type="text" name="image_title_template"
                       value="{content_data.get('image_title_template', '')}"
                       style="width:100%;"></label><br><br>
            <label>Image subtitle template<br>
                <input type="text" name="image_subtitle_template"
                       value="{content_data.get('image_subtitle_template', '')}"
                       style="width:100%;"></label><br><br>
            <label>First comment template<br>
                <textarea name="first_comment_template"
                          style="width:100%;" rows="3">{content_data.get('first_comment_template', '')}</textarea>
            </label><br><br>
            <label>Tone<br>
                <input type="text" name="tone"
                       value="{content_data.get('tone', '')}"
                       style="width:100%;"></label><br><br>

            <h2>Posting Schedule</h2>
            <label>Frequency<br>
                <select name="schedule_frequency" style="width:100%;">
                    {freq_options}
                </select></label><br><br>
            <label>Posting times <small>(HH:MM UTC, comma-separated)</small><br>
                <input type="text" name="schedule_times"
                       value="{sched['times_text']}"
                       style="width:100%;"></label><br><br>
            <label>Active days<br>
                {day_checkboxes}
                <input type="hidden" name="schedule_active_days"
                       id="schedule_active_days_hidden"
                       value="{sched['active_days_text']}">
            </label><br><br>
            <label>Max posts per day (1–10)<br>
                <input type="number" name="schedule_max_posts"
                       value="{sched['max_posts']}" min="1" max="10"
                       style="width:80px;"></label><br><br>

            <p><small>⚠️ Schedule is saved and activates on next scheduler restart.
            Use the Pause button on the settings page to stop posting.</small></p>

            <button type="submit">Save</button>
        </form>

        <hr>
        <h2>Upload Topics from CSV</h2>
        <p>Upload a .csv file with one topic per row to add to your topics list.</p>
        <form method="post" action="/brands/{slug}/facebook/upload-topics"
              enctype="multipart/form-data">
            <input type="file" name="file" accept=".csv"><br><br>
            <label>
                <input type="checkbox" name="replace" value="1">
                Replace all existing topics (default: merge)
            </label><br><br>
            <button type="submit">Upload</button>
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
        slug=slug, page_id=cred_data.get("page_id", ""), content_data=content_data
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
    schedule_frequency: str = Form("daily"),
    schedule_times: str = Form("09:00"),
    schedule_active_days: str = Form("0,1,2,3,4"),
    schedule_max_posts: str = Form("1"),
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

    schedule_form = {
        "schedule_frequency": schedule_frequency,
        "schedule_times": schedule_times,
        "schedule_active_days": schedule_active_days,
        "schedule_max_posts": schedule_max_posts,
    }
    schedule = parse_schedule_form(schedule_form)

    all_errors = validate_content_config(new_content_config) + validate_schedule(schedule)
    if all_errors:
        return HTMLResponse(
            _render_facebook_edit_form(
                slug=slug,
                page_id=page_id,
                content_data=new_content_config,
                errors=all_errors,
            ),
            status_code=400,
        )

    new_content_config = merge_schedule_into_config(new_content_config, schedule)

    existing_cred = get_credentials(brand.id, CRED_FACEBOOK)
    existing_cred_data = existing_cred.as_dict() if existing_cred else {}
    merged_cred = merge_credential_update(existing_cred_data, page_id, access_token)

    upsert_credential(brand.id, CRED_FACEBOOK, merged_cred)
    upsert_content_config(brand.id, "facebook", new_content_config)

    # Phase 13D-Ext: sync validated schedule to the schedules table
    # so APScheduler picks it up on next restart.
    try:
        sync_schedule_to_db(
            brand_id=brand.id,
            module_name="daily_news",
            schedule=schedule,
        )
        logger.info(
            "schedule_synced_from_dashboard | brand_id=%d | frequency=%s",
            brand.id, schedule.get("frequency"),
        )
    except Exception as exc:
        # Never fail the whole save because of a scheduler write error.
        # Content config is already saved; the schedule will be retried
        # next time the user saves again.
        logger.error(
            "schedule_sync_failed | brand_id=%d | error=%s",
            brand.id, exc,
        )

    return RedirectResponse(url=f"/brands/{slug}/facebook", status_code=303)


@app.get("/brands/{slug}/facebook/preview", response_class=HTMLResponse)
def facebook_preview(slug: str, request: Request):
    _require_session(request)
    brand = get_brand_by_slug(slug)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand not found: {slug!r}")

    content = get_content_config(brand.id, "facebook")
    content_data = content.as_dict() if content else {}

    try:
        plan = build_preview_plan(content_data)
    except ValueError as exc:
        return HTMLResponse(f"""
        <html><body style="font-family: sans-serif; padding: 2rem;">
            <p><a href="/brands/{slug}/facebook">&larr; back</a></p>
            <h1>Preview unavailable</h1>
            <p style="color:red;">{exc}</p>
        </body></html>
        """, status_code=400)

    ai_error = None
    caption_text = None
    try:
        cfg = get_ai_config("daily_news")
        caption_text = ai_complete(cfg, prompt=plan["user_prompt"],
                                    system=plan["system_prompt"])
    except AIClientError as exc:
        ai_error = str(exc)

    caption_html = (
        f"<p>{caption_text}</p>" if caption_text
        else f'<p style="color:red;">Caption generation failed: {ai_error}</p>'
    )
    img = plan["image_plan"]

    return f"""
    <html><body style="font-family: sans-serif; padding: 2rem; max-width: 700px;">
        <p><a href="/brands/{slug}/facebook">&larr; back</a>
           | <a href="/logout">Logout</a></p>
        <h1>Preview — {brand.name} Facebook Post</h1>
        <p><em>Dry-run preview. Nothing was published or saved.</em></p>
        <h2>Topic used this time</h2><p>{plan['topic']}</p>
        <h2>Generated caption</h2>{caption_html}
        <h2>Hashtags</h2>
        <p>{plan['hashtag_line'] or '(none configured)'}</p>
        <h2>Image plan</h2>
        <table border="1" cellpadding="6">
            <tr><td>Source</td><td>{img['source']}</td></tr>
            <tr><td>Search query</td><td>{img['search_query']}</td></tr>
            <tr><td>Overlay title</td><td>{img['overlay_title']}</td></tr>
            <tr><td>Overlay subtitle</td><td>{img['overlay_subtitle'] or '(none)'}</td></tr>
        </table>
        <p><small>{img['note']}</small></p>
        <h2>First comment</h2>
        <p>{plan['first_comment'] or '(none configured)'}</p>
        <h2>CTA</h2>
        <p>{plan['cta_text'] or '(none configured)'}</p>
        <p><a href="/brands/{slug}/facebook/preview">Generate another</a></p>
    </body></html>
    """


# ---------------------------------------------------------------------------
# Phase 13D Step 2 — CSV topic upload
# ---------------------------------------------------------------------------

@app.post("/brands/{slug}/facebook/upload-topics", response_class=HTMLResponse)
async def facebook_upload_topics(
    slug: str,
    request: Request,
    file: UploadFile = File(...),
    replace: str = Form(""),
):
    _require_session(request)
    brand = get_brand_by_slug(slug)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand not found: {slug!r}")

    raw = await file.read()
    parse_errors: list[str] = []
    uploaded_topics: list[str] = []

    try:
        uploaded_topics, parse_errors = parse_csv_bytes(raw)
    except ValueError as exc:
        return HTMLResponse(f"""
        <html><body style="font-family:sans-serif;padding:2rem;">
            <p><a href="/brands/{slug}/facebook/edit">&larr; back</a></p>
            <h1>Upload failed</h1>
            <p style="color:red;">{exc}</p>
        </body></html>
        """, status_code=400)

    validation_errors = validate_topics_list(uploaded_topics)
    if validation_errors:
        return HTMLResponse(f"""
        <html><body style="font-family:sans-serif;padding:2rem;">
            <p><a href="/brands/{slug}/facebook/edit">&larr; back</a></p>
            <h1>Upload failed</h1>
            {"".join(f"<p style='color:red;'>{e}</p>" for e in validation_errors)}
        </body></html>
        """, status_code=400)

    content = get_content_config(brand.id, "facebook")
    content_data = content.as_dict() if content else {}
    existing_topics = content_data.get("caption_topics") or []

    do_replace = replace == "1"
    merged = merge_topics(existing_topics, uploaded_topics, replace=do_replace)
    content_data["caption_topics"] = merged
    upsert_content_config(brand.id, "facebook", content_data)

    action = "replaced" if do_replace else "merged"
    warning_html = "".join(f"<p style='color:orange;'>{e}</p>" for e in parse_errors)

    return HTMLResponse(f"""
    <html><body style="font-family:sans-serif;padding:2rem;">
        <p><a href="/brands/{slug}/facebook/edit">&larr; back to edit</a>
           | <a href="/brands/{slug}/facebook">view settings</a></p>
        <h1>Topics uploaded</h1>
        {warning_html}
        <p>Successfully {action} topics.
           {len(merged)} topic(s) now saved for {brand.name}.</p>
        <ul>{"".join(f"<li>{t}</li>" for t in merged[:20])}
        {"<li><em>...and more</em></li>" if len(merged) > 20 else ""}
        </ul>
    </body></html>
    """)


# ---------------------------------------------------------------------------
# Phase 13D Step 3 — Post history view
# ---------------------------------------------------------------------------

@app.get("/brands/{slug}/history", response_class=HTMLResponse)
def post_history(slug: str, request: Request, limit: int = 50):
    _require_session(request)

    brand = get_brand_by_slug(slug)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand not found: {slug!r}")

    # Read directly from publish_history using the same SQLite connection
    # pattern as the rest of the platform (shared/store.py).
    import os, sqlite3
    db_path = os.getenv("STORE_DB_PATH", "/app/data/db/contentpilot.db")

    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT platform, status, external_post_id,
                   error_message, published_at, module_name
            FROM publish_history
            WHERE target_key IN (
                SELECT value FROM json_each(
                    (SELECT credential_json FROM brand_credentials
                     WHERE brand_id = ? AND credential_type = 'social_targets'
                     ORDER BY id DESC LIMIT 1)
                )
            )
            OR module_name LIKE ?
            ORDER BY published_at DESC
            LIMIT ?
            """,
            (brand.id, f"%brand_id={brand.id}%", limit),
        ).fetchall()
        conn.close()
    except Exception:
        # Fallback: show all recent rows (no brand-scoping possible without
        # social_targets credential row being set)
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT platform, status, external_post_id, error_message, "
            "published_at, module_name FROM publish_history "
            "ORDER BY published_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        conn.close()

    if not rows:
        history_html = "<p><em>No posts published yet.</em></p>"
    else:
        history_rows = "".join(
            f"<tr>"
            f"<td>{r['published_at'][:19].replace('T',' ')}</td>"
            f"<td>{r['platform']}</td>"
            f"<td>{r['module_name']}</td>"
            f"<td style='color:{'green' if r['status']=='success' else 'red'};'>{r['status']}</td>"
            f"<td>{r['external_post_id'] or ''}</td>"
            f"<td style='color:red;font-size:0.85em;'>{r['error_message'] or ''}</td>"
            f"</tr>"
            for r in rows
        )
        history_html = f"""
        <table border="1" cellpadding="6" style="width:100%;border-collapse:collapse;">
            <tr style="background:#f0f0f0;">
                <th>Time (UTC)</th><th>Platform</th><th>Module</th>
                <th>Status</th><th>Post ID</th><th>Error</th>
            </tr>
            {history_rows}
        </table>
        """

    return f"""
    <html><body style="font-family:sans-serif;padding:2rem;max-width:1000px;">
        <p><a href="/brands/{slug}">&larr; back to {slug}</a>
           | <a href="/logout">Logout</a></p>
        <h1>{brand.name} — Post History</h1>
        <p>Showing last {limit} publish attempts.</p>
        {history_html}
    </body></html>
    """


# ---------------------------------------------------------------------------
# Phase 13D-Ext — schedule pause/resume
# ---------------------------------------------------------------------------

@app.post("/brands/{slug}/facebook/schedule/pause", response_class=HTMLResponse)
def facebook_schedule_pause(slug: str, request: Request):
    _require_session(request)
    brand = get_brand_by_slug(slug)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand not found: {slug!r}")
    disable_schedules_for_brand(brand.id, "daily_news")
    return RedirectResponse(url=f"/brands/{slug}/facebook", status_code=303)


# ---------------------------------------------------------------------------
# Phase 14A — Admin panel
# ---------------------------------------------------------------------------

def _require_admin_session(request: Request) -> None:
    """Raises RedirectLoginException to /admin/login if not authenticated."""
    token = request.cookies.get(ADMIN_COOKIE_NAME, "")
    if not verify_admin_session_token(token):
        raise HTTPException(status_code=302, headers={"Location": "/admin/login"})


@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_form(error: str | None = None):
    error_html = f'<p style="color:red;">{error}</p>' if error else ""
    return f"""
    <html><body style="font-family:sans-serif;padding:2rem;max-width:500px;">
        <h1>ContentPilot Admin</h1>
        {error_html}
        <form method="post" action="/admin/login">
            <input type="password" name="password"
                   placeholder="Admin password" autofocus style="width:100%;">
            <br><br>
            <button type="submit">Login</button>
        </form>
    </body></html>
    """


@app.post("/admin/login")
def admin_login_submit(password: str = Form(...)):
    if not verify_admin_password(password):
        return RedirectResponse(
            url="/admin/login?error=Invalid+admin+password", status_code=303
        )
    token = create_admin_session_token()
    response = RedirectResponse(url="/admin", status_code=303)
    response.set_cookie(
        key=ADMIN_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=os.getenv("DASHBOARD_COOKIE_SECURE", "true").lower() == "true",
        max_age=60 * 60 * 8,
    )
    return response


@app.get("/admin/logout")
def admin_logout():
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie(ADMIN_COOKIE_NAME)
    return response


@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request, flash: str = ""):
    _require_admin_session(request)
    from shared.brands import get_all_enabled_brands
    brands = get_all_enabled_brands()
    brand_dicts = [
        {
            "id": b.id,
            "name": b.name,
            "slug": b.slug,
            "enabled": b.enabled,
        }
        for b in brands
    ]
    return render_admin_brand_list(brand_dicts, flash=flash)


@app.get("/admin/brands/new", response_class=HTMLResponse)
def admin_brand_new_form(request: Request):
    _require_admin_session(request)
    return render_admin_brand_create_form()


@app.post("/admin/brands/new", response_class=HTMLResponse)
def admin_brand_new_submit(
    request: Request,
    name: str = Form(""),
    slug: str = Form(""),
    website_url: str = Form(""),
    brand_name: str = Form(""),
    brand_cta: str = Form(""),
):
    _require_admin_session(request)

    name = name.strip()
    slug = slug.strip().lower()

    errors = validate_brand_form(name, slug)

    # Also check slug uniqueness against existing brands
    if not errors:
        from shared.brands import get_brand_by_slug
        existing = get_brand_by_slug(slug)
        if existing:
            errors.append(f"A brand with slug '{slug}' already exists.")

    if errors:
        return HTMLResponse(
            render_admin_brand_create_form(errors=errors),
            status_code=400,
        )

    from shared.brands import create_brand, upsert_profile
    brand_id = create_brand(name=name, slug=slug)
    upsert_profile(
        brand_id=brand_id,
        website_url=website_url.strip(),
        brand_name=brand_name.strip() or name,
        brand_cta=brand_cta.strip(),
    )

    logger.info(
        "admin_brand_created | brand_id=%d | name=%s | slug=%s",
        brand_id, name, slug,
    )

    return HTMLResponse(render_admin_brand_created(name, slug))


@app.get("/admin/brands/{slug}", response_class=HTMLResponse)
def admin_brand_detail(slug: str, request: Request, flash: str = ""):
    _require_admin_session(request)

    from shared.brands import get_brand_by_slug, get_all_credentials
    brand = get_brand_by_slug(slug)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand not found: {slug!r}")

    creds = get_all_credentials(brand.id)
    cred_types = {c.credential_type for c in creds}

    schedules = get_active_schedules_for_brand(brand.id, "daily_news")

    brand_dict = {
        "id": brand.id,
        "name": brand.name,
        "slug": brand.slug,
        "enabled": brand.enabled,
    }

    return render_admin_brand_detail(
        brand=brand_dict,
        credentials=cred_types,
        schedules=schedules,
        flash=flash,
    )


@app.post("/admin/brands/{slug}/enable", response_class=HTMLResponse)
def admin_brand_enable(slug: str, request: Request):
    _require_admin_session(request)
    _admin_set_brand_enabled(slug, enabled=True)
    return RedirectResponse(url=f"/admin/brands/{slug}?flash=Brand+enabled", status_code=303)


@app.post("/admin/brands/{slug}/disable", response_class=HTMLResponse)
def admin_brand_disable(slug: str, request: Request):
    _require_admin_session(request)
    _admin_set_brand_enabled(slug, enabled=False)
    return RedirectResponse(url=f"/admin/brands/{slug}?flash=Brand+disabled", status_code=303)


def _admin_set_brand_enabled(slug: str, enabled: bool) -> None:
    """Enable or disable a brand by slug."""
    import sqlite3 as _sqlite3
    from datetime import datetime, timezone
    db_path = os.getenv("STORE_DB_PATH", "/app/data/db/contentpilot.db")
    now = datetime.now(timezone.utc).isoformat()
    conn = _sqlite3.connect(db_path, check_same_thread=False)
    conn.execute(
        "UPDATE brands SET enabled = ?, updated_at = ? WHERE slug = ?",
        (1 if enabled else 0, now, slug),
    )
    conn.commit()
    conn.close()
    logger.info(
        "admin_brand_%s | slug=%s", "enabled" if enabled else "disabled", slug
    )


# ---------------------------------------------------------------------------
# Health check (unauthenticated, always open)
# ---------------------------------------------------------------------------

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
