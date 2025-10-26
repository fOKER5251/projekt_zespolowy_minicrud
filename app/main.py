# MINI-CRUD — APLIKACJA STUDENCKA
# Flask + SQLAlchemy + SQLite
# CRUD = Create / Read / Update / Delete

from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import select
from .config import settings
from . import database as db
from .models import Student

# Inicjalny test działania aplikacji
# static_folder → folder, w którym znajduje się frontend (index.html, JS)
app = Flask(__name__, static_folder=str(Path(__file__).resolve().parent.parent / "static"))

# Tworzymy ścieżkę do bazy danych, jeśli jeszcze nie istnieje
Path(settings.DB_PATH).parent.mkdir(parents=True, exist_ok=True)

# Inicjalizacja bazy SQLite + tworzenie tabel na podstawie modeli
db.init_engine(settings.DB_PATH)
db.Base.metadata.create_all(bind=db.engine)

#  ENDPOINT: HEALTHCHECK
# Służy do sprawdzenia, czy serwer działa (200 OK)
@app.get("/healthz")
def healthz():
    return "ok", 200

# Funkcja pomocnicza — otwiera nową sesję z bazą danych
def get_db() -> Session:
    return db.SessionLocal()

#  READ — pobierz listę studentów (GET)
@app.get("/api/students/")
def list_students():
    s = get_db()
     # Pobieramy studentów z bazy danych (sortujemy po ID malejąco)
    res = s.execute(select(Student).order_by(Student.id.desc())).scalars().all()
     # Konwertujemy obiekty Student do formatu JSON
    out = [serialize(x) for x in res]
    s.close()
    return jsonify(out)

#  READ — pobierz jednego studenta po ID
@app.get("/api/students/<int:student_id>")
def get_student(student_id: int):
    s = get_db()
    obj = s.get(Student, student_id)
    s.close()
    if not obj:
         # Jeśli nie znaleziono → 404 Not Found
        return jsonify({"detail":"student nie znaleziony"}), 404
    return jsonify(serialize(obj))

#  CREATE — dodaj nowego studenta
@app.post("/api/students/")
def create_student():
    payload = request.get_json(force=True, silent=True) or {}
     # Walidacja danych
    ok, msg = validate(payload)
    if not ok:
        return jsonify({"detail": msg}), 400
    s = get_db()
    # Tworzymy nowy obiekt Student i zapisujemy do bazy
    obj = Student(**payload)
    s.add(obj); s.commit(); s.refresh(obj)
    out = serialize(obj)
    s.close()
    return jsonify(out), 201 # 201 = Created

#  UPDATE — edycja istniejącego studenta
@app.put("/api/students/<int:student_id>")
def update_student(student_id: int):
    payload = request.get_json(force=True, silent=True) or {}
    ok, msg = validate(payload)
    if not ok:
        return jsonify({"detail": msg}), 400
    s = get_db()
    obj = s.get(Student, student_id)
    if not obj:
        s.close()
        return jsonify({"detail":"student nie znaleziony"}), 404
     # Aktualizujemy pola obiektu
    for k,v in payload.items():
        setattr(obj, k, v)
    s.commit(); s.refresh(obj)
    out = serialize(obj)
    s.close()
    return jsonify(out)

#  DELETE — usuń studenta
@app.delete("/api/students/<int:student_id>")
def delete_student(student_id: int):
    s = get_db()
    obj = s.get(Student, student_id)
    if not obj:
        s.close()
        return jsonify({"detail":"student nie znaleziony"}), 404
    s.delete(obj); s.commit(); s.close()
    return ("", 204) # 204 = No Content

#  STRONA GŁÓWNA FRONTENDU (index.html)
# Zwraca plik HTML z folderu /static
@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

#  FUNKCJE POMOCNICZE
# serialize() — konwertuje model na JSON
# validate() — sprawdza, czy wszystkie pola są poprawne
def serialize(st: Student) -> dict:
    return {"id": st.id, "first_name": st.first_name, "last_name": st.last_name, "group_code": st.group_code}

def validate(p: dict) -> tuple[bool,str]:
    for k in ["first_name","last_name","group_code"]:
        if k not in p:
            return False, f"brakuje pola: {k}"
        if isinstance(p[k], str) and not p[k].strip():
            return False, f"pole {k} nie może być puste"
    return True, ""

# LOKALNE URUCHOMIENIE APLIKACJI
# Gdy plik uruchamiany bezpośrednio, startuje serwer Flask
if __name__ == "__main__":
    app.run(debug=True)
