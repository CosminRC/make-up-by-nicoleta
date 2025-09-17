
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from datetime import date, time
from .db import engine, init_db
from .models import Appointment

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
def bookings_page(request: Request, q_day: str | None = None):
    with Session(engine) as session:
        stmt = select(Appointment)
        if q_day:
            stmt = stmt.where(Appointment.day == date.fromisoformat(q_day))
        stmt = stmt.order_by(Appointment.day, Appointment.hour)
        items = session.exec(stmt).all()
    return templates.TemplateResponse("bookings.html", {"request": request, "items": items, "q_day": q_day})

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
    appt = Appointment(
        client_name=client_name,
        phone=phone,
        service=service,
        day=date.fromisoformat(day),
        hour=time.fromisoformat(hour),
        notes=notes or None
    )
    with Session(engine) as session:
        session.add(appt)
        session.commit()
    return RedirectResponse(url="/bookings", status_code=303)

app.get("/admin")
def admin_page(request: Request, token: str | None = None, q_day: str | None = None):
    is_admin = (token == ADMIN_TOKEN)
    items = []
    if is_admin:
        from sqlmodel import Session, select
        from datetime import date
        with Session(engine) as session:
            stmt = select(Appointment)
            if q_day:
                stmt = stmt.where(Appointment.day == date.fromisoformat(q_day))
            stmt = stmt.order_by(Appointment.day, Appointment.hour)
            items = session.exec(stmt).all()
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "is_admin": is_admin, "items": items, "q_day": q_day, "token": token or ""}
    )

@app.post("/admin/login")
def admin_login(token: str = Form(...)):
    if token != ADMIN_TOKEN:
        return RedirectResponse(url="/admin", status_code=303)
    return RedirectResponse(url=f"/admin?token={token}", status_code=303)