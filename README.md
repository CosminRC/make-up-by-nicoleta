
# Makeup by Nicoleta – Starter (FastAPI + SQLite + Jinja2)

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open: http://127.0.0.1:8000

## Structure
```
app/
  main.py
  models.py
  db.py
  templates/
    base.html
    index.html
    bookings.html
  static/
    styles.css
```
