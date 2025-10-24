from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import select
from .config import settings
from . import database as db
from .models import Student

app = Flask(__name__, static_folder=str(Path(__file__).resolve().parent.parent / "static"))
Path(settings.DB_PATH).parent.mkdir(parents=True, exist_ok=True)

# init DB
db.init_engine(settings.DB_PATH)
db.Base.metadata.create_all(bind=db.engine)

@app.get("/healthz")
def healthz():
    return "ok", 200

def get_db() -> Session:
    return db.SessionLocal()

@app.get("/api/students/")
def list_students():
    s = get_db()
    res = s.execute(select(Student).order_by(Student.id.desc())).scalars().all()
    out = [serialize(x) for x in res]
    s.close()
    return jsonify(out)

@app.get("/api/students/<int:student_id>")
def get_student(student_id: int):
    s = get_db()
    obj = s.get(Student, student_id)
    s.close()
    if not obj:
        return jsonify({"detail":"student nie znaleziony"}), 404
    return jsonify(serialize(obj))

@app.post("/api/students/")
def create_student():
    payload = request.get_json(force=True, silent=True) or {}
    ok, msg = validate(payload)
    if not ok:
        return jsonify({"detail": msg}), 400
    s = get_db()
    obj = Student(**payload)
    s.add(obj); s.commit(); s.refresh(obj)
    out = serialize(obj)
    s.close()
    return jsonify(out), 201

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
    for k,v in payload.items():
        setattr(obj, k, v)
    s.commit(); s.refresh(obj)
    out = serialize(obj)
    s.close()
    return jsonify(out)

@app.delete("/api/students/<int:student_id>")
def delete_student(student_id: int):
    s = get_db()
    obj = s.get(Student, student_id)
    if not obj:
        s.close()
        return jsonify({"detail":"student nie znaleziony"}), 404
    s.delete(obj); s.commit(); s.close()
    return ("", 204)

@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# helpers  # TODO: sprawdzić działanie endpointu /api/students

def serialize(st: Student) -> dict:
    return {"id": st.id, "first_name": st.first_name, "last_name": st.last_name, "group_code": st.group_code}

def validate(p: dict) -> tuple[bool,str]:
    for k in ["first_name","last_name","group_code"]:
        if k not in p:
            return False, f"brakuje pola: {k}"
        if isinstance(p[k], str) and not p[k].strip():
            return False, f"pole {k} nie może być puste"
    return True, ""

if __name__ == "__main__":
    app.run(debug=True)
