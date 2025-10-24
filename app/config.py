from dataclasses import dataclass
from pathlib import Path

@dataclass
class Settings:
    DB_PATH: str = str(Path(__file__).resolve().parent / "data" / "app.db")

settings = Settings()
