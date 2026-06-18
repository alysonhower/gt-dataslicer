"""Helpers for committing generated artifacts safely."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from uuid import uuid4


def sibling_temp_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.tmp-{uuid4().hex}")


def commit_with_temporary_path(path: Path, writer: Callable[[Path], None]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = sibling_temp_path(path)
    try:
        writer(temp_path)
        temp_path.replace(path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def write_text_atomic(path: Path, text: str, *, encoding: str = "utf-8") -> None:
    commit_with_temporary_path(path, lambda temp_path: temp_path.write_text(text, encoding=encoding))
