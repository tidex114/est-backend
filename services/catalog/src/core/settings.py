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

    app_name: str = "EST Catalog"
    env: str = "dev"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/est_catalog"


settings = Settings()
