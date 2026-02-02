"""
Shared Settings for Inter-Service Configuration
"""
from pydantic_settings import BaseSettings


class SharedSettings(BaseSettings):
    """Settings used across multiple services"""

    # Service URLs
    auth_service_url: str = "http://localhost:8001"
    catalog_service_url: str = "http://localhost:8000"

    # Inter-service communication timeout (seconds)
    service_call_timeout: float = 5.0

    # Environment
    env: str = "dev"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


shared_settings = SharedSettings()
