# modules/dashboard/facebook_form.py
"""
Pure data-transformation logic for the Facebook config edit form
(Step 5). Deliberately separated from app.py's route handlers so it
can be unit-tested without importing FastAPI.

Two concerns live here:
  1. Parsing submitted form fields into the shapes the DB expects
     (e.g. comma-separated text -> list)
  2. Merging a submitted credential update with the existing stored
     credential, so leaving the access token field blank means
     "keep what's already there", not "erase it"
"""
from __future__ import annotations


def parse_list_field(raw: str) -> list[str]:
    """'  #a, #b ,#c' -> ['#a', '#b', '#c']. Empty/whitespace-only -> []."""
    if not raw or not raw.strip():
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def list_field_to_text(items: list[str] | None) -> str:
    """Inverse of parse_list_field, for re-populating the form."""
    if not items:
        return ""
    return ", ".join(items)


def build_content_config(form: dict) -> dict:
    """
    Build the brand_content_config(facebook) JSON payload from raw
    form fields. Keys here define the full schema of what the
    dashboard can configure for Facebook content strategy.
    """
    return {
        "caption_topics": parse_list_field(form.get("caption_topics", "")),
        "hashtags": parse_list_field(form.get("hashtags", "")),
        "excluded_keywords": parse_list_field(form.get("excluded_keywords", "")),
        "location_text": form.get("location_text", "").strip(),
        "cta_text": form.get("cta_text", "").strip(),
        "image_source": form.get("image_source", "pexels").strip() or "pexels",
        "image_title_template": form.get("image_title_template", "").strip(),
        "image_subtitle_template": form.get("image_subtitle_template", "").strip(),
        "first_comment_template": form.get("first_comment_template", "").strip(),
        "tone": form.get("tone", "").strip(),
    }


def merge_credential_update(
    existing: dict, page_id: str, access_token: str
) -> dict:
    """
    Merge a submitted page_id/access_token into the existing credential
    dict. An empty access_token means "keep the existing token" — the
    edit form never pre-fills the real token, so an empty submission
    must not be treated as "the user wants to clear it".

    A non-empty page_id always overwrites (page_id isn't a secret,
    safe to show/replace directly).
    """
    merged = dict(existing)  # don't mutate caller's dict
    page_id = page_id.strip()
    access_token = access_token.strip()

    if page_id:
        merged["page_id"] = page_id

    if access_token:
        merged["access_token"] = access_token
    # else: keep whatever was already in `existing` (or absent, if none existed)

    return merged


def validate_content_config(config: dict) -> list[str]:
    """
    Returns a list of human-readable error strings. Empty list = valid.
    Server-side validation per project convention — never trust the
    client alone.
    """
    errors = []

    cta = config.get("cta_text", "")
    if len(cta) > 200:
        errors.append("CTA text must be 200 characters or fewer.")

    first_comment = config.get("first_comment_template", "")
    if len(first_comment) > 500:
        errors.append("First comment template must be 500 characters or fewer.")

    valid_sources = {"pexels", "pixabay", "unsplash"}
    source = config.get("image_source", "")
    if source and source not in valid_sources:
        errors.append(
            f"Image source '{source}' is not supported. "
            f"Choose one of: {', '.join(sorted(valid_sources))}."
        )

    if len(config.get("hashtags", [])) > 30:
        errors.append("Too many hashtags — keep it to 30 or fewer.")

    return errors
