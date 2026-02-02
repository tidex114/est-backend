"""
User Repository - Database access layer for users
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.auth.src.models.user import UserORM
from services.auth.src.domain.user import User, Email, InvalidEmail


class UserRepository:
    """Repository for User aggregate"""

    def __init__(self, db: Session):
        self.db = db

    def save(self, user: User) -> UserORM:
        """Save user to database"""
        orm = UserORM(
            id=user.id,
            email=user.email.value,
            password_hash=user.password_hash,
            role=user.role,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return orm

    def get_by_email(self, email: str) -> Optional[UserORM]:
        """Get user by email"""
        query = select(UserORM).where(UserORM.email == email.lower())
        return self.db.scalars(query).first()

    def get_by_id(self, user_id: UUID) -> Optional[UserORM]:
        """Get user by ID"""
        return self.db.get(UserORM, user_id)

    def update(self, user_id: UUID, **kwargs) -> Optional[UserORM]:
        """Update user fields"""
        user = self.get_by_id(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: UUID) -> bool:
        """Delete user"""
        user = self.get_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True

    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        return self.get_by_email(email) is not None
