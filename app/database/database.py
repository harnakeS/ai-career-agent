from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base



PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIRECTORY = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIRECTORY / "jobs.db"

DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def create_database() -> None:
    """Create all database tables if they don't already exist."""
    Base.metadata.create_all(bind=engine)