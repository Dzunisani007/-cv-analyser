import os
import sys
from pathlib import Path
import pytest

def pytest_configure():
    service_dir = Path(__file__).resolve().parents[1]
    if str(service_dir) not in sys.path:
        sys.path.insert(0, str(service_dir))

    # Use file-backed sqlite (in-memory + threads can be flaky).
    db_path = service_dir / ".pytest-db.sqlite"
    os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{db_path.as_posix()}"

    # Deterministic and lightweight tests.
    os.environ.setdefault("SKIP_MODEL_LOAD", "true")
    os.environ.setdefault("INLINE_JOBS", "true")

    # Option B: allow anonymous uploads when AUTH_SECRET is unset.
    os.environ.pop("AUTH_SECRET", None)
    os.environ["PUBLIC_UPLOADS"] = "true"

@pytest.fixture(autouse=True)
def _setup_db_and_storage(tmp_path):
    os.environ["LOCAL_STORAGE_PATH"] = str(tmp_path / "storage")

    from app.db import Base, init_session_factory
    from app.db import get_engine
    import app.models  # noqa: F401

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    init_session_factory()
    yield
