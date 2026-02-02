"""
Auth Domain Layer
Contains core business logic and domain models for authentication.
This layer has zero dependencies on infrastructure (database, HTTP, etc).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
import re
from typing import Optional

import bcrypt


# ========== Domain Exceptions ==========

class DomainError(Exception):
    """Base domain error"""
    pass


class ValidationError(DomainError):
    """Data validation error"""
    pass


class InvalidEmail(ValidationError):
    """Invalid email format"""
    pass


class WeakPassword(ValidationError):
    """Password doesn't meet requirements"""
    pass


class UserExists(DomainError):
    """User with this email already exists"""
    pass


class InvalidCredentials(DomainError):
    """Invalid email or password"""
    pass


class UserNotFound(DomainError):
    """User not found"""
    pass


class VerificationFailed(DomainError):
    """Email verification failed"""
    pass


class InvalidToken(DomainError):
    """Invalid or expired token"""
    pass


# ========== Value Objects ==========

@dataclass(frozen=True)
class Email:
    """Email value object with validation"""
    value: str

    def __post_init__(self):
        # Simple email validation (RFC 5322 simplified)
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, self.value):
            raise InvalidEmail(f"Invalid email format: {self.value}")

    @property
    def email(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Password:
    """Password value object with validation and hashing"""
    value: str

    def __post_init__(self):
        # Password requirements:
        # - At least 8 characters
        # - At least one uppercase letter
        # - At least one lowercase letter
        # - At least one digit
        if len(self.value) < 8:
            raise WeakPassword("Password must be at least 8 characters")

        if not any(c.isupper() for c in self.value):
            raise WeakPassword("Password must contain at least one uppercase letter")

        if not any(c.islower() for c in self.value):
            raise WeakPassword("Password must contain at least one lowercase letter")

        if not any(c.isdigit() for c in self.value):
            raise WeakPassword("Password must contain at least one digit")

    def hash(self) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(self.value.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify(password_plain: str, password_hash: str) -> bool:
        """Verify plain password against hash"""
        return bcrypt.checkpw(password_plain.encode(), password_hash.encode())


# ========== Domain Aggregates ==========

@dataclass
class User:
    """
    User aggregate - represents a user in the system.

    Can have roles: "user" (customer), "partner" (restaurant), "admin"
    """
    id: UUID
    email: Email
    password_hash: str
    role: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        email: str,
        password: str,
        role: str = "user",
    ) -> User:
        """Factory method to create new user with validation"""
        # Validate email
        email_obj = Email(email)  # Raises InvalidEmail if invalid

        # Validate password
        password_obj = Password(password)  # Raises WeakPassword if invalid

        # Validate role
        valid_roles = {"user", "partner", "admin"}
        if role not in valid_roles:
            raise ValidationError(f"Invalid role: {role}. Must be one of {valid_roles}")

        # Create user
        now = datetime.now(timezone.utc)
        return User(
            id=uuid4(),
            email=email_obj,
            password_hash=password_obj.hash(),
            role=role,
            is_verified=False,
            created_at=now,
            updated_at=now,
        )

    def verify_email(self) -> None:
        """Mark user email as verified"""
        if self.is_verified:
            raise ValidationError("User already verified")

        # Create new instance with updated fields
        # (User is immutable from the perspective of external code)
        object.__setattr__(self, 'is_verified', True)
        object.__setattr__(self, 'updated_at', datetime.now(timezone.utc))

    def verify_password(self, password: str) -> bool:
        """Verify that provided password matches stored hash"""
        return Password.verify(password, self.password_hash)


@dataclass
class VerificationToken:
    """
    Email verification token.
    Represents a single-use token sent to user's email.
    """
    token: str
    user_id: UUID
    expires_at: datetime
    used: bool = False

    @staticmethod
    def create(user_id: UUID, validity_hours: int = 24) -> VerificationToken:
        """Create new verification token"""
        import secrets
        token = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        expires_at = datetime.fromtimestamp(
            now.timestamp() + (validity_hours * 3600),
            tz=timezone.utc
        )

        return VerificationToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
            used=False,
        )

    def is_valid(self, current_time: Optional[datetime] = None) -> bool:
        """Check if token is still valid (not expired and not used)"""
        if self.used:
            return False

        check_time = current_time or datetime.now(timezone.utc)
        return check_time < self.expires_at

    def mark_as_used(self) -> None:
        """Mark token as used (single-use)"""
        if self.used:
            raise ValidationError("Token already used")
        object.__setattr__(self, 'used', True)
