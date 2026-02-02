"""
Auth Schemas - Request and Response models for API
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ========== Request Schemas ==========

class UserRegister(BaseModel):
    """User registration request"""
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password (min 8 chars, must include uppercase, lowercase, digit)")
    role: str = Field(default="user", description="user or partner (admin created manually)")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        valid_roles = {"user", "partner"}
        if v not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of {valid_roles}")
        return v


class UserLogin(BaseModel):
    """User login request"""
    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class VerifyEmail(BaseModel):
    """Email verification request"""
    token: str = Field(..., description="Verification token from email")


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")


# ========== Response Schemas ==========

class TokenResponse(BaseModel):
    """Token pair response"""
    access_token: str = Field(..., description="JWT access token (15 min expiry)")
    refresh_token: str = Field(..., description="JWT refresh token (7 day expiry)")
    token_type: str = Field(default="bearer")
    expires_in: int = Field(description="Access token expiry in seconds")


class UserOut(BaseModel):
    """User response (public info only)"""
    id: UUID
    email: str
    role: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Complete authentication response"""
    user: UserOut
    tokens: TokenResponse


class RegisterResponse(BaseModel):
    """Registration response"""
    user: UserOut
    message: str = "Registration successful. Check your email for verification link."


class LoginResponse(BaseModel):
    """Login response"""
    user: UserOut
    tokens: TokenResponse


class VerifyEmailResponse(BaseModel):
    """Email verification response"""
    message: str = "Email verified successfully"
    user: UserOut
