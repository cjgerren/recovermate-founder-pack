"""SQLite database setup for local Demo Arena."""
import os
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("RECOVERMATE_DB", str(BASE_DIR / "recovermate.db")))
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema() -> None:
    """Create tables and apply tiny additive upgrades for existing demo DBs.

    Models must already be imported so Base.metadata is populated.
    """
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    insp = inspect(engine)
    tables = set(insp.get_table_names())
    if "found_items" in tables:
        cols = {c["name"] for c in insp.get_columns("found_items")}
        if "notes" not in cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE found_items ADD COLUMN notes TEXT"))
    if "matches" in tables:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS uq_matches_pair "
                    "ON matches (lost_report_id, found_item_id)"
                )
            )
