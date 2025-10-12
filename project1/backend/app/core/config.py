"""
Application configuration
BMAD-compliant settings management
"""
import os


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
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "onlsuggest2024")

    # API settings
    PROJECT_NAME: str = "ONLSuggest"
    VERSION: str = "1.0.0"

    # Performance
    QUERY_MIN_LENGTH: int = 2
    MAX_SUGGESTIONS: int = 5

    # Suggestion Engine (template requires database, koop uses external API)
    # KOOP API not accessible from Vercel, use template
    SUGGESTION_ENGINE: str = os.getenv("SUGGESTION_ENGINE", "template")


settings = Settings()
