
import os
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from datetime import date, time
from .db import engine, init_db
from .models import Appointment

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "secret123")
OPEN_HOUR = 9   # 09:00
CLOSE_HOUR = 20 # 20:00 (ultima oră de început acceptată 19:59)

def is_within_hours(t: time) -> bool:
    return (t.hour >= OPEN_HOUR) and (t.hour < CLOSE_HOUR)

app = FastAPI(title="Makeup by Nicoleta – Programări")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/bookings")
def bookings_page(request: Request, q_day: str | None = None, msg: str | None = None, ok: str | None = None, token: str | None = None):
    with Session(engine) as session:
        stmt = select(Appointment)
        if q_day:
            stmt = stmt.where(Appointment.day == date.fromisoformat(q_day))
        stmt = stmt.order_by(Appointment.day, Appointment.hour)
        items = session.exec(stmt).all()
    is_admin = token == ADMIN_TOKEN
    return templates.TemplateResponse(
        "bookings.html",
        {"request": request, "items": items, "q_day": q_day, "msg": msg, "ok": ok, "is_admin": is_admin, "token": token or ""}
    )

@app.post("/book")
def create_booking(
    request: Request,
    client_name: str = Form(...),
    phone: str = Form(...),
    service: str = Form(...),
    day: str = Form(...),   # YYYY-MM-DD
    hour: str = Form(...),  # HH:MM
    notes: str = Form("")
):
    d = date.fromisoformat(day)
    h = time.fromisoformat(hour)

    # Business-hours validation
    if not is_within_hours(h):
        return RedirectResponse(url=f"/bookings?msg=Programările sunt permise între {OPEN_HOUR}:00 și {CLOSE_HOUR}:00", status_code=303)

    with Session(engine) as session:
        # Check overlap (unique slot per day+hour)
        exists = session.exec(
            select(Appointment).where(Appointment.day == d, Appointment.hour == h)
        ).first()
        if exists:
            return RedirectResponse(url="/bookings?msg=Acest interval este deja ocupat. Alege altă oră.", status_code=303)

        appt = Appointment(
            client_name=client_name,
            phone=phone,
            service=service,
            day=d,
            hour=h,
            notes=notes or None
        )
        session.add(appt)
        session.commit()
    return RedirectResponse(url="/bookings?ok=Programare creată cu succes", status_code=303)

@app.post("/delete/{appt_id}")
def delete_booking(appt_id: int, token: str = Form(...)):
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Token admin invalid")
    with Session(engine) as session:
        appt = session.get(Appointment, appt_id)
        if not appt:
            raise HTTPException(status_code=404, detail="Programare inexistentă")
        session.delete(appt)
        session.commit()
    return RedirectResponse(url=f"/bookings?ok=Programare ștearsă&token={token}", status_code=303)
