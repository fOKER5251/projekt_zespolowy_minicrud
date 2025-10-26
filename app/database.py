#  KONFIGURACJA BAZY DANYCH (SQLAlchemy)
# Ten plik odpowiada za połączenie z bazą SQLite
# oraz utworzenie mechanizmu sesji do komunikacji z bazą.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Base — klasa bazowa dla wszystkich modeli (ORM)
# Dzięki niej SQLAlchemy wie, jak tworzyć tabele w bazie danych.
Base = declarative_base()

# Zmienna globalna dla silnika i sesji
engine = None
SessionLocal = None

# Funkcja inicjalizująca połączenie z bazą danych
def init_engine(db_path: str):
    global engine, SessionLocal
    # Tworzymy silnik połączenia do bazy SQLite
    # check_same_thread=False → pozwala używać tej samej bazy w wielu wątkach (Flask)
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    # Tworzymy fabrykę sesji (SessionLocal), która służy do pracy z bazą
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# "Tutaj konfiguruję SQLAlchemy — tworzę połączenie z bazą SQLite
# i ustawiam klasę SessionLocal, która pozwala wykonywać zapytania
# w mojej aplikacji Flask."