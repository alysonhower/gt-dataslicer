"""Background job management for the desktop UI."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from threading import Lock, Thread
from typing import Callable
from uuid import uuid4

from ..report import QueueRunReport, RunReport


LOGGER = logging.getLogger(__name__)

ProgressCallback = Callable[[str], None]
CancelCallback = Callable[[], None]
CancelRegistration = Callable[[CancelCallback], Callable[[], None]]
JobRunner = Callable[[ProgressCallback, CancelRegistration], RunReport | QueueRunReport]


class JobAlreadyRunningError(RuntimeError):
    """Raised when the UI tries to start a second export job."""


class JobCancelledError(RuntimeError):
    """Raised inside a worker when the user requested cancellation."""


@dataclass(slots=True)
class JobStatus:
    job_id: str
    phase: str = "queued"
    running: bool = True
    cancel_requested: bool = False
    report: RunReport | QueueRunReport | None = None
    error: dict[str, str] | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: datetime | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "job_id": self.job_id,
            "phase": self.phase,
            "running": self.running,
            "cancel_requested": self.cancel_requested,
            "report": self.report.to_dict() if self.report is not None else None,
            "error": self.error,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at is not None else None,
        }


class JobManager:
    def __init__(self, *, max_completed_jobs: int = 20) -> None:
        self._lock = Lock()
        self._jobs: dict[str, JobStatus] = {}
        self._cancel_callbacks: dict[str, list[CancelCallback]] = {}
        self._active_job_id: str | None = None
        self._max_completed_jobs = max(1, max_completed_jobs)

    def start(self, runner: JobRunner, *, on_error: Callable[[Exception], dict[str, str]]) -> JobStatus:
        with self._lock:
            if self._active_job_id is not None and self._jobs[self._active_job_id].running:
                raise JobAlreadyRunningError
            job = JobStatus(job_id=uuid4().hex)
            self._jobs[job.job_id] = job
            self._active_job_id = job.job_id

        thread = Thread(
            target=self._run,
            args=(job.job_id, runner, on_error),
            daemon=False,
            name=f"DataSlicerJob-{job.job_id[:8]}",
        )
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
                cancel_requested=job.cancel_requested,
                report=deepcopy(job.report),
                error=deepcopy(job.error),
                started_at=job.started_at,
                ended_at=job.ended_at,
            )

    def has_running_job(self) -> bool:
        with self._lock:
            return self._active_job_id is not None and self._jobs[self._active_job_id].running

    def cancel(self, job_id: str) -> JobStatus:
        callbacks: list[CancelCallback] = []
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                raise KeyError(job_id)
            if job.running:
                job.cancel_requested = True
                job.phase = "canceling"
                callbacks = list(self._cancel_callbacks.get(job_id, []))
        for callback in callbacks:
            try:
                callback()
            except Exception:  # noqa: BLE001 - cancellation should continue best-effort.
                LOGGER.exception("DataSlicer cancellation callback failed")
        return self.get(job_id)

    def _run(self, job_id: str, runner: JobRunner, on_error: Callable[[Exception], dict[str, str]]) -> None:
        def progress(phase: str) -> None:
            if self._is_cancel_requested(job_id):
                raise JobCancelledError("Job was cancelled.")
            self._update(job_id, phase=phase)
            if self._is_cancel_requested(job_id):
                raise JobCancelledError("Job was cancelled.")

        def register_cancel_callback(callback: CancelCallback) -> Callable[[], None]:
            return self._register_cancel_callback(job_id, callback)

        try:
            progress("queued")
            report = runner(progress, register_cancel_callback)
        except JobCancelledError:
            self._update(job_id, phase="cancelled", running=False, cancel_requested=False, ended=True)
            return
        except Exception as exc:  # noqa: BLE001 - converted to a UI-safe error payload.
            if self._is_cancel_requested(job_id):
                self._update(job_id, phase="cancelled", running=False, cancel_requested=False, ended=True)
                return
            LOGGER.exception("DataSlicer UI job failed")
            self._update(job_id, phase="error", running=False, cancel_requested=False, error=on_error(exc), ended=True)
            return

        self._update(job_id, phase="done", running=False, cancel_requested=False, report=report, ended=True)

    def _is_cancel_requested(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            return bool(job and job.cancel_requested)

    def _register_cancel_callback(self, job_id: str, callback: CancelCallback) -> Callable[[], None]:
        call_now = False
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None or not job.running:
                return lambda: None
            self._cancel_callbacks.setdefault(job_id, []).append(callback)
            call_now = job.cancel_requested

        if call_now:
            try:
                callback()
            except Exception:  # noqa: BLE001 - cancellation should continue best-effort.
                LOGGER.exception("DataSlicer cancellation callback failed")

        def unregister() -> None:
            with self._lock:
                callbacks = self._cancel_callbacks.get(job_id)
                if callbacks is None:
                    return
                try:
                    callbacks.remove(callback)
                except ValueError:
                    return

        return unregister

    def _update(
        self,
        job_id: str,
        *,
        phase: str | None = None,
        running: bool | None = None,
        report: RunReport | QueueRunReport | None = None,
        error: dict[str, str] | None = None,
        cancel_requested: bool | None = None,
        ended: bool = False,
    ) -> None:
        with self._lock:
            job = self._jobs[job_id]
            if phase is not None:
                job.phase = phase
            if running is not None:
                job.running = running
            if cancel_requested is not None:
                job.cancel_requested = cancel_requested
            if report is not None:
                job.report = report
            if error is not None:
                job.error = error
            if ended:
                job.ended_at = datetime.now(timezone.utc)
                self._cancel_callbacks.pop(job_id, None)
                if self._active_job_id == job_id:
                    self._active_job_id = None
                self._prune_completed_locked()

    def _prune_completed_locked(self) -> None:
        completed = [
            job
            for job in self._jobs.values()
            if not job.running and job.job_id != self._active_job_id
        ]
        completed.sort(key=lambda job: job.ended_at or job.started_at)
        excess = len(completed) - self._max_completed_jobs
        for job in completed[: max(0, excess)]:
            self._jobs.pop(job.job_id, None)
