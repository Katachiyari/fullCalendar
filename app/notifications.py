from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


def is_email_configured() -> bool:
    return bool(os.getenv("SMTP_HOST"))


def send_email(to_email: str, subject: str, body: str) -> None:
    """Envoi email best-effort.

    Si SMTP n'est pas configuré, la fonction ne fait rien.
    """
    host = os.getenv("SMTP_HOST")
    if not host:
        return

    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("SMTP_FROM", user or "no-reply@opshub.local")

    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(host, port, timeout=10) as smtp:
        smtp.ehlo()
        if os.getenv("SMTP_STARTTLS", "1") == "1":
            smtp.starttls()
            smtp.ehlo()
        if user and password:
            smtp.login(user, password)
        smtp.send_message(msg)
