
from datetime import datetime, date, time
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint

class Appointment(SQLModel, table=True):
    __table_args__ = (UniqueConstraint('day', 'hour', name='uq_day_hour'),)

    id: Optional[int] = Field(default=None, primary_key=True)
    client_name: str
    phone: str
    service: str
    day: date
    hour: time
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
