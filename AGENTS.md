# Repository Guidelines

## Project Overview
`gt-dataslicer` is a Python 3.12+ CLI and Pywebview desktop app for filtering large CSV files with a safe bilingual expression DSL and exporting matches to CSV or XLSX. It uses DuckDB for CSV scanning/filter execution, Lark for parsing, Typer/Rich for the localized CLI, Pywebview for the non-technical-first UI, and XlsxWriter for constant-memory Excel output. User-facing text defaults to pt-BR and can switch to en-US with the global `--idioma`/`--lang` option in the CLI or the UI language selector.

## Architecture & Data Flow
- CLI entry point: `gt-dataslicer` -> `gt_dataslicer.cli:main`; tests may import the module-level `app` or call `create_app("en-US")`.
- Desktop UI entry point: `dataslicer` -> `gt_dataslicer.ui.app:main`; `gt-dataslicer abrir` launches the same UI, and hidden alias `gt-dataslicer ui` remains available.
- CLI commands are Portuguese-primary: `filtrar`, `inspecionar`, and `validar-filtro`. English aliases `filter`, `inspect`, and `validate-filter` remain supported but are hidden from the default command list.
- CLI options are Portuguese-primary with English aliases kept for compatibility, for example `--saida/--output`, `--filtro/--where`, `--selecionar/--select`, `--relatorio/--report`, and `--rejeitados/--rejects`.
- Flow: Typer command -> `config.py` merges config presets and CLI flags into `FilterRunOptions` -> `DuckDBEngine.run_filter()` inspects CSV schema, registers lookup CSVs, parses/compiles filters, builds the SELECT query, and delegates export.
- Filter DSL: `filters/grammar.lark` -> `filters/parser.py` -> frozen AST dataclasses in `filters/ast.py` -> parameterized DuckDB SQL from `filters/compiler.py`. The grammar accepts English operators plus pt-BR aliases such as `E`, `OU`, `NAO`/`NÃO`, `EM`, `ENTRE`, `contém`, and `começa com`.
- CSV export uses DuckDB `COPY TO` in `export/csv.py`; XLSX export streams `fetchmany()` batches through XlsxWriter in `export/excel.py`.
- Desktop UI flow: static assets in `ui/web/` call `ui.api.DataSlicerApi` through Pywebview's JS bridge; the API converts visual filters into the existing DSL and builds the same `FilterRunOptions` used by the CLI.
- Reports use `report.RunReport` and can be written as JSON by the CLI `--report` path.
- Human-facing CLI text is centralized in `i18n.py`; do not translate stable config keys, report JSON keys, Python identifiers, or exception class names.

## Key Directories
- `src/gt_dataslicer/`: package source and CLI.
- `src/gt_dataslicer/filters/`: DSL grammar, parser, typed AST, type helpers, SQL compiler.
- `src/gt_dataslicer/engine/`: DuckDB-backed execution pipeline.
- `src/gt_dataslicer/export/`: CSV and XLSX writers.
- `src/gt_dataslicer/ui/`: Pywebview launcher, JS bridge API, background jobs, visual filter builder, and package-local HTML/CSS/JS.
- `packaging/pyinstaller/`: Windows-first PyInstaller freezing entry point and canonical spec file.
- `scripts/`: local build helpers, currently `build-dataslicer.ps1` for `dist\DataSlicer.exe`.
- `tests/unit/`: focused module tests for config, parser, compiler, engine, Excel export.
- `tests/integration/`: Typer CLI end-to-end tests.

## Development Commands
```bash
python -m pip install -e .[dev]
pytest
pytest tests/unit/test_parser.py
pytest tests/integration/test_cli.py
hatch build
python -m pip install -e .[dev,freeze]
.\scripts\build-dataslicer.ps1
```
CLI examples:
```bash
gt-dataslicer inspect input.csv
gt-dataslicer validate-filter input.csv --where 'STATUS EM ("ATIVO", "SUSPENSO")'
gt-dataslicer filter input.csv -o output.csv --where 'CD_EMPRESA = 1 E ST_CONTRATO != "P"'
gt-dataslicer filter input.csv -o output --format xlsx --where 'STATUS = "ATIVO"'
gt-dataslicer --lang en-US validate-filter input.csv --where 'STATUS IN ("ACTIVE", "SUSPENDED")'
gt-dataslicer filtrar input.csv --saida output.csv --filtro 'STATUS EM ("ATIVO", "SUSPENSO")'
gt-dataslicer --idioma en-US validar-filtro input.csv --filtro 'STATUS IN ("ACTIVE", "SUSPENDED")'
dataslicer
gt-dataslicer abrir
```

## Code Conventions & Common Patterns
- Python uses `from __future__ import annotations`, typed function signatures, and dataclasses with `slots=True`; AST nodes are frozen dataclasses.
- Raise typed exceptions from `exceptions.py` instead of raw runtime errors. CLI maps `DataSlicerError.exit_code` to Typer exits; usage/config/filter validation errors generally exit 2.
- Keep SQL generation parameterized. Use `quote_identifier()` and `quote_literal()` when SQL identifiers or literals must be interpolated.
- Preserve the pipeline boundary: parse/validate in filters, option merging in `config.py`, execution/query assembly in `DuckDBEngine`, file writing in `export/`.
- UI code must preserve the same pipeline boundary. Do not reimplement filtering, query assembly, CSV export, or XLSX export in JavaScript or UI-specific Python.
- The visible desktop product name is `DataSlicer` with descriptor `Powered by Grant Thornton Brasil`. Do not expose the `GT` acronym, the Mobius symbol, or invented Grant Thornton logo assets in the UI.
- Freezing is Windows-first and uses PyInstaller one-file mode through `packaging/pyinstaller/dataslicer.spec`; use the spec file instead of ad hoc PyInstaller commands.
- No async patterns or DI container are used. `DuckDBEngine` owns an in-memory DuckDB connection; instantiate directly unless a test needs monkeypatching.
- Tests prefer real temp files via `tmp_path`, `pytest.raises`, and `typer.testing.CliRunner`; there is no shared `conftest.py`.

## Important Files
- `pyproject.toml`: hatchling build, dependencies, `gt-dataslicer` script, pytest config (`testpaths = ["tests"]`, `addopts = "-q"`).
- `README.md`: user-facing examples and output behavior. Keep it simple, non-technical, and copy/paste oriented; avoid architecture details unless they directly help users.
- `src/gt_dataslicer/cli.py`: localized app factory, `main()`, and commands `inspect`, `validate-filter`, and `filter`.
- `src/gt_dataslicer/ui/app.py`: Pywebview window creation and desktop entry point.
- `src/gt_dataslicer/ui/api.py`: JSON-safe bridge used by the static UI.
- `src/gt_dataslicer/ui/web/`: desktop UI assets; keep copy simple, practical, and non-technical.
- `packaging/pyinstaller/dataslicer.spec`: canonical build definition for `dist\DataSlicer.exe`; it must include `ui/web` assets and avoid test files/brand PDFs.
- `scripts/build-dataslicer.ps1`: PowerShell wrapper for the PyInstaller build.
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
- Runtime dependencies: DuckDB, Lark, PyYAML, Pywebview, Rich, Typer, XlsxWriter.
- Dev dependencies: pytest, pytest-cov, openpyxl.
- Freeze dependencies: PyInstaller via `python -m pip install -e .[freeze]`.
- No formatter/linter/type-checker configuration is present; do not invent a new style tool unless explicitly requested.
- No `docs/`, Makefile, tox/nox, pre-commit, or CI config exists in this repository.

## Testing & QA
- Primary test command: `pytest`.
- Unit tests cover config precedence, bilingual DSL parsing, SQL compilation, engine row counts, and XLSX safety/summary behavior.
- Integration tests use `CliRunner` for real CLI flows: filtering, validation, config presets, lookups, dedupe/sort, date casting, strict values, rejects, output formats, and localized CLI output.
- For DSL changes, update parser and compiler tests together; grammar-only changes are incomplete without SQL validation coverage.
- For CLI/config/i18n changes, add or update integration coverage in `tests/integration/test_cli.py` because option aliases, command aliases, language defaults, help text, and exit codes are user-facing.
- For UI changes, test the Python bridge, visual filter conversion, job manager, and CLI launch routing. Do not require a live Pywebview window in automated tests; monkeypatch `webview.create_window` and `webview.start` when launch behavior needs coverage.
- For freezing changes, test the launcher/spec/script as files and imports. Do not require a PyInstaller build in normal tests unless an explicit opt-in environment variable is added.
