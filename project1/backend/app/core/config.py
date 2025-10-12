"""
Application configuration
BMAD-compliant settings management
"""
import os
from typing import Optional


class Settings:
    """Application settings from environment variables"""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # KOOP API
    KOOP_API_URL: str = os.getenv(
        "KOOP_API_URL",
        "https://onl-suggester.koop-innovatielab-tst.test5.s15m.nl/api/suggest"
    )

    # Admin credentials
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

    # API settings
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "ONLSuggest"
    VERSION: str = "1.0.0"

    # CORS
    CORS_ORIGINS: list = ["*"]  # Configure for production

    # Performance
    QUERY_MIN_LENGTH: int = 2
    MAX_SUGGESTIONS: int = 5
    DEBOUNCE_MS: int = 150


settings = Settings()
