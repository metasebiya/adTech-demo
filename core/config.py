from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AdTech Demo Platform"
    api_base_url: str = "http://127.0.0.1:8000"
    jwt_secret_key: str = "change-this-demo-secret"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    sqlite_db_path: str = str(Path("data") / "adtech_demo.db")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ADTECH_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
