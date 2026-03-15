from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass

import os

from app.db import session_scope
from app.models import CVAnalysis


@dataclass(frozen=True)
class Job:
    analysis_id: str
    resume_id: str
    job_description: str | None


_q: queue.Queue[Job] = queue.Queue()
_workers: list[threading.Thread] = []
_stop = threading.Event()


def start_workers(worker_count: int) -> None:
    if _workers:
        return
    _stop.clear()
    for i in range(max(1, worker_count)):
        t = threading.Thread(target=_worker_loop, name=f"cv-worker-{i}", daemon=True)
        _workers.append(t)
        t.start()


def stop_workers() -> None:
    _stop.set()


def enqueue(job: Job) -> None:
    if (os.getenv("INLINE_JOBS", "false") or "false").lower() == "true":
        _set_analysis_status(job.analysis_id, "processing")
        try:
            from app.tasks.pipeline import process_job

            process_job(job)
            _set_analysis_status(job.analysis_id, "completed")
        except Exception as e:
            _set_analysis_status(job.analysis_id, "failed", warnings={"error": str(e)})
        return

    _q.put(job)


def _worker_loop() -> None:
    while not _stop.is_set():
        try:
            job = _q.get(timeout=0.5)
        except queue.Empty:
            continue

        _set_analysis_status(job.analysis_id, "processing")
        try:
            from app.tasks.pipeline import process_job

            process_job(job)
            _set_analysis_status(job.analysis_id, "completed")
        except Exception as e:
            _set_analysis_status(job.analysis_id, "failed", warnings={"error": str(e)})
        finally:
            _q.task_done()
            time.sleep(0.01)


def _set_analysis_status(analysis_id: str, status: str, warnings: dict | None = None) -> None:
    import uuid
    import datetime

    with session_scope() as db:
        a = db.get(CVAnalysis, uuid.UUID(analysis_id))
        if not a:
            return
        a.status = status
        now = datetime.datetime.now(datetime.timezone.utc)
        if hasattr(a, "started_at") and status == "processing" and getattr(a, "started_at", None) is None:
            setattr(a, "started_at", now)
        if hasattr(a, "finished_at") and status in ("completed", "failed"):
            setattr(a, "finished_at", now)
        if warnings is not None:
            a.warnings = warnings
        db.add(a)
