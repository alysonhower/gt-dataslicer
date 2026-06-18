"""DuckDB-native CSV export."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..artifacts import commit_with_temporary_path
from ..filters.compiler import quote_literal


_SPREADSHEET_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r", "\n")


@dataclass(slots=True)
class CsvExportOptions:
    output_path: Path
    delimiter: str = ","
    spreadsheet_safe: bool = False
    batch_size: int = 10_000


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
        if options.spreadsheet_safe:
            copied_rows = _export_query_to_spreadsheet_safe_csv(
                connection,
                query=query,
                params=params,
                output_path=temp_path,
                delimiter=options.delimiter,
                batch_size=options.batch_size,
            )
            return
        sql = (
            f"COPY ({query}) TO {quote_literal(str(temp_path))} "
            f"(HEADER, DELIMITER {quote_literal(options.delimiter)})"
        )
        row = connection.execute(sql, params).fetchone()
        copied_rows = 0 if row is None or row[0] is None else int(row[0])

    commit_with_temporary_path(options.output_path, write_temp)
    return copied_rows


def _export_query_to_spreadsheet_safe_csv(
    connection: Any,
    *,
    query: str,
    params: list[Any],
    output_path: Path,
    delimiter: str,
    batch_size: int,
) -> int:
    cursor = connection.execute(query, params)
    headers = [item[0] for item in cursor.description or []]
    row_count = 0
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=delimiter)
        writer.writerow(headers)
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            for row in rows:
                writer.writerow([_spreadsheet_safe_cell(value) for value in row])
                row_count += 1
    return row_count


def _spreadsheet_safe_cell(value: Any) -> Any:
    if isinstance(value, str) and value.startswith(_SPREADSHEET_FORMULA_PREFIXES):
        return f"'{value}"
    return value
