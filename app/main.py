# MINI-CRUD — APLIKACJA STUDENCKA
# Flask + SQLAlchemy + SQLite
# CRUD = Create / Read / Update / Delete

from flask import Flask, jsonify, request, send_from_directory, session
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from .config import settings
from . import database as db
from .database import Base
from .models import Student, User



def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"ok": False, "error": "auth_required"}), 401
        return fn(*args, **kwargs)
    return wrapper


# Inicjalny test działania aplikacji
# static_folder → folder, w którym znajduje się frontend (index.html, JS)
app = Flask(__name__, static_folder=str(Path(__file__).resolve().parent.parent / "static"))
@app.get("/__rules")
def __rules():
    # повертаємо список усіх зареєстрованих маршрутів
    return (
        "\n".join(sorted(str(r) for r in app.url_map.iter_rules())),
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )

app.config["SECRET_KEY"] = settings.SECRET_KEY
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = settings.SESSION_COOKIE_SECURE

# Tworzymy ścieżkę do bazy danych, jeśli jeszcze nie istnieje
Path(settings.DB_PATH).parent.mkdir(parents=True, exist_ok=True)

# Inicjalizacja bazy SQLite + tworzenie tabel na podstawie modeli
db.init_engine(settings.DB_PATH)
db.Base.metadata.create_all(bind=db.engine)
# AUTH: rejestracja / logowanie / wylogowanie

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User

@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})


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

@app.post("/api/register", endpoint="auth_register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify({"ok": False, "error": "email_and_password_required"}), 400

    pwd_hash = generate_password_hash(password)
    with db.SessionLocal() as s:
        user = User(email=email, password_hash=pwd_hash)
        s.add(user)
        try:
            s.commit()
        except IntegrityError:
            s.rollback()
            return jsonify({"ok": False, "error": "email_taken"}), 409
    return jsonify({"ok": True})


@app.post("/api/login", endpoint="auth_login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify({"ok": False, "error": "email_and_password_required"}), 400

    with db.SessionLocal() as s:
        user = s.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"ok": False, "error": "invalid_credentials"}), 401

    session["user_id"] = user.id
    session["user_email"] = email
    return jsonify({"ok": True})


@app.post("/api/logout", endpoint="auth_logout")
def logout():
    session.clear()
    return jsonify({"ok": True})

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
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

