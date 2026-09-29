import os
import shutil
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


BUNDLED_DB = Path(__file__).resolve().parents[1] / "medsite.db"


def default_sqlite_path() -> Path:
    """SQLite needs a writable directory; a serverless bundle is mounted read-only."""
    if not os.getenv("VERCEL") and os.access(BUNDLED_DB.parent, os.W_OK):
        return BUNDLED_DB
    runtime_db = Path(os.getenv("TMPDIR", "/tmp")) / "medsite.db"
    if not runtime_db.exists() and BUNDLED_DB.exists():
        shutil.copyfile(BUNDLED_DB, runtime_db)
    return runtime_db


DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{default_sqlite_path()}"


class Base(DeclarativeBase):
    pass


def configure_sqlite(engine):
    if engine.url.get_backend_name() != "sqlite":
        return engine

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = configure_sqlite(create_engine(DATABASE_URL, connect_args=connect_args))


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
