from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is not None:
        return _engine

    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is not set")

    url = settings.database_url
    if url.startswith("sqlite") and ":memory:" in url:
        _engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            future=True,
        )
        return _engine

    _engine = create_engine(url, pool_pre_ping=True, future=True)
    return _engine


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=None, future=True)


def init_session_factory() -> None:
    engine = get_engine()
    SessionLocal.configure(bind=engine)


@contextmanager
def session_scope() -> Session:
    if SessionLocal.kw.get("bind") is None:
        init_session_factory()
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_db() -> dict:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
