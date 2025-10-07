"""
Application configuration using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "ONLSuggest"
    debug: bool = False
    environment: str = "development"

    # Database
    database_url: str = "postgresql+asyncpg://onlsuggest:devpassword@localhost:5433/onlsuggest"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # API Rate Limiting
    rate_limit_per_minute: int = 100

    # CORS
    cors_origins: list[str] = ["http://localhost:8000", "http://localhost:3000"]

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Create global settings instance
settings = Settings()
