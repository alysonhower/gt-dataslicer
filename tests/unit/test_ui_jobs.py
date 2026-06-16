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

