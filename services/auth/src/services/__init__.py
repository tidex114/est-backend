"""
Auth Service - Main business logic for authentication
Orchestrates between repositories, domain logic, and external services
"""
from datetime import datetime, timezone
from typing import Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from services.auth.src.core.email_service import get_email_service
from services.auth.src.core.jwt_utils import create_access_token, create_refresh_token
from services.auth.src.domain.user import (
    User, VerificationToken, Email, Password,
    DomainError, ValidationError, InvalidEmail, WeakPassword,
    UserExists, InvalidCredentials, UserNotFound, VerificationFailed
)
from services.auth.src.models.user import UserORM
from services.auth.src.models.verification_token import VerificationTokenORM
from services.auth.src.repo import UserRepository
from services.auth.src.repo.verification_token import VerificationTokenRepository


class AuthService:
    """Service for authentication operations"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = VerificationTokenRepository(db)
        self.email_service = get_email_service()

    def register(self, email: str, password: str, role: str = "user") -> Tuple[UserORM, str]:
        """
        Register a new user

        Returns:
            Tuple of (UserORM, message)

        Raises:
            InvalidEmail: If email format is invalid
            WeakPassword: If password doesn't meet requirements
            UserExists: If user with email already exists
        """
        # Validate email doesn't exist
        if self.user_repo.exists_by_email(email):
            raise UserExists(f"User with email {email} already exists")

        # Create domain user (validates email and password)
        try:
            domain_user = User.create(
                email=email,
                password=password,
                role=role,
            )
        except (InvalidEmail, WeakPassword) as e:
            raise e

        # Save to database
        orm_user = self.user_repo.save(domain_user)

        # Create and send verification email
        if True:  # Email verification enabled by default
            token = VerificationToken.create(domain_user.id, validity_hours=24)
            self.token_repo.save(token)

            # Send verification email
            self.email_service.send_verification_email(
                email=email,
                verification_token=token.token,
                user_id=domain_user.id,
            )

        message = (
            "Registration successful. "
            "Check your email for verification link."
        )

        return orm_user, message

    def login(self, email: str, password: str) -> Tuple[UserORM, str, str]:
        """
        Login user with email and password

        Returns:
            Tuple of (UserORM, access_token, refresh_token)

        Raises:
            InvalidCredentials: If email doesn't exist or password is wrong
        """
        # Find user by email
        user = self.user_repo.get_by_email(email)
        if not user:
            raise InvalidCredentials("Invalid email or password")

        # Verify password
        if not Password.verify(password, user.password_hash):
            raise InvalidCredentials("Invalid email or password")

        # Generate tokens
        access_token = create_access_token(user.id, user.email, user.role)
        refresh_token = create_refresh_token(user.id, user.email)

        return user, access_token, refresh_token

    def verify_email(self, token_str: str) -> UserORM:
        """
        Verify user's email using verification token

        Returns:
            Updated UserORM

        Raises:
            VerificationFailed: If token is invalid or expired
        """
        # Get token from database
        token_orm = self.token_repo.get_by_token(token_str)
        if not token_orm:
            raise VerificationFailed("Invalid verification token")

        # Check if token is valid (not expired, not used)
        if token_orm.expires_at < datetime.now(timezone.utc):
            raise VerificationFailed("Verification token expired")

        if token_orm.used:
            raise VerificationFailed("Verification token already used")

        # Get user and update
        user = self.user_repo.get_by_id(token_orm.user_id)
        if not user:
            raise UserNotFound(f"User {token_orm.user_id} not found")

        # Mark user as verified
        updated_user = self.user_repo.update(
            token_orm.user_id,
            is_verified=True,
            updated_at=datetime.now(timezone.utc),
        )

        # Mark token as used
        self.token_repo.mark_as_used(token_str)

        return updated_user

    def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        """
        Create new access token using refresh token

        Returns:
            Tuple of (new_access_token, refresh_token)

        Raises:
            InvalidCredentials: If refresh token is invalid or expired
        """
        from services.auth.src.core.jwt_utils import verify_refresh_token

        # Verify refresh token
        payload = verify_refresh_token(refresh_token)
        if not payload:
            raise InvalidCredentials("Invalid or expired refresh token")

        # Get user
        user_id = UUID(payload["user_id"])
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound(f"User {user_id} not found")

        # Create new access token
        new_access_token = create_access_token(user.id, user.email, user.role)

        # Optionally create new refresh token (token rotation)
        # For now, we'll reuse the existing refresh token
        return new_access_token, refresh_token

    def get_user(self, user_id: UUID) -> UserORM:
        """Get user by ID"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound(f"User {user_id} not found")
        return user
