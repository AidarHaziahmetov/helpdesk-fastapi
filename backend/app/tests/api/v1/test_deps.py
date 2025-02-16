from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
from uuid import uuid4

import jwt
import pytest
from fastapi import HTTPException
from sqlmodel import Session
from pydantic import ValidationError

from app.api.v1.deps import get_current_user, get_current_active_superuser
from app.core.config import settings
from app.core.security import ALGORITHM, create_access_token
from app.models.user import User


@pytest.fixture
def mock_session():
    return Mock(spec=Session)


@pytest.fixture
def active_user():
    return User(
        id=uuid4(),
        email="test@example.com",
        hashed_password="hashed",
        is_active=True,
        is_superuser=False
    )


@pytest.fixture
def superuser():
    return User(
        id=uuid4(),
        email="admin@example.com",
        hashed_password="hashed",
        is_active=True,
        is_superuser=True
    )


@pytest.fixture
def inactive_user():
    return User(
        id=uuid4(),
        email="inactive@example.com",
        hashed_password="hashed",
        is_active=False,
        is_superuser=False
    )


def test_get_current_user_valid_token(mock_session, active_user):
    # Подготовка
    token = create_access_token(
        subject=str(active_user.id),
        expires_delta=timedelta(minutes=15)
    )
    mock_session.get.return_value = active_user

    # Выполнение
    user = get_current_user(mock_session, token)

    # Проверка
    assert user == active_user
    mock_session.get.assert_called_once()


def test_get_current_user_invalid_token(mock_session):
    # Подготовка
    invalid_token = "invalid_token"

    # Проверка
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(mock_session, invalid_token)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Could not validate credentials"


def test_get_current_user_expired_token(mock_session):
    # Подготовка
    expired_time = datetime.now(timezone.utc) - timedelta(days=1)
    payload = {"exp": expired_time, "sub": "user_id"}
    expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)

    # Проверка
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(mock_session, expired_token)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Could not validate credentials"


def test_get_current_user_invalid_token_payload(mock_session):
    # Подготовка
    # Создаем токен с payload, который вызовет ValidationError при десериализации в TokenPayload
    invalid_payload = {
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        "sub": {"invalid": "format"}  # TokenPayload ожидает str, но получает dict
    }
    invalid_token = jwt.encode(invalid_payload, settings.SECRET_KEY, algorithm=ALGORITHM)

    # Проверка
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(mock_session, invalid_token)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Could not validate credentials"


def test_get_current_user_user_not_found(mock_session):
    # Подготовка
    token = create_access_token(
        subject="nonexistent_user_id",
        expires_delta=timedelta(minutes=15)
    )
    mock_session.get.return_value = None

    # Проверка
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(mock_session, token)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


def test_get_current_user_inactive_user(mock_session, inactive_user):
    # Подготовка
    token = create_access_token(
        subject=str(inactive_user.id),
        expires_delta=timedelta(minutes=15)
    )
    mock_session.get.return_value = inactive_user

    # Проверка
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(mock_session, token)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Inactive user"


def test_get_current_active_superuser_valid(superuser):
    # Выполнение
    result = get_current_active_superuser(superuser)

    # Проверка
    assert result == superuser


def test_get_current_active_superuser_not_superuser(active_user):
    # Проверка
    with pytest.raises(HTTPException) as exc_info:
        get_current_active_superuser(active_user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "The user doesn't have enough privileges"