import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from src.modules.auth.models import User, UserRole
from src.modules.auth.schemas import UserCreate
from src.modules.auth.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from src.modules.auth.service import AuthService


def test_password_hashing():
    """Test that password hashing and verification works correctly."""
    password = "SuperSecretPassword123"
    hashed = get_password_hash(password)

    # Check hash is generated and verified
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_jwt_generation_and_decoding():
    """Test creating and decoding JWT access and refresh tokens."""
    subject = "user-uuid-12345"
    role = "trader"

    access_token = create_access_token(subject=subject, role=role)
    refresh_token = create_refresh_token(subject=subject, role=role)

    assert access_token is not None
    assert refresh_token is not None

    # Decode access token
    access_payload = decode_token(access_token)
    assert access_payload is not None
    assert access_payload["sub"] == subject
    assert access_payload["role"] == role

    # Decode refresh token
    refresh_payload = decode_token(refresh_token)
    assert refresh_payload is not None
    assert refresh_payload["sub"] == subject
    assert refresh_payload["role"] == role


@pytest.mark.asyncio
async def test_auth_service_registration_success():
    """Test that AuthService successfully registers a new user when details are unique."""
    mock_db = AsyncMock()

    # Mock repository methods
    # We mock UserRepository instances created inside AuthService
    service = AuthService(mock_db)

    # Mock get_by_username and get_by_email to return None (no duplicates)
    service.repo.get_by_username = AsyncMock(return_value=None)
    service.repo.get_by_email = AsyncMock(return_value=None)

    # Mock repository create method
    mock_user = User(
        id=1,
        username="john_doe",
        email="john@example.com",
        hashed_password="hashed_string",
        role=UserRole.TRADER,
    )
    service.repo.create = AsyncMock(return_value=mock_user)

    user_create = UserCreate(
        username="john_doe",
        email="john@example.com",
        password="SuperSecretPassword123",
        role=UserRole.TRADER,
    )

    registered_user = await service.register(user_create)

    assert registered_user.username == "john_doe"
    assert registered_user.email == "john@example.com"
    service.repo.get_by_username.assert_called_once_with("john_doe")
    service.repo.get_by_email.assert_called_once_with("john@example.com")
    service.repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_auth_service_registration_duplicate_username():
    """Test that AuthService raises HTTPException when username is already taken."""
    mock_db = AsyncMock()
    service = AuthService(mock_db)

    # Mock get_by_username to return an existing User object
    service.repo.get_by_username = AsyncMock(return_value=User(username="john_doe"))
    service.repo.get_by_email = AsyncMock(return_value=None)

    user_create = UserCreate(
        username="john_doe",
        email="john2@example.com",
        password="SuperSecretPassword123",
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.register(user_create)

    assert exc_info.value.status_code == 400
    assert "Username already registered" in exc_info.value.detail


@pytest.mark.asyncio
async def test_auth_service_registration_duplicate_email():
    """Test that AuthService raises HTTPException when email is already taken."""
    mock_db = AsyncMock()
    service = AuthService(mock_db)

    # Mock get_by_username to return None, and get_by_email to return an existing User
    service.repo.get_by_username = AsyncMock(return_value=None)
    service.repo.get_by_email = AsyncMock(return_value=User(email="john@example.com"))

    user_create = UserCreate(
        username="john_doe",
        email="john@example.com",
        password="SuperSecretPassword123",
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.register(user_create)

    assert exc_info.value.status_code == 400
    assert "Email address already registered" in exc_info.value.detail
