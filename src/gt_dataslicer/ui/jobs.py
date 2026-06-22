"""Background job management for the desktop UI."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from threading import Lock, Thread
from typing import Callable, Mapping, Final
from uuid import uuid4

from ..i18n import tr
from ..report import QueueRunReport, RunReport


LOGGER = logging.getLogger(__name__)
TIMELINE_LIMIT: Final = 12

ProgressUpdate = str | Mapping[str, object]
ProgressCallback = Callable[[ProgressUpdate], None]
JobRunner = Callable[[ProgressCallback], RunReport | QueueRunReport]


class JobAlreadyRunningError(RuntimeError):
    """Raised when the UI tries to start a second export job."""


@dataclass(slots=True)
class JobStatus:
    job_id: str
    phase: str = "queued"
    running: bool = True
    report: RunReport | QueueRunReport | None = None
    error: dict[str, str] | None = None
    progress: dict[str, object] = field(default_factory=dict)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: datetime | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "job_id": self.job_id,
            "phase": self.phase,
            "running": self.running,
            "report": self.report.to_dict() if self.report is not None else None,
            "error": self.error,
            "progress": _copy_progress(self.progress),
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
                progress=_copy_progress(job.progress),
                started_at=job.started_at,
                ended_at=job.ended_at,
            )

    def _run(self, job_id: str, runner: JobRunner, on_error: Callable[[Exception], dict[str, str]]) -> None:
        def progress(update: ProgressUpdate) -> None:
            self._update(job_id, phase=update)

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
        phase: ProgressUpdate | None = None,
        running: bool | None = None,
        report: RunReport | QueueRunReport | None = None,
        error: dict[str, str] | None = None,
        ended: bool = False,
    ) -> None:
        with self._lock:
            job = self._jobs[job_id]
            if phase is not None:
                job.phase = _phase_text(phase)
                job.progress = _progress_payload(phase, job.progress, job.started_at)
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


def _copy_progress(progress: dict[str, object]) -> dict[str, object]:
    copied = dict(progress)
    copied["timeline"] = [dict(item) for item in _timeline(progress)]
    return copied


def _phase_text(update: ProgressUpdate) -> str:
    if isinstance(update, str):
        return update
    phase = update.get("phase")
    return str(phase or "running")


def _progress_payload(update: ProgressUpdate, previous: dict[str, object], started_at: datetime) -> dict[str, object]:
    now = datetime.now(timezone.utc).isoformat()
    values = _progress_values(update)
    label_key = values["label_key"] or f"ui.phase.{values['phase']}"
    label = values["label"] or tr(str(label_key))
    entry = {
        "phase": values["phase"],
        "label_key": label_key,
        "label": label,
        "input_index": values["input_index"],
        "input_total": values["input_total"],
        "input_name": values["input_name"],
        "artifact": values["artifact"],
        "percent": values["percent"],
        "determinate": values["determinate"],
        "timestamp": now,
    }
    timeline = [*_timeline(previous), entry][-TIMELINE_LIMIT:]
    return {
        **entry,
        "timeline": timeline,
        "started_at": previous.get("started_at") or started_at.isoformat(),
        "updated_at": now,
    }


def _progress_values(update: ProgressUpdate) -> dict[str, object]:
    if isinstance(update, str):
        return _string_progress_values(update)
    phase = str(update.get("phase") or "running")
    determinate = bool(update.get("determinate", update.get("percent") is not None))
    percent = _percent(update.get("percent")) if determinate else None
    return {
        "phase": phase,
        "label_key": _optional_text(update.get("label_key")),
        "label": _optional_text(update.get("label")),
        "input_index": _positive_int(update.get("input_index")),
        "input_total": _positive_int(update.get("input_total")),
        "input_name": _optional_text(update.get("input_name")),
        "artifact": _optional_text(update.get("artifact")),
        "percent": percent,
        "determinate": determinate,
    }


def _string_progress_values(phase_text: str) -> dict[str, object]:
    parts = phase_text.split(":")
    if len(parts) == 3 and parts[0] == "queue":
        input_index = _positive_int(parts[1])
        input_total = _positive_int(parts[2])
        percent = _queue_percent(input_index, input_total)
        return {
            "phase": "queue",
            "label_key": "ui.phase.queue",
            "label": None,
            "input_index": input_index,
            "input_total": input_total,
            "input_name": None,
            "artifact": None,
            "percent": percent,
            "determinate": percent is not None,
        }
    return {
        "phase": phase_text,
        "label_key": f"ui.phase.{phase_text}",
        "label": None,
        "input_index": None,
        "input_total": None,
        "input_name": None,
        "artifact": None,
        "percent": 100 if phase_text == "done" else None,
        "determinate": phase_text == "done",
    }


def _timeline(progress: dict[str, object]) -> list[dict[str, object]]:
    timeline = progress.get("timeline")
    if not isinstance(timeline, list):
        return []
    return [item for item in timeline if isinstance(item, dict)]


def _positive_int(value: object) -> int | None:
    try:
        number = int(value) if value is not None else 0
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _percent(value: object) -> int | None:
    try:
        number = round(float(value)) if value is not None else 0
    except (TypeError, ValueError):
        return None
    return max(0, min(100, number))


def _queue_percent(input_index: int | None, input_total: int | None) -> int | None:
    if input_index is None or input_total is None:
        return None
    return _percent(((input_index - 1) / input_total) * 100)


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
