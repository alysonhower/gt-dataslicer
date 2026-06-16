"""DuckDB-native CSV export."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
    options.output_path.parent.mkdir(parents=True, exist_ok=True)
    sql = (
        f"COPY ({query}) TO {quote_literal(str(options.output_path))} "
        f"(HEADER, DELIMITER {quote_literal(options.delimiter)})"
    )
    row = connection.execute(sql, params).fetchone()
    if row is None or row[0] is None:
        return 0
    return int(row[0])
