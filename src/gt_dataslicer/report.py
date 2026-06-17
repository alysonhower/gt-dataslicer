"""Run report models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class OutputArtifact:
    kind: str
    path: str
    rows: int


@dataclass(slots=True)
class RunReport:
    input_path: str
    artifacts: list[OutputArtifact] = field(default_factory=list)
    output_paths: list[str] = field(default_factory=list)
    input_rows: int | None = None
    output_rows: int = 0
    rejected_rows: int | None = None
    applied_filters: list[str] = field(default_factory=list)
    selected_columns: list[str] = field(default_factory=list)
    renamed_columns: dict[str, str] = field(default_factory=dict)
    schema: dict[str, str] = field(default_factory=dict)
    engine_options: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    dry_run: bool = False
    started_at: datetime = field(default_factory=utc_now)
    ended_at: datetime | None = None

    @property
    def duration_seconds(self) -> float | None:
        if self.ended_at is None:
            return None
        return (self.ended_at - self.started_at).total_seconds()

    def finish(self) -> None:
        self.ended_at = utc_now()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["started_at"] = self.started_at.isoformat()
        data["ended_at"] = self.ended_at.isoformat() if self.ended_at else None
        data["duration_seconds"] = self.duration_seconds
        return data

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


@dataclass(slots=True)
class QueueRunReport:
    input_paths: list[str]
    output_paths: list[str] = field(default_factory=list)
    output_rows: int = 0
    processed_inputs: int = 0
    failed_inputs: int = 0
    runs: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=utc_now)
    ended_at: datetime | None = None

    @property
    def duration_seconds(self) -> float | None:
        if self.ended_at is None:
            return None
        return (self.ended_at - self.started_at).total_seconds()

    def finish(self) -> None:
        self.ended_at = utc_now()

    def add_run(self, report: RunReport) -> None:
        data = report.to_dict()
        self.runs.append(data)
        self.output_paths.extend(report.output_paths)
        self.output_rows += report.output_rows
        self.processed_inputs += 1
        self.warnings.extend(report.warnings)

    def add_error(self, input_path: str, exc: Exception) -> None:
        self.failed_inputs += 1
        self.errors.append({"input_path": input_path, "type": exc.__class__.__name__, "message": str(exc)})

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_paths": self.input_paths,
            "output_paths": self.output_paths,
            "output_rows": self.output_rows,
            "processed_inputs": self.processed_inputs,
            "failed_inputs": self.failed_inputs,
            "runs": self.runs,
            "errors": self.errors,
            "warnings": self.warnings,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": self.duration_seconds,
        }

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
