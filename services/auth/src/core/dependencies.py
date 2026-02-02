"""
Auth Service Dependencies for FastAPI Dependency Injection
Database session and current user extraction
"""
from __future__ import annotations

from typing import Annotated, Generator, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from services.auth.src.core.db import SessionLocal
from services.auth.src.core.jwt_utils import verify_access_token


# ========== Database Session ==========

def get_db() -> Generator[Session, None, None]:
    """Provide database session with automatic cleanup"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DBSession = Annotated[Session, Depends(get_db)]


# ========== Authentication ==========

class CurrentUser:
    """Represents the authenticated user"""
    def __init__(self, user_id: UUID, email: str, role: str):
        self.user_id = user_id
        self.email = email
        self.role = role

    def is_admin(self) -> bool:
        return self.role == "admin"

    def is_partner(self) -> bool:
        return self.role == "partner"

    def is_user(self) -> bool:
        return self.role == "user"


def get_current_user(
    authorization: Annotated[Optional[str], Header()] = None,
) -> CurrentUser:
    """
    Extract current user from Authorization header (Bearer token)

    In production, this validates JWT and extracts claims.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    # Expected format: "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid auth scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    # Verify token
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        user_id = UUID(payload["user_id"])
        email = payload["email"]
        role = payload["role"]
        return CurrentUser(user_id=user_id, email=email, role=role)
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=401, detail=f"Invalid token claims: {e}")


def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Require admin role"""
    if not user.is_admin():
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


def require_partner(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Require partner role"""
    if not user.is_partner():
        raise HTTPException(status_code=403, detail="Partner role required")
    return user


def require_user(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Require user role"""
    if not user.is_user():
        raise HTTPException(status_code=403, detail="User role required")
    return user


# Type aliases
AuthUser = Annotated[CurrentUser, Depends(get_current_user)]
AdminUser = Annotated[CurrentUser, Depends(require_admin)]
PartnerUser = Annotated[CurrentUser, Depends(require_partner)]
CustomerUser = Annotated[CurrentUser, Depends(require_user)]
