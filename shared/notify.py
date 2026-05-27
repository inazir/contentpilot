"""
Lightweight notification layer for ContentPilot.

Currently supports:
- Email (via SMTP — reuses existing SMTP config from legacy)
- Telegram (via Bot API)

Notifications fire only for fatal/repeated failures.
Add providers here. Nothing else changes.
"""

import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

def _send_email(subject: str, body: str) -> bool:
    host = os.getenv("SMTP_HOST", "").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASS", "").strip()
    to_addr = os.getenv("NOTIFY_EMAIL_TO", "").strip()

    if not all([host, user, password, to_addr]):
        logger.debug("Email notification skipped — SMTP not fully configured")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr
    msg.set_content(body)

    try:
        with smtplib.SMTP(host, port, timeout=15) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(msg)
        logger.info("Notification email sent | to=%s | subject=%r", to_addr, subject)
        return True
    except Exception as exc:
        logger.warning("Failed to send notification email: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------

def _send_telegram(message: str) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    if not token or not chat_id:
        logger.debug("Telegram notification skipped — not configured")
        return False

    try:
        import requests
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
            timeout=10,
        )
        if response.ok:
            logger.info("Telegram notification sent | chat_id=%s", chat_id)
            return True
        logger.warning(
            "Telegram notification failed | status=%d | body=%s",
            response.status_code, response.text[:200],
        )
        return False
    except Exception as exc:
        logger.warning("Failed to send Telegram notification: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def notify_failure(module_name: str, error: str, run_id: str = "") -> None:
    """
    Send failure notification via all configured channels.
    Never raises — notification failure must not crash the job.
    """
    subject = f"[ContentPilot] FAILED: {module_name}"
    body = (
        f"Module:  {module_name}\n"
        f"Run ID:  {run_id}\n"
        f"Error:   {error}\n"
    )

    _send_email(subject, body)
    _send_telegram(f"<b>ContentPilot FAILED</b>\nModule: {module_name}\nError: {error}")
