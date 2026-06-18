"""DuckDB-native CSV export."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..artifacts import commit_with_temporary_path
from ..filters.compiler import quote_literal


@dataclass(slots=True)
class CsvExportOptions:
    output_path: Path
    delimiter: str = ","


def export_query_to_csv(
    connection: Any,
    *,
    query: str,
    params: list[Any],
    options: CsvExportOptions,
) -> int:
    copied_rows = 0

    def write_temp(temp_path: Path) -> None:
        nonlocal copied_rows
        sql = (
            f"COPY ({query}) TO {quote_literal(str(temp_path))} "
            f"(HEADER, DELIMITER {quote_literal(options.delimiter)})"
        )
        row = connection.execute(sql, params).fetchone()
        copied_rows = 0 if row is None or row[0] is None else int(row[0])

    commit_with_temporary_path(options.output_path, write_temp)
    return copied_rows
