import os
import smtplib
from email.message import EmailMessage
from typing import Optional, List

# CHANGE IF NEEDED: You can override these via Streamlit Secrets / Environment variables
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

# Forward all mail here by default (you asked for this):
DEFAULT_TO = "hudson@moniqueryan.com.au"
DEFAULT_FROM = os.getenv("DEFAULT_FROM", SMTP_USER or "no-reply@moniqueryan.com.au")

def send_email(subject: str, body: str, to: Optional[List[str]] = None, attachments: Optional[List[str]] = None):
    """Send an email with optional attachments.
    NOTE: For Gmail, enable 2FA and create an App Password. Set SMTP_USER/SMTP_PASS accordingly.
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = DEFAULT_FROM
    msg["To"] = ", ".join(to or [DEFAULT_TO])
    msg.set_content(body)

    for path in attachments or []:
        try:
            with open(path, "rb") as f:
                data = f.read()
            filename = os.path.basename(path)
            msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=filename)
        except Exception as e:
            print(f"[WARN] Attachment failed: {path} | {e}")

    if not SMTP_USER or not SMTP_PASS:
        print("[WARN] SMTP credentials not set. Email not sent.")
        return

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)
