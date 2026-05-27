from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    All values are read from the .env file in the project root.
    Call get_settings() anywhere in the app to access these values.
    """

    # External API keys
    groq_api_key: str
    sarvam_api_key: str

    # SQLite database path (relative to project root)
    database_path: str = "./data/interview.db"

    # FastAPI server
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


def get_settings() -> Settings:
    """Creates and returns the application settings from the .env file."""
    return Settings()
