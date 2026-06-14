from pathlib import Path

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve the project root directory dynamically
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn

    # GitHub Integration Config
    GITHUB_TOKEN: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""
    GITHUB_API_URL: str = "https://api.github.com"

    # Microsoft Foundry IQ Config
    AZURE_AI_FOUNDRY_CONNECTION_STRING: str = ""
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4o"
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # type: ignore[call-arg]
