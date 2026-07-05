from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.auth.models import User, UserRole


class UserRepository:
    """Repository pattern implementation for User database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Fetch user by primary key ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_by_uuid(self, user_uuid: str) -> Optional[User]:
        """Fetch user by public UUID."""
        result = await self.db.execute(select(User).where(User.uuid == user_uuid))
        return result.scalars().first()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Fetch user by username."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch user by email address."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Fetch multiple users with pagination."""
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, user: User) -> User:
        """Add a new user to the database."""
        self.db.add(user)
        await self.db.flush()  # Populates auto-incremented fields like ID
        return user

    async def update(self, user: User) -> User:
        """Update an existing user in the database."""
        self.db.add(user)
        await self.db.flush()
        return user
