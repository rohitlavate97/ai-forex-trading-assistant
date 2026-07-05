from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.auth.models import User
from src.modules.auth.repository import UserRepository
from src.modules.auth.schemas import UserCreate, Token
from src.modules.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


class AuthService:
    """Service layer handling registration, authentication, and token operations."""

    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, schema: UserCreate) -> User:
        """Register a new user after verifying unique credentials."""
        # Check duplicate username
        existing_user = await self.repo.get_by_username(schema.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        # Check duplicate email
        existing_email = await self.repo.get_by_email(schema.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address already registered",
            )

        # Create user
        hashed_password = get_password_hash(schema.password)
        new_user = User(
            username=schema.username,
            email=schema.email,
            hashed_password=hashed_password,
            role=schema.role or "trader",
        )
        return await self.repo.create(new_user)

    async def authenticate(self, username_or_email: str, password: str) -> User:
        """Authenticate user login credentials."""
        # Try fetch by username, fallback to email
        user = await self.repo.get_by_username(username_or_email)
        if not user:
            user = await self.repo.get_by_email(username_or_email)

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username, email, or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated",
            )

        return user

    def generate_tokens(self, user: User) -> Token:
        """Generate JWT Access and Refresh tokens."""
        access_token = create_access_token(subject=user.uuid, role=user.role.value)
        refresh_token = create_refresh_token(subject=user.uuid, role=user.role.value)
        return Token(access_token=access_token, refresh_token=refresh_token)

    async def refresh_token(self, refresh_token: str) -> Token:
        """Refresh JWT access token using a valid refresh token."""
        payload = decode_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        user = await self.repo.get_by_uuid(user_uuid)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        return self.generate_tokens(user)
