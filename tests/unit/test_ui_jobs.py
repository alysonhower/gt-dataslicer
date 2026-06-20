from threading import Event
import time

import pytest

from gt_dataslicer.report import RunReport
from gt_dataslicer.ui.jobs import JobAlreadyRunningError, JobManager


def test_job_manager_records_success() -> None:
    manager = JobManager()

    def runner(progress):
        progress("exporting")
        report = RunReport(input_path="input.csv")
        report.output_rows = 2
        report.output_paths = ["output.csv"]
        report.finish()
        return report

    job = manager.start(runner, on_error=lambda exc: {"type": type(exc).__name__, "message": str(exc), "details": str(exc)})

    for _ in range(50):
        snapshot = manager.get(job.job_id)
        if not snapshot.running:
            break
        time.sleep(0.01)

    snapshot = manager.get(job.job_id)
    assert snapshot.phase == "done"
    assert snapshot.report is not None
    assert snapshot.report.output_rows == 2


def test_job_manager_keeps_phase_and_adds_structured_progress() -> None:
    manager = JobManager()
    progress_recorded = Event()
    release = Event()

    def runner(progress):
        progress("queue:2:4")
        progress_recorded.set()
        release.wait(timeout=2)
        report = RunReport(input_path="input.csv")
        report.finish()
        return report

    job = manager.start(runner, on_error=lambda exc: {"type": type(exc).__name__, "message": str(exc), "details": str(exc)})
    assert progress_recorded.wait(timeout=2)

    data = manager.get(job.job_id).to_dict()
    assert data["phase"] == "queue:2:4"
    progress = data["progress"]
    assert isinstance(progress, dict)
    assert progress["phase"] == "queue"
    assert progress["input_index"] == 2
    assert progress["input_total"] == 4
    assert progress["percent"] == 25
    assert progress["determinate"] is True
    assert progress["started_at"]
    assert progress["updated_at"]
    release.set()


def test_job_manager_bounds_progress_timeline() -> None:
    manager = JobManager()
    progress_recorded = Event()
    release = Event()

    def runner(progress):
        for index in range(12):
            progress({"phase": f"phase-{index}", "label": f"Phase {index}"})
        progress_recorded.set()
        release.wait(timeout=2)
        report = RunReport(input_path="input.csv")
        report.finish()
        return report

    job = manager.start(runner, on_error=lambda exc: {"type": type(exc).__name__, "message": str(exc), "details": str(exc)})
    assert progress_recorded.wait(timeout=2)

    data = manager.get(job.job_id).to_dict()
    progress = data["progress"]
    assert isinstance(progress, dict)
    timeline = progress["timeline"]
    assert isinstance(timeline, list)
    assert len(timeline) == 12
    assert timeline[-1]["phase"] == "phase-11"
    release.set()


def test_job_manager_prevents_concurrent_runs() -> None:
    manager = JobManager()
    release = Event()

    def runner(progress):
        progress("exporting")
        release.wait(timeout=2)
        report = RunReport(input_path="input.csv")
        report.finish()
        return report

    manager.start(runner, on_error=lambda exc: {"type": type(exc).__name__, "message": str(exc), "details": str(exc)})

    with pytest.raises(JobAlreadyRunningError):
        manager.start(runner, on_error=lambda exc: {"type": type(exc).__name__, "message": str(exc), "details": str(exc)})

    release.set()

