import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import emails  # type: ignore
import jwt
from jinja2 import Template
from jwt.exceptions import InvalidTokenError

from app.core import security
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    # Try to load compiled HTML template, fallback to MJML source if missing
    base = Path(__file__).parent / "email-templates"
    html_path = base / "build" / template_name
    if html_path.exists():
        template_str = html_path.read_text()
    else:
        # Fallback: look for MJML source with same name
        mjml_name = Path(template_name).with_suffix('.mjml').name
        mjml_path = base / "src" / mjml_name
        if not mjml_path.exists():
            # Neither HTML nor MJML exist
            raise FileNotFoundError(f"Email template not found: {template_name}")
        logger.warning(f"HTML template '{template_name}' not found, falling back to MJML '{mjml_name}'")
        template_str = mjml_path.read_text()
    # Render with Jinja2
    html_content = Template(template_str).render(context)
    return html_content


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    assert settings.emails_enabled, "no provided configuration for email variables"
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, smtp=smtp_options)
    logger.info(f"send email result: {response}")


def generate_test_email(email_to: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.FRONTEND_HOST,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None
def send_test_email(
    *,
    email_to: str,
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    smtp_tls: bool = True,
    from_email: str,
    from_name: str,
) -> None:
    """Send a test email using custom SMTP settings with improved debugging"""
    subject = f"{from_name} - Email Configuration Test"
    html_content = render_email_template(
        template_name="test_email.html",
        context={
            "project_name": from_name,
            "email": email_to
        },
    )
    
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(from_name, from_email),
    )
    
    smtp_options = {
        "host": smtp_host,
        "port": smtp_port,
        "user": smtp_user,
        "password": smtp_password,
        "debug": 1  # Enable SMTP level debugging
    }
    
    # Configure TLS properly
    if smtp_tls:
        smtp_options["tls"] = True
    
    try:
        logger.info(f"Sending test email to {email_to} via {smtp_host}:{smtp_port}")
        response = message.send(to=email_to, smtp=smtp_options)
        
        # More detailed logging
        logger.info(f"Test email result: {response}")
        logger.info(f"Response status: {getattr(response, 'status_code', None)}")
        logger.info(f"Response body: {getattr(response, 'body', None)}")
        
        if not response.status_code or response.status_code != 250:
            logger.error(f"Email sending failed with status: {getattr(response, 'status_code', 'unknown')}")
            
        return response
    except Exception as e:
        logger.error(f"Exception sending test email: {str(e)}", exc_info=True)
        raise