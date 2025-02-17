import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import emails  # type: ignore
from fastapi import BackgroundTasks
from jinja2 import Template

from app.core.config import settings
from app.models.appeal import Appeal
from app.models.organization import Organization

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent.parent / "email-templates" / "build" / template_name
    ).read_text()
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


def send_new_appeal_email(*, appeal: Appeal, organization: Organization) -> None:
    """
    Отправка email о новом обращении
    """
    if not settings.emails_enabled:
        return

    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Новое обращение #{appeal.id}"

    # Формируем контекст для шаблона
    context = {
        "project_name": project_name,
        "appeal_id": appeal.id,
        "appeal_title": appeal.title,
        "appeal_description": appeal.description,
        "organization_name": organization.name,
        "created_at": appeal.created_at,
        "link": f"{settings.FRONTEND_HOST}/appeals/{appeal.id}",
    }

    # Рендерим HTML из шаблона
    html_content = render_email_template(
        template_name="new_appeal.html",
        context=context,
    )

    # Отправляем email
    if organization.email:
        send_email(
            email_to=organization.email,
            subject=subject,
            html_content=html_content,
        )


def send_new_status_email(
    background_tasks: BackgroundTasks,
    appeal: Appeal,
    old_status: str,
    new_status: str,
) -> None:
    """
    Отправляет email об изменении статуса обращения
    """
    if not settings.emails_enabled:
        return

    # Используем background_tasks для асинхронной отправки
    message = f"[MOCK] Отправка email об изменении статуса обращения {appeal.id} с {old_status} на {new_status}"
    background_tasks.add_task(print, message)
