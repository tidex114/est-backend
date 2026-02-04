"""
Auth Service Configuration
Extends base settings with JWT and email configuration
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Build path to .env file - goes up to project root
ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Service identity
    app_name: str = "EST Auth"
    env: str = "dev"

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/est_auth"

    # JWT Configuration
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # Email Configuration
    smtp_server: str = "localhost"
    smtp_port: int = 1025
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@est.local"
    email_verification_enabled: bool = True

    # Service URLs (for inter-service communication)
    auth_service_url: str = "http://localhost:8001"
    catalog_service_url: str = "http://localhost:8000"


settings = Settings()
