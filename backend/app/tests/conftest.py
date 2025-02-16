from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from pydantic_settings import BaseSettings
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models.user import User
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers


class MockSettings(BaseSettings):
    PROJECT_NAME: str = "TestProject"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "test_secret_key_for_testing"
    POSTGRES_SERVER: str = "test_db"
    POSTGRES_USER: str = "test_user"
    POSTGRES_PASSWORD: str = "test_password"
    POSTGRES_DB: str = "test_db"
    FIRST_SUPERUSER: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin"
    USERS_OPEN_REGISTRATION: bool = True

    # Добавляем SMTP настройки
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = "smtp.example.com"
    SMTP_USER: str = "admin@example.com"
    SMTP_PASSWORD: str = "test_password"
    EMAILS_FROM_EMAIL: str = "test@example.com"
    EMAILS_FROM_NAME: str = "Test Project"
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "app/email-templates/build"
    EMAILS_ENABLED: bool = True
    EMAIL_TEST_USER: str = "test@example.com"


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(User)
        session.exec(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


@pytest.fixture(autouse=True)
def mock_settings():
    with patch("app.core.config.Settings", MockSettings):
        with patch("app.core.config.settings", MockSettings()):
            yield
