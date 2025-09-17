
mport os
from sqlmodel import SQLModel, create_engine

# Folosește variabila de mediu dacă există (ex: sqlite:////data/makeup.db pe Render),
# altfel cade pe fișierul local din proiect.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./makeup.db")
engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)
