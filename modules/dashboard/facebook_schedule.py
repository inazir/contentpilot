# modules/dashboard/facebook_schedule.py
"""
Phase 13D Step 1: Schedule configuration logic for Facebook posting.

Deliberately separated from app.py so it's testable without FastAPI.
Stored in brand_content_config (platform='facebook') under the key
'schedule' — same JSON blob, no schema change needed.

The scheduler wiring (making APScheduler actually read these values)
is a follow-up step once the real scheduler files are available.
This module only handles: parse form → validate → store/retrieve.

Schedule shape stored in config_json['schedule']:
{
    "frequency": "daily" | "twice_daily" | "weekly",
    "times": ["09:00", "17:00"],       # 24h UTC, list
    "active_days": [0,1,2,3,4],        # 0=Mon … 6=Sun
    "max_posts_per_day": 2
}
"""
from __future__ import annotations

VALID_FREQUENCIES = {"daily", "twice_daily", "weekly"}
VALID_DAYS = {0, 1, 2, 3, 4, 5, 6}

_FREQUENCY_DEFAULTS: dict[str, dict] = {
    "daily": {
        "times": ["09:00"],
        "active_days": [0, 1, 2, 3, 4],
        "max_posts_per_day": 1,
    },
    "twice_daily": {
        "times": ["09:00", "17:00"],
        "active_days": [0, 1, 2, 3, 4],
        "max_posts_per_day": 2,
    },
    "weekly": {
        "times": ["09:00"],
        "active_days": [0],
        "max_posts_per_day": 1,
    },
}

DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def parse_schedule_form(form: dict) -> dict:
    """
    Parse raw form fields into a validated schedule dict.

    Form fields expected:
        schedule_frequency   str  e.g. "daily"
        schedule_times       str  e.g. "09:00, 17:00"
        schedule_active_days str  e.g. "0,1,2,3,4"  (comma-sep ints)
        schedule_max_posts   str  e.g. "2"
    """
    frequency = form.get("schedule_frequency", "daily").strip()
    if frequency not in VALID_FREQUENCIES:
        frequency = "daily"

    raw_times = form.get("schedule_times", "").strip()
    times = _parse_times(raw_times) if raw_times else _FREQUENCY_DEFAULTS[frequency]["times"]

    raw_days = form.get("schedule_active_days", "").strip()
    active_days = _parse_days(raw_days) if raw_days else _FREQUENCY_DEFAULTS[frequency]["active_days"]

    try:
        max_posts = int(form.get("schedule_max_posts", "1"))
        max_posts = max(1, min(max_posts, 10))  # clamp 1–10
    except (ValueError, TypeError):
        max_posts = _FREQUENCY_DEFAULTS[frequency]["max_posts_per_day"]

    return {
        "frequency": frequency,
        "times": times,
        "active_days": active_days,
        "max_posts_per_day": max_posts,
    }


def validate_schedule(schedule: dict) -> list[str]:
    """Returns list of human-readable errors. Empty list = valid."""
    errors = []

    freq = schedule.get("frequency", "")
    if freq not in VALID_FREQUENCIES:
        errors.append(
            f"Invalid frequency '{freq}'. Choose: {', '.join(sorted(VALID_FREQUENCIES))}."
        )

    times = schedule.get("times", [])
    if not times:
        errors.append("At least one posting time is required.")
    for t in times:
        if not _is_valid_time(t):
            errors.append(f"Invalid time '{t}'. Use HH:MM format (24h UTC).")

    active_days = schedule.get("active_days", [])
    if not active_days:
        errors.append("At least one active day is required.")
    for d in active_days:
        if d not in VALID_DAYS:
            errors.append(f"Invalid day '{d}'. Use 0 (Mon) to 6 (Sun).")

    max_posts = schedule.get("max_posts_per_day", 1)
    if not isinstance(max_posts, int) or max_posts < 1 or max_posts > 10:
        errors.append("Max posts per day must be between 1 and 10.")

    if not errors and freq == "daily" and len(times) > 1:
        errors.append(
            "Frequency 'daily' allows only one posting time. "
            "Use 'twice_daily' for two times per day."
        )

    return errors


def schedule_to_display(schedule: dict | None) -> dict:
    """
    Convert stored schedule dict into display-friendly strings
    for rendering in the dashboard template.
    """
    if not schedule:
        return {
            "frequency": "daily",
            "times_text": "09:00",
            "active_days_text": "0,1,2,3,4",
            "max_posts": 1,
            "active_day_labels": "Mon, Tue, Wed, Thu, Fri",
        }

    active_days = schedule.get("active_days", [])
    day_labels = ", ".join(DAY_LABELS[d] for d in sorted(active_days) if 0 <= d <= 6)

    return {
        "frequency": schedule.get("frequency", "daily"),
        "times_text": ", ".join(schedule.get("times", ["09:00"])),
        "active_days_text": ",".join(str(d) for d in sorted(active_days)),
        "max_posts": schedule.get("max_posts_per_day", 1),
        "active_day_labels": day_labels or "(none)",
    }


def merge_schedule_into_config(content_config: dict, schedule: dict) -> dict:
    """
    Merge a validated schedule dict into the existing content_config blob.
    Returns a new dict — does not mutate the input.
    """
    merged = dict(content_config)
    merged["schedule"] = schedule
    return merged


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_times(raw: str) -> list[str]:
    """'09:00, 17:00' -> ['09:00', '17:00'], filtering invalid."""
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return [p for p in parts if _is_valid_time(p)]


def _parse_days(raw: str) -> list[int]:
    """'0,1,2,3,4' -> [0,1,2,3,4], filtering invalid."""
    result = []
    for part in raw.split(","):
        part = part.strip()
        try:
            d = int(part)
            if d in VALID_DAYS:
                result.append(d)
        except ValueError:
            pass
    return sorted(set(result))


def _is_valid_time(t: str) -> bool:
    """'09:00' -> True. '9am' -> False."""
    parts = t.split(":")
    if len(parts) != 2:
        return False
    try:
        h, m = int(parts[0]), int(parts[1])
        return 0 <= h <= 23 and 0 <= m <= 59
    except ValueError:
        return False
