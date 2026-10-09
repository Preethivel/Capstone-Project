"""Non-blocking Resend email service."""

import logging
import os
from typing import Iterable

import requests

logger = logging.getLogger(__name__)
RESEND_URL = "https://api.resend.com/emails"


def send_email(*, to: str | Iterable[str], subject: str, html: str) -> bool:
    api_key = os.getenv("RESEND_API_KEY", "").strip()
    from_email = os.getenv("RESEND_FROM_EMAIL", "").strip()
    if not api_key or not from_email:
        logger.info("Resend is not configured; skipping email")
        return False

    recipients = [to] if isinstance(to, str) else list(to)
    try:
        response = requests.post(
            RESEND_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"from": from_email, "to": recipients, "subject": subject, "html": html},
            timeout=10,
        )
        response.raise_for_status()
        return True
    except requests.RequestException as exc:
        logger.warning("Resend email failed: %s", type(exc).__name__)
        return False


def send_welcome_email(user_name: str, recipient: str) -> bool:
    return send_email(
        to=recipient,
        subject="Welcome to LearnVerse",
        html=(
            f"<p>Hi {user_name},</p>"
            "<p>Welcome to LearnVerse. Your learning journey starts here.</p>"
            "<p>Explore a course and take your next step.</p>"
        ),
    )


def send_enrollment_confirmation(user_name: str, recipient: str, course_title: str) -> bool:
    return send_email(
        to=recipient,
        subject=f"You are enrolled in {course_title}",
        html=(
            f"<p>Hi {user_name},</p>"
            f"<p>Your enrollment in <strong>{course_title}</strong> is confirmed.</p>"
            "<p>Open LearnVerse whenever you are ready to learn.</p>"
        ),
    )
