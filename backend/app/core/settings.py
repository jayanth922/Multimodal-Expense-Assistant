from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

def _default_sqlite_path() -> str:
    # repo root is three levels up from this file
    return str(Path(__file__).resolve().parents[3] / "db" / "expenses.sqlite")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    GOOGLE_API_KEY: str
    GENAI_MODEL: str = "gemini-2.5-flash"
    SQLITE_PATH: str = _default_sqlite_path()
    USE_VERTEXAI: bool = False
    DATABASE_URL: str | None = None

settings = Settings()
