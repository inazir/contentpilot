# modules/dashboard/admin_views.py
"""
Phase 14A: Admin panel rendering helpers.

Pure functions — no FastAPI imports, no DB calls.
All data is passed in; these functions only produce HTML strings.
Separated so they can be unit-tested without importing FastAPI.

The "infrastructure instructions" pattern: when a new brand is created,
the admin panel shows exact Caddyfile and sites.yml lines to add rather
than trying to auto-edit those files. Auto-editing Caddy config risks
taking down all sites if something goes wrong; showing the lines is
safer and transparent.
"""
from __future__ import annotations


BASE_DOMAIN = "mycontentpilot.de"
DASHBOARD_PORT = 8090


def render_admin_brand_list(brands: list[dict], flash: str = "") -> str:
    flash_html = f'<p style="color:green;font-weight:bold;">{flash}</p>' if flash else ""
    if not brands:
        rows_html = "<tr><td colspan='4'><em>No brands yet.</em></td></tr>"
    else:
        rows_html = "".join(
            f"<tr>"
            f"<td>{b['id']}</td>"
            f"<td><a href='/admin/brands/{b['slug']}'>{b['name']}</a></td>"
            f"<td>{b['slug']}</td>"
            f"<td style='color:{'green' if b['enabled'] else 'red'};'>"
            f"{'enabled' if b['enabled'] else 'disabled'}</td>"
            f"<td>"
            f"<a href='/admin/brands/{b['slug']}'>Edit</a>"
            f"</td>"
            f"</tr>"
            for b in brands
        )
    return f"""
    <html><body style="font-family:sans-serif;padding:2rem;max-width:900px;">
        <p><a href="/admin/logout">Logout (admin)</a></p>
        <h1>ContentPilot Admin</h1>
        {flash_html}
        <h2>Brands</h2>
        <table border="1" cellpadding="6" style="width:100%;border-collapse:collapse;">
            <tr style="background:#f0f0f0;">
                <th>ID</th><th>Name</th><th>Slug</th>
                <th>Status</th><th>Actions</th>
            </tr>
            {rows_html}
        </table>
        <br>
        <a href="/admin/brands/new"><strong>+ Create new brand</strong></a>
    </body></html>
    """


def render_admin_brand_create_form(errors: list[str] | None = None) -> str:
    error_html = ""
    if errors:
        items = "".join(f"<li>{e}</li>" for e in errors)
        error_html = f'<ul style="color:red;">{items}</ul>'
    return f"""
    <html><body style="font-family:sans-serif;padding:2rem;max-width:700px;">
        <p><a href="/admin">&larr; back to admin</a>
           | <a href="/admin/logout">Logout</a></p>
        <h1>Create New Brand</h1>
        {error_html}
        <form method="post" action="/admin/brands/new">
            <label>Brand name <small>(e.g. "Germany Support")</small><br>
                <input type="text" name="name" style="width:100%;"
                       required autofocus></label><br><br>
            <label>Slug <small>(e.g. "germanysupport" — lowercase, no spaces,
                   used for subdomain)</small><br>
                <input type="text" name="slug" style="width:100%;"
                       pattern="[a-z0-9-]+" required
                       title="Lowercase letters, numbers, hyphens only">
            </label><br><br>
            <label>Website URL <small>(optional)</small><br>
                <input type="url" name="website_url"
                       style="width:100%;"></label><br><br>
            <label>Brand display name <small>(optional, defaults to name)</small><br>
                <input type="text" name="brand_name"
                       style="width:100%;"></label><br><br>
            <label>Brand CTA <small>(optional, e.g. "Visit us at...")</small><br>
                <input type="text" name="brand_cta"
                       style="width:100%;"></label><br><br>
            <button type="submit">Create Brand</button>
        </form>
    </body></html>
    """


def render_admin_brand_created(brand_name: str, slug: str) -> str:
    """
    Shows the newly created brand plus exact infrastructure lines
    to add manually — Caddyfile block and sites.yml entry.
    """
    caddy_block = (
        f"{slug}.{BASE_DOMAIN} {{\n"
        f"    reverse_proxy 127.0.0.1:{DASHBOARD_PORT}\n"
        f"}}"
    )
    sites_entry = (
        f"  - host: {slug}.{BASE_DOMAIN}\n"
        f"    port: {DASHBOARD_PORT}\n"
        f"    compose: docker-compose.yml\n"
        f"    service: dashboard"
    )
    return f"""
    <html><body style="font-family:sans-serif;padding:2rem;max-width:800px;">
        <p><a href="/admin">&larr; back to admin</a></p>
        <h1>Brand created: {brand_name}</h1>
        <p style="color:green;">
            ✅ Brand row and profile created in the database.
        </p>

        <h2>Next steps — add to infrastructure</h2>
        <p>Two manual steps are required to make
           <strong>{slug}.{BASE_DOMAIN}</strong> live:</p>

        <h3>1. Add to <code>deploy/caddy/Caddyfile</code></h3>
        <pre style="background:#f0f0f0;padding:1rem;border-radius:4px;">{caddy_block}</pre>

        <h3>2. Add to <code>deploy/sites.yml</code></h3>
        <pre style="background:#f0f0f0;padding:1rem;border-radius:4px;">{sites_entry}</pre>

        <h3>3. Reload Caddy</h3>
        <pre style="background:#f0f0f0;padding:1rem;border-radius:4px;">docker exec contentpilot_ssl_proxy caddy reload --config /etc/caddy/Caddyfile</pre>

        <p>Once those are done,
           <a href="https://{slug}.{BASE_DOMAIN}" target="_blank">
           {slug}.{BASE_DOMAIN}</a> will route to this dashboard,
           scoped to the {brand_name} brand.</p>

        <p><a href="/admin/brands/{slug}">Configure {brand_name} &rarr;</a></p>
    </body></html>
    """


def render_admin_brand_detail(
    brand: dict,
    credentials: dict,
    schedules: list[dict],
    flash: str = "",
) -> str:
    flash_html = f'<p style="color:green;font-weight:bold;">{flash}</p>' if flash else ""
    enabled_label = "enabled" if brand["enabled"] else "disabled"
    toggle_action = "disable" if brand["enabled"] else "enable"
    toggle_color = "red" if brand["enabled"] else "green"

    cred_rows = "".join(
        f"<tr><td>{ctype}</td>"
        f"<td style='color:gray;font-size:0.85em;'>saved</td></tr>"
        for ctype in credentials
    ) or "<tr><td colspan='2'><em>No credentials set yet.</em></td></tr>"

    sched_rows = "".join(
        f"<tr><td>{s['cron_expression']}</td>"
        f"<td style='color:green;'>active</td></tr>"
        for s in schedules
    ) or "<tr><td colspan='2'><em>No active schedules.</em></td></tr>"

    return f"""
    <html><body style="font-family:sans-serif;padding:2rem;max-width:800px;">
        <p><a href="/admin">&larr; back to admin</a>
           | <a href="/admin/logout">Logout</a></p>
        <h1>Brand: {brand['name']}</h1>
        {flash_html}

        <table border="1" cellpadding="6" style="margin-bottom:1rem;">
            <tr><td>ID</td><td>{brand['id']}</td></tr>
            <tr><td>Slug</td><td>{brand['slug']}</td></tr>
            <tr><td>Status</td>
                <td style="color:{'green' if brand['enabled'] else 'red'};">
                    {enabled_label}</td></tr>
            <tr><td>Dashboard URL</td>
                <td><a href="https://{brand['slug']}.{BASE_DOMAIN}" target="_blank">
                    {brand['slug']}.{BASE_DOMAIN}</a></td></tr>
        </table>

        <form method="post"
              action="/admin/brands/{brand['slug']}/{toggle_action}"
              style="display:inline;">
            <button type="submit" style="color:{toggle_color};">
                {toggle_action.capitalize()} brand
            </button>
        </form>

        <h2>Credentials</h2>
        <table border="1" cellpadding="6">
            <tr><th>Type</th><th>Status</th></tr>
            {cred_rows}
        </table>
        <p><small>Credentials are managed via the brand's own dashboard at
           <a href="https://{brand['slug']}.{BASE_DOMAIN}" target="_blank">
           {brand['slug']}.{BASE_DOMAIN}</a>.</small></p>

        <h2>Active schedules</h2>
        <table border="1" cellpadding="6">
            <tr><th>Cron (UTC)</th><th>Status</th></tr>
            {sched_rows}
        </table>
    </body></html>
    """


# ---------------------------------------------------------------------------
# Validation helpers (pure, testable without FastAPI)
# ---------------------------------------------------------------------------

def validate_brand_form(name: str, slug: str) -> list[str]:
    """Returns list of errors. Empty = valid."""
    errors = []
    name = name.strip()
    slug = slug.strip().lower()

    if not name:
        errors.append("Brand name is required.")
    if len(name) > 100:
        errors.append("Brand name must be 100 characters or fewer.")

    if not slug:
        errors.append("Slug is required.")
    if len(slug) > 50:
        errors.append("Slug must be 50 characters or fewer.")

    import re
    if slug and not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', slug) and len(slug) > 1:
        errors.append(
            "Slug must contain only lowercase letters, numbers, and hyphens, "
            "and cannot start or end with a hyphen."
        )
    if slug and len(slug) == 1 and not re.match(r'^[a-z0-9]$', slug):
        errors.append("Slug must be a lowercase letter or number.")

    # Reserved slugs that would conflict with existing routes
    reserved = {"admin", "api", "www", "mail", "smtp", "healthz", "static"}
    if slug in reserved:
        errors.append(f"'{slug}' is a reserved name and cannot be used as a slug.")

    return errors
