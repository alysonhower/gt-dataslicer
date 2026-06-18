from threading import Event
import time

import pytest

from gt_dataslicer.report import RunReport
from gt_dataslicer.ui import jobs as jobs_module
from gt_dataslicer.ui.jobs import JobAlreadyRunningError, JobManager


def test_job_manager_records_success() -> None:
    manager = JobManager()

    def runner(progress, _register_cancel):
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


def test_job_manager_uses_non_daemon_worker_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = JobManager()
    created_threads: list[FakeThread] = []

    class FakeThread:
        def __init__(self, *, target, args, daemon, name) -> None:
            self.target = target
            self.args = args
            self.daemon = daemon
            self.name = name
            created_threads.append(self)

        def start(self) -> None:
            self.target(*self.args)

    def runner(_progress, _register_cancel):
        report = RunReport(input_path="input.csv")
        report.finish()
        return report

    monkeypatch.setattr(jobs_module, "Thread", FakeThread)

    job = manager.start(runner, on_error=lambda exc: {"type": type(exc).__name__, "message": str(exc), "details": str(exc)})

    assert job.running is False
    assert created_threads[0].daemon is False
    assert created_threads[0].name.startswith("DataSlicerJob-")


def test_job_manager_prevents_concurrent_runs() -> None:
    manager = JobManager()
    release = Event()

    def runner(progress, _register_cancel):
        progress("exporting")
        release.wait(timeout=2)
        report = RunReport(input_path="input.csv")
        report.finish()
        return report

    manager.start(runner, on_error=lambda exc: {"type": type(exc).__name__, "message": str(exc), "details": str(exc)})

    with pytest.raises(JobAlreadyRunningError):
        manager.start(runner, on_error=lambda exc: {"type": type(exc).__name__, "message": str(exc), "details": str(exc)})

    release.set()


def test_job_manager_cancel_reaches_cancelled_terminal_state() -> None:
    manager = JobManager()
    entered = Event()
    release = Event()
    interrupt_called = Event()

    def runner(progress, register_cancel):
        unregister = register_cancel(interrupt_called.set)
        progress("exporting")
        entered.set()
        release.wait(timeout=2)
        try:
            progress("finishing")
            report = RunReport(input_path="input.csv")
            report.finish()
            return report
        finally:
            unregister()

    job = manager.start(runner, on_error=lambda exc: {"type": type(exc).__name__, "message": str(exc), "details": str(exc)})
    assert entered.wait(timeout=2)

    cancelled = manager.cancel(job.job_id)
    assert cancelled.running is True
    assert cancelled.cancel_requested is True
    assert cancelled.phase == "canceling"
    assert interrupt_called.wait(timeout=2)

    release.set()
    for _attempt in range(50):
        snapshot = manager.get(job.job_id)
        if not snapshot.running:
            break
        time.sleep(0.01)

    snapshot = manager.get(job.job_id)
    assert snapshot.running is False
    assert snapshot.cancel_requested is False
    assert snapshot.phase == "cancelled"
    assert snapshot.report is None


def test_job_manager_treats_exception_after_cancel_as_cancelled() -> None:
    manager = JobManager()
    entered = Event()
    release = Event()
    interrupt_called = Event()

    def runner(progress, register_cancel):
        register_cancel(interrupt_called.set)
        progress("exporting")
        entered.set()
        release.wait(timeout=2)
        raise RuntimeError("duckdb query interrupted")

    job = manager.start(runner, on_error=lambda exc: {"type": type(exc).__name__, "message": str(exc), "details": str(exc)})
    assert entered.wait(timeout=2)

    manager.cancel(job.job_id)
    assert interrupt_called.wait(timeout=2)
    release.set()

    for _attempt in range(50):
        snapshot = manager.get(job.job_id)
        if not snapshot.running:
            break
        time.sleep(0.01)

    snapshot = manager.get(job.job_id)
    assert snapshot.running is False
    assert snapshot.cancel_requested is False
    assert snapshot.phase == "cancelled"
    assert snapshot.error is None


def test_job_manager_prunes_old_completed_jobs() -> None:
    manager = JobManager(max_completed_jobs=2)
    job_ids: list[str] = []

    def runner(_progress, _register_cancel):
        report = RunReport(input_path="input.csv")
        report.finish()
        return report

    for _ in range(3):
        job = manager.start(runner, on_error=lambda exc: {"type": type(exc).__name__, "message": str(exc), "details": str(exc)})
        job_ids.append(job.job_id)
        for _attempt in range(50):
            if not manager.get(job.job_id).running:
                break
            time.sleep(0.01)

    with pytest.raises(KeyError):
        manager.get(job_ids[0])
    assert manager.get(job_ids[1]).running is False
    assert manager.get(job_ids[2]).running is False


def test_job_manager_get_returns_report_snapshot() -> None:
    manager = JobManager()

    def runner(_progress, _register_cancel):
        report = RunReport(input_path="input.csv")
        report.output_rows = 1
        report.finish()
        return report

    job = manager.start(runner, on_error=lambda exc: {"type": type(exc).__name__, "message": str(exc), "details": str(exc)})
    for _attempt in range(50):
        snapshot = manager.get(job.job_id)
        if not snapshot.running:
            break
        time.sleep(0.01)

    first = manager.get(job.job_id)
    assert first.report is not None
    first.report.output_rows = 99

    second = manager.get(job.job_id)
    assert second.report is not None
    assert second.report.output_rows == 1

