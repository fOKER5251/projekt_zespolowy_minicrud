from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class Settings:
    # шлях до бази даних SQLite
    DB_PATH: str = str(Path(__file__).resolve().parent / "data" / "app.db")

    # секретний ключ Flask (для сесій)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-please")
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    SESSION_COOKIE_SECURE: bool = os.getenv("SESSION_COOKIE_SECURE", "0") == "1"

settings = Settings()
