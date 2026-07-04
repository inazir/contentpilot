# modules/dashboard/facebook_csv.py
"""
Phase 13D Step 2: CSV upload parsing for caption topics.

Pure logic module — no FastAPI, no file I/O beyond parsing bytes.
The route handler in app.py receives the uploaded bytes and passes
them here for parsing and validation.

Accepted CSV formats:
    One topic per row, single column:
        Anmeldung process
        Health insurance for expats
        Opening a bank account

    Or with a header row (header is auto-detected and skipped):
        topic
        Anmeldung process
        Health insurance for expats

Topics are merged with any existing caption_topics in content_config
(union, deduplication) unless replace=True is passed, in which case
the uploaded list fully replaces the existing one.
"""
from __future__ import annotations

import csv
import io

MAX_TOPICS = 100
MAX_TOPIC_LENGTH = 300


def parse_csv_bytes(raw: bytes, encoding: str = "utf-8") -> tuple[list[str], list[str]]:
    """
    Parse raw CSV bytes into a list of topic strings.

    Returns (topics, errors):
        topics: list of cleaned, non-empty topic strings
        errors: list of human-readable problems found (non-fatal)

    Raises ValueError only for completely unparseable input
    (e.g. binary garbage, wrong encoding).
    """
    errors: list[str] = []

    try:
        text = raw.decode(encoding).strip()
    except (UnicodeDecodeError, LookupError):
        try:
            text = raw.decode("latin-1").strip()
        except Exception:
            raise ValueError("Could not decode the uploaded file. Please save it as UTF-8.")

    if not text:
        raise ValueError("The uploaded file is empty.")

    reader = csv.reader(io.StringIO(text))
    rows = list(reader)

    if not rows:
        raise ValueError("No rows found in the uploaded file.")

    # Auto-detect and skip header row: if the first row's first cell
    # looks like a header (contains "topic", "title", "subject", etc.)
    # skip it, otherwise treat it as data.
    first_cell = rows[0][0].strip().lower() if rows[0] else ""
    header_words = {"topic", "topics", "title", "subject", "caption", "content"}
    start_row = 1 if first_cell in header_words else 0

    topics: list[str] = []
    for i, row in enumerate(rows[start_row:], start=start_row + 1):
        if not row:
            continue
        topic = row[0].strip()
        if not topic:
            continue
        if len(topic) > MAX_TOPIC_LENGTH:
            errors.append(
                f"Row {i}: topic truncated to {MAX_TOPIC_LENGTH} chars "
                f"(was {len(topic)} chars)."
            )
            topic = topic[:MAX_TOPIC_LENGTH]
        topics.append(topic)

    if len(topics) > MAX_TOPICS:
        errors.append(
            f"File contains {len(topics)} topics — only the first "
            f"{MAX_TOPICS} will be used."
        )
        topics = topics[:MAX_TOPICS]

    return topics, errors


def merge_topics(
    existing: list[str],
    uploaded: list[str],
    replace: bool = False,
) -> list[str]:
    """
    Merge uploaded topics into existing list.

    replace=False (default): union, deduplicated, existing order preserved.
    replace=True: uploaded list fully replaces existing.
    """
    if replace:
        return list(dict.fromkeys(uploaded))  # deduplicate, preserve order

    combined = list(existing) + [t for t in uploaded if t not in existing]
    return combined[:MAX_TOPICS]


def validate_topics_list(topics: list[str]) -> list[str]:
    """Returns list of errors. Empty = valid."""
    errors = []
    if not topics:
        errors.append("Topics list cannot be empty after upload.")
    if len(topics) > MAX_TOPICS:
        errors.append(f"Too many topics ({len(topics)}). Maximum is {MAX_TOPICS}.")
    return errors
