from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
# __file__ = .../services/catalog/src/core/settings.py
# parents[2] = .../services/catalog

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "EST Catalog"
    env: str = "dev"
    database_url: str


settings = Settings()
