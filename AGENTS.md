# Repository Guidelines

## Project Overview
`gt-dataslicer` is a Python 3.12+ CLI for filtering large CSV files with a safe bilingual expression DSL and exporting matches to CSV or XLSX. It uses DuckDB for CSV scanning/filter execution, Lark for parsing, Typer/Rich for the localized CLI, and XlsxWriter for constant-memory Excel output. User-facing CLI text defaults to pt-BR and can switch to en-US with the global `--lang` option.

## Architecture & Data Flow
- CLI entry point: `gt-dataslicer` -> `gt_dataslicer.cli:main`; tests may import the module-level `app` or call `create_app("en-US")`.
- Flow: Typer command -> `config.py` merges config presets and CLI flags into `FilterRunOptions` -> `DuckDBEngine.run_filter()` inspects CSV schema, registers lookup CSVs, parses/compiles filters, builds the SELECT query, and delegates export.
- Filter DSL: `filters/grammar.lark` -> `filters/parser.py` -> frozen AST dataclasses in `filters/ast.py` -> parameterized DuckDB SQL from `filters/compiler.py`. The grammar accepts English operators plus pt-BR aliases such as `E`, `OU`, `NAO`/`NÃO`, `EM`, `ENTRE`, `contém`, and `começa com`.
- CSV export uses DuckDB `COPY TO` in `export/csv.py`; XLSX export streams `fetchmany()` batches through XlsxWriter in `export/excel.py`.
- Reports use `report.RunReport` and can be written as JSON by the CLI `--report` path.
- Human-facing CLI text is centralized in `i18n.py`; do not translate stable config keys, report JSON keys, Python identifiers, or exception class names.

## Key Directories
- `src/gt_dataslicer/`: package source and CLI.
- `src/gt_dataslicer/filters/`: DSL grammar, parser, typed AST, type helpers, SQL compiler.
- `src/gt_dataslicer/engine/`: DuckDB-backed execution pipeline.
- `src/gt_dataslicer/export/`: CSV and XLSX writers.
- `tests/unit/`: focused module tests for config, parser, compiler, engine, Excel export.
- `tests/integration/`: Typer CLI end-to-end tests.

## Development Commands
```bash
python -m pip install -e .[dev]
pytest
pytest tests/unit/test_parser.py
pytest tests/integration/test_cli.py
hatch build
```
CLI examples:
```bash
gt-dataslicer inspect input.csv
gt-dataslicer validate-filter input.csv --where 'STATUS EM ("ATIVO", "SUSPENSO")'
gt-dataslicer filter input.csv -o output.csv --where 'CD_EMPRESA = 1 E ST_CONTRATO != "P"'
gt-dataslicer filter input.csv -o output --format xlsx --where 'STATUS = "ATIVO"'
gt-dataslicer --lang en-US validate-filter input.csv --where 'STATUS IN ("ACTIVE", "SUSPENDED")'
```

## Code Conventions & Common Patterns
- Python uses `from __future__ import annotations`, typed function signatures, and dataclasses with `slots=True`; AST nodes are frozen dataclasses.
- Raise typed exceptions from `exceptions.py` instead of raw runtime errors. CLI maps `DataSlicerError.exit_code` to Typer exits; usage/config/filter validation errors generally exit 2.
- Keep SQL generation parameterized. Use `quote_identifier()` and `quote_literal()` when SQL identifiers or literals must be interpolated.
- Preserve the pipeline boundary: parse/validate in filters, option merging in `config.py`, execution/query assembly in `DuckDBEngine`, file writing in `export/`.
- No async patterns or DI container are used. `DuckDBEngine` owns an in-memory DuckDB connection; instantiate directly unless a test needs monkeypatching.
- Tests prefer real temp files via `tmp_path`, `pytest.raises`, and `typer.testing.CliRunner`; there is no shared `conftest.py`.

## Important Files
- `pyproject.toml`: hatchling build, dependencies, `gt-dataslicer` script, pytest config (`testpaths = ["tests"]`, `addopts = "-q"`).
- `README.md`: user-facing CLI examples and output behavior.
- `src/gt_dataslicer/cli.py`: localized app factory, `main()`, and commands `inspect`, `validate-filter`, and `filter`.
- `src/gt_dataslicer/i18n.py`: pt-BR/en-US message templates and user-facing error localization.
- `src/gt_dataslicer/config.py`: config file loading, preset selection, CLI/config merge, output format resolution.
- `src/gt_dataslicer/engine/duckdb_engine.py`: main CSV inspection/filter/export pipeline.
- `src/gt_dataslicer/filters/grammar.lark`: DSL operators and syntax.
- `src/gt_dataslicer/filters/compiler.py`: AST-to-SQL validation and compilation.
- `src/gt_dataslicer/export/excel.py`: XLSX limits, splitting, summary sheet, cell normalization.
- `tests/integration/test_cli.py`: best reference for supported CLI behavior and exit codes.

## Runtime/Tooling Preferences
- Runtime: Python `>=3.12`.
- Build backend: Hatchling (`hatchling.build`); wheel package is `src/gt_dataslicer`.
- Runtime dependencies: DuckDB, Lark, PyYAML, Rich, Typer, XlsxWriter.
- Dev dependencies: pytest, pytest-cov, openpyxl.
- No formatter/linter/type-checker configuration is present; do not invent a new style tool unless explicitly requested.
- No `scripts/`, `docs/`, Makefile, tox/nox, pre-commit, or CI config exists in this repository.

## Testing & QA
- Primary test command: `pytest`.
- Unit tests cover config precedence, bilingual DSL parsing, SQL compilation, engine row counts, and XLSX safety/summary behavior.
- Integration tests use `CliRunner` for real CLI flows: filtering, validation, config presets, lookups, dedupe/sort, date casting, strict values, rejects, output formats, and localized CLI output.
- For DSL changes, update parser and compiler tests together; grammar-only changes are incomplete without SQL validation coverage.
- For CLI/config/i18n changes, add or update integration coverage in `tests/integration/test_cli.py` because option precedence, language defaults, help text, and exit codes are user-facing.
