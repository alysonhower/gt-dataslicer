"""Background job management for the desktop UI."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from threading import Lock, Thread
from typing import Callable
from uuid import uuid4

from ..report import RunReport


LOGGER = logging.getLogger(__name__)

ProgressCallback = Callable[[str], None]
JobRunner = Callable[[ProgressCallback], RunReport]


class JobAlreadyRunningError(RuntimeError):
    """Raised when the UI tries to start a second export job."""


@dataclass(slots=True)
class JobStatus:
    job_id: str
    phase: str = "queued"
    running: bool = True
    report: RunReport | None = None
    error: dict[str, str] | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: datetime | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "job_id": self.job_id,
            "phase": self.phase,
            "running": self.running,
            "report": self.report.to_dict() if self.report is not None else None,
            "error": self.error,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at is not None else None,
        }


class JobManager:
    def __init__(self) -> None:
        self._lock = Lock()
        self._jobs: dict[str, JobStatus] = {}
        self._active_job_id: str | None = None

    def start(self, runner: JobRunner, *, on_error: Callable[[Exception], dict[str, str]]) -> JobStatus:
        with self._lock:
            if self._active_job_id is not None and self._jobs[self._active_job_id].running:
                raise JobAlreadyRunningError
            job = JobStatus(job_id=uuid4().hex)
            self._jobs[job.job_id] = job
            self._active_job_id = job.job_id

        thread = Thread(target=self._run, args=(job.job_id, runner, on_error), daemon=True)
        thread.start()
        return self.get(job.job_id)

    def get(self, job_id: str) -> JobStatus:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                raise KeyError(job_id)
            return JobStatus(
                job_id=job.job_id,
                phase=job.phase,
                running=job.running,
                report=job.report,
                error=job.error,
                started_at=job.started_at,
                ended_at=job.ended_at,
            )

    def _run(self, job_id: str, runner: JobRunner, on_error: Callable[[Exception], dict[str, str]]) -> None:
        def progress(phase: str) -> None:
            self._update(job_id, phase=phase)

        try:
            progress("queued")
            report = runner(progress)
        except Exception as exc:  # noqa: BLE001 - converted to a UI-safe error payload.
            LOGGER.exception("DataSlicer UI job failed")
            self._update(job_id, phase="error", running=False, error=on_error(exc), ended=True)
            return

        self._update(job_id, phase="done", running=False, report=report, ended=True)

    def _update(
        self,
        job_id: str,
        *,
        phase: str | None = None,
        running: bool | None = None,
        report: RunReport | None = None,
        error: dict[str, str] | None = None,
        ended: bool = False,
    ) -> None:
        with self._lock:
            job = self._jobs[job_id]
            if phase is not None:
                job.phase = phase
            if running is not None:
                job.running = running
            if report is not None:
                job.report = report
            if error is not None:
                job.error = error
            if ended:
                job.ended_at = datetime.now(timezone.utc)
                if self._active_job_id == job_id:
                    self._active_job_id = None

