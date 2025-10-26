#  KONFIGURACJA APLIKACJI
# Ten plik zawiera podstawowe ustawienia projektu,
# np. ścieżkę do bazy danych (SQLite).
from dataclasses import dataclass
from pathlib import Path

#  Używamy dataclass — prosta struktura do przechowywania konfiguracji
@dataclass
@dataclass
class Settings:
     # Ścieżka do bazy danych SQLite
     # Tworzy plik app.db w folderze /data obok kodu projektu
    DB_PATH: str = str(Path(__file__).resolve().parent / "data" / "app.db")

#  Tworzymy obiekt konfiguracyjny, który potem importujemy w main.py
settings = Settings()

# Ten plik definiuje konfigurację aplikacji — w tym ścieżkę do bazy SQLite.
# Flask backend korzysta z tej ścieżki, żeby wiedzieć, gdzie zapisać dane.