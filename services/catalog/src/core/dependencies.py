"""
Core dependencies for FastAPI dependency injection.
Includes database session management and authentication stubs.
"""
from __future__ import annotations

from typing import Annotated, Literal, Generator
from uuid import UUID

from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from services.catalog.src.core.db import SessionLocal


# ========== Database Session ==========

def get_db() -> Generator[Session, None, None]:
    """Provide database session with automatic cleanup"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DBSession = Annotated[Session, Depends(get_db)]


# ========== Authentication Stubs ==========
# In production, this would validate JWT tokens with the Auth service
# For now, we'll use simple header-based auth for demonstration

Role = Literal["user", "partner", "admin"]


class CurrentUser:
    """Represents the authenticated user"""
    def __init__(self, user_id: UUID, email: str, role: Role, place_id: UUID | None = None):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.place_id = place_id  # Only set for partners

    def is_admin(self) -> bool:
        return self.role == "admin"

    def is_partner(self) -> bool:
        return self.role == "partner"

    def is_user(self) -> bool:
        return self.role == "user"

    def can_manage_place(self, place_id: UUID) -> bool:
        """Check if user can manage this place"""
        return self.role == "partner" and self.place_id == place_id


def get_current_user(
    x_user_id: str = Header(..., description="User ID"),
    x_user_email: str = Header(..., description="User email"),
    x_user_role: Role = Header(..., description="User role: user, partner, or admin"),
    x_place_id: str | None = Header(None, description="Place ID (for partners)"),
) -> CurrentUser:
    """
    Extract current user from headers.

    In production, replace this with JWT token validation from Auth service:
    - Parse Authorization: Bearer <token>
    - Call auth service to validate token
    - Extract claims (user_id, email, role, place_id)
    - Return CurrentUser

    For now, we trust headers for development/testing.
    """
    try:
        user_id = UUID(x_user_id)
        place_id = UUID(x_place_id) if x_place_id else None
        return CurrentUser(
            user_id=user_id,
            email=x_user_email,
            role=x_user_role,
            place_id=place_id
        )
    except (ValueError, AttributeError) as e:
        raise HTTPException(status_code=401, detail=f"Invalid user credentials: {e}")


def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Require admin role"""
    if not user.is_admin():
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


def require_partner(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Require partner role"""
    if not user.is_partner():
        raise HTTPException(status_code=403, detail="Partner role required")
    if not user.place_id:
        raise HTTPException(status_code=403, detail="Partner must have associated place")
    return user


def require_user(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Require user role (customer)"""
    if not user.is_user():
        raise HTTPException(status_code=403, detail="User role required")
    return user


# Type aliases for dependencies
AuthUser = Annotated[CurrentUser, Depends(get_current_user)]
AdminUser = Annotated[CurrentUser, Depends(require_admin)]
PartnerUser = Annotated[CurrentUser, Depends(require_partner)]
CustomerUser = Annotated[CurrentUser, Depends(require_user)]
