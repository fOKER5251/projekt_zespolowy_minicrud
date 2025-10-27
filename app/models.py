# MODEL DANYCH — STUDENT
# Ten plik definiuje strukturę danych (tabelę w bazie).
# Dzięki SQLAlchemy tworzymy model obiektowy (ORM),
# który automatycznie zamienia dane Python  SQLite.

from sqlalchemy import Column, Integer, String
from .database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)  # unikalne ID (klucz główny)
    first_name = Column(String(80), nullable=False)  # imię studenta (nie może być puste)
    last_name = Column(String(80), nullable=False)  # nazwisko studenta
    group_code = Column(String(40), nullable=False)  # symbol grupy studenckiej

# TODO: można dodać walidację danych (np. długość imienia lub format group_code)