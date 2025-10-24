# Mini‑CRUD „Students” — Flask + SQLite (PL)

Instrukcja w pliku.
#  Mini-CRUD „Studenci” — Flask + SQLite

Aplikacja zaliczeniowa z przedmiotu **Projekt zespołowy**  
Wersja przygotowana na ocenę **3.0–3.5**

Autor: [Vladyslav Stavskyi]  
Grupa: [grupa 1]

---

 Opis projektu

Projekt przedstawia prostą aplikację webową typu CRUD (Create, Read, Update, Delete)**  
umożliwiającą zarządzanie listą studentów w bazie danych SQLite.  

Aplikacja składa się z:
- backendu napisanego w **Python (Flask)**,
- prostego interfejsu frontendowego w **HTML / JavaScript**,
- REST API obsługującego operacje na danych.

Funkcjonalności:
-  dodawanie nowych studentów  
-  edycja istniejących danych  
-  usuwanie studentów  
-  wyświetlanie listy studentów  
-  endpoint `/api/students/count` zwracający liczbę rekordów  
-  sprawdzanie stanu aplikacji pod `/healthz`  
-  dane przechowywane lokalnie w pliku `app/data/app.db`
---
##  Technologie

- Python 3.10+  
- Flask  
- SQLAlchemy  
- SQLite  
- HTML, CSS, JavaScript  

---

##  Instrukcja uruchomienia lokalnie (Windows)

1 **Otwórz projekt w VS Code**  
Folder: `minicrud_ready_flask`

2 **Utwórz środowisko wirtualne**  
```bash
python -m venv .venv

3 Aktywuj środowisko
.\.venv\Scripts\activate

4️ Zainstaluj zależności
pip install -r requirements.txt

5️ Uruchom aplikację
python -m app.main

6️ Otwórz w przeglądarce:

http://127.0.0.1:5000
 → interfejs użytkownika

http://127.0.0.1:5000/api/students
 → dane JSON

http://127.0.0.1:5000/healthz
 → test działania (ok)
