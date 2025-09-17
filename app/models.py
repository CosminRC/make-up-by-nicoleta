
from datetime import datetime, date, time
from typing import Optional
from sqlmodel import SQLModel, Field

class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_name: str
    phone: str
    service: str
    day: date
    hour: time
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
