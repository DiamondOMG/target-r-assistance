import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv

# Load .env from current dir or MCP_SERVER/.env
load_dotenv()
_env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(_env_path):
    load_dotenv(dotenv_path=_env_path)


def send_email(
    to: Union[List[str], str],
    subject: str,
    body: str,
    is_html: bool = False,
    cc: Optional[List[str]] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
) -> Dict[str, Any]:
    """ส่งอีเมลผ่าน Gmail SMTP"""
    sender_email = user or os.getenv("GMAIL_USER", "").strip()
    app_password = password or os.getenv("GMAIL_APP_PASSWORD", "").strip()

    if not sender_email or not app_password:
        raise ValueError("CONFIG_ERROR: GMAIL_USER and GMAIL_APP_PASSWORD must be configured")

    if isinstance(to, str):
        recipients = [e.strip() for e in to.split(",") if e.strip()]
    elif isinstance(to, list):
        recipients = [str(e).strip() for e in to if str(e).strip()]
    else:
        raise ValueError("INVALID_INPUT: 'to' must be a list of emails or a comma-separated string")

    if not recipients:
        raise ValueError("INVALID_INPUT: At least one recipient email is required")

    if not subject or not subject.strip():
        raise ValueError("INVALID_INPUT: Email subject must not be empty")

    if not body:
        raise ValueError("INVALID_INPUT: Email body must not be empty")

    # Prepare message
    msg = MIMEMultipart("alternative")
    msg["From"] = f"Jarvis Assistant <{sender_email}>"
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject.strip()

    cc_list = []
    if cc:
        if isinstance(cc, list):
            cc_list = [str(e).strip() for e in cc if str(e).strip()]
        elif isinstance(cc, str):
            cc_list = [e.strip() for e in cc.split(",") if e.strip()]
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)

    all_recipients = recipients + cc_list

    subtype = "html" if is_html else "plain"
    part = MIMEText(body, subtype, "utf-8")
    msg.attach(part)

    # Clean password (remove spaces)
    cleaned_password = app_password.replace(" ", "")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20.0) as server:
            server.login(sender_email, cleaned_password)
            server.sendmail(sender_email, all_recipients, msg.as_string())
    except smtplib.SMTPAuthenticationError as e:
        raise RuntimeError(f"SMTP_AUTH_ERROR: Authentication failed for {sender_email}: {e}")
    except Exception as e:
        raise RuntimeError(f"SEND_FAILED: Failed to send email: {e}")

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    return {
        "source": "gmail_smtp",
        "status": "success",
        "sender": sender_email,
        "to": recipients,
        "cc": cc_list,
        "subject": subject.strip(),
        "is_html": is_html,
        "timestamp": now_iso,
    }

