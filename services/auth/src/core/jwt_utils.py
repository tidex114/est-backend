"""
JWT Token Management Utilities
Handles encoding and decoding JWT tokens with user claims
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import jwt

from services.auth.src.core.settings import settings


def create_access_token(user_id: UUID, email: str, role: str) -> str:
    """
    Create a short-lived access token (15 minutes by default)

    Claims:
    - user_id: User's UUID
    - email: User's email
    - role: User's role (user, partner, admin)
    - type: "access" (for distinguishing from refresh tokens)
    - iat: Issued at
    - exp: Expiration time
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    payload = {
        "user_id": str(user_id),
        "email": email,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    return token


def create_refresh_token(user_id: UUID, email: str) -> str:
    """
    Create a long-lived refresh token (7 days by default)

    Claims:
    - user_id: User's UUID
    - email: User's email
    - type: "refresh"
    - iat: Issued at
    - exp: Expiration time
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.jwt_refresh_token_expire_days)

    payload = {
        "user_id": str(user_id),
        "email": email,
        "type": "refresh",
        "iat": now,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    return token


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token
    Returns decoded payload or None if invalid/expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token


def verify_access_token(token: str) -> Optional[dict]:
    """Verify token is valid access token and return claims"""
    payload = decode_token(token)
    if not payload:
        return None

    if payload.get("type") != "access":
        return None  # Not an access token

    return payload


def verify_refresh_token(token: str) -> Optional[dict]:
    """Verify token is valid refresh token and return claims"""
    payload = decode_token(token)
    if not payload:
        return None

    if payload.get("type") != "refresh":
        return None  # Not a refresh token

    return payload
