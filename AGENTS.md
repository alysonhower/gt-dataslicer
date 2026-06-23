# Repository Guidelines

## Project Overview
`gt-dataslicer` is a Python 3.12+ CLI and Pywebview desktop app for filtering large CSV, Parquet, Excel `.xlsx`, and ZIP-delivered data files with a safe bilingual expression DSL and exporting matches to CSV, XLSX, or Parquet. It uses DuckDB for tabular scanning/filter execution and CSV/Parquet export, Lark for parsing, Typer/Rich for the localized CLI, Pywebview for the non-technical-first UI, and XlsxWriter for constant-memory Excel output. User-facing text defaults to pt-BR and can switch to en-US with the global `--idioma`/`--lang` option in the CLI or the UI language selector.

## Architecture & Data Flow
- CLI entry point: `gt-dataslicer` -> `gt_dataslicer.cli:main`; tests may import the module-level `app` or call `create_app("en-US")`.
- Desktop UI entry point: `dataslicer` -> `gt_dataslicer.ui.app:main`; `gt-dataslicer abrir` launches the same UI, and hidden alias `gt-dataslicer ui` remains available.
- CLI commands are Portuguese-primary: `filtrar`, `inspecionar`, and `validar-filtro`. English aliases `filter`, `inspect`, and `validate-filter` remain supported but are hidden from the default command list.
- CLI options are Portuguese-primary with English aliases kept for compatibility, for example `--saida/--output`, `--filtro/--where`, `--selecionar/--select`, `--relatorio/--report`, and `--rejeitados/--rejects`.
- Flow: Typer command -> input resolution expands CSV/Parquet/XLSX/ZIP files into a sequential queue -> `config.py` merges config presets and CLI flags into `FilterRunOptions` -> `DuckDBEngine.run_filter()` inspects the resolved tabular source, registers lookup CSVs, parses/compiles filters, adds post-filter derived columns, builds the SELECT query, and delegates export.
- Filter DSL: `filters/grammar.lark` -> `filters/parser.py` -> frozen AST dataclasses in `filters/ast.py` -> parameterized DuckDB SQL from `filters/compiler.py`. The grammar accepts English operators plus pt-BR aliases such as `E`, `OU`, `NAO`/`NÃO`, `EM`, `ENTRE`, `contém`, and `começa com`.
- CSV and Parquet export use DuckDB `COPY TO` in `export/`; XLSX export streams `fetchmany()` batches through XlsxWriter in `export/excel.py`.
- Desktop UI flow: static assets in `ui/web/` call `ui.api.DataSlicerApi` through Pywebview's JS bridge; the API converts visual filters into the existing DSL and builds the same `FilterRunOptions` used by the CLI.
- CLI, UI, and config must remain 1:1 compatible for user-visible features. Complex features such as derived columns use one shared schema accepted by UI payloads, config files, `--coluna-derivada/--derived-column`, and `--colunas-derivadas-arquivo/--derived-columns-file`.
- The visual filter builder includes browser-side fuzzy column search for quickly locating columns; it must still submit exact selected/typed column names to the existing Python validation path.
- Derived columns are post-filter projections. They must be validated and compiled in Python/DuckDB, never implemented as JavaScript-only data transforms.
- Beginner-facing UI copy should avoid data-structure jargon such as “list/lista” for membership filters. Prefer “é um destes valores” / “is one of these values” and keep raw DSL keywords (`IN`, `EM`) documented only where useful.
- Step 4 in the UI should show parsed result cards, warnings, and friendly next steps. Keep raw JSON/technical details behind a collapsed disclosure for support/debugging only.
- UI output-name controls must not repeat source filenames in labels, helper text, previews, or ARIA labels. In Step 5, identify rows by artifact type such as `Base limpa` / `Cleaned base` or `Sumarização` / `Summarization`; the editable filename field is the only place the output base name should appear.
- When composing output filenames, never concatenate base names and suffixes naively. Normalize separator boundaries for `.`, `_`, `-`, and surrounding spaces, strip only known generated suffixes, and avoid outputs such as doubled separators, repeated suffixes, or `name_- 1_suffix`.
- Avoid redundant UI chrome: do not add a second preview line that repeats the composed filename, and do not add hover titles that duplicate visible text. Keep tooltips/ARIA descriptions only where visible text is just a symbol, icon, or otherwise ambiguous.
- Summarization copy should explain the grouped-total action directly without referencing external products or assuming the user lacks domain knowledge.
- ZIP passwords are session-only. Never persist, log, or include them in report JSON.
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
- `manual-test-data/`: local-only sample CSV/Parquet/XLSX files for manual UI testing. This directory must stay ignored by Git.
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
# build script also supports machines with uv but no python command:
uv run --extra freeze python -m PyInstaller packaging\pyinstaller\dataslicer.spec --noconfirm --clean
```
CLI examples:
```bash
gt-dataslicer inspect input.csv
gt-dataslicer validate-filter input.csv --where 'STATUS EM ("ATIVO", "SUSPENSO")'
gt-dataslicer filter input.csv -o output.csv --where 'CD_EMPRESA = 1 E ST_CONTRATO != "P"'
gt-dataslicer filter input.csv -o output --format xlsx --where 'STATUS = "ATIVO"'
gt-dataslicer filtrar input.csv --saida output.parquet --filtro 'STATUS = "ATIVO"'
gt-dataslicer filtrar input.csv --saida output.csv --coluna-derivada '{"source":"CPF","name":{"prefix":"LIMPO","separator":"_"},"transforms":[{"operation":"keep_digits"}]}'
gt-dataslicer filtrar dados.zip --senha-zip senha --saida output.csv --filtro 'STATUS = "ATIVO"'
gt-dataslicer filtrar input.xlsx --todas-abas --saida saidas --filtro 'STATUS = "ATIVO"'
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
- Preserve the pipeline boundary: parse/validate in filters and derived-column models, option merging in `config.py`, execution/query assembly in `DuckDBEngine`, file writing in `export/`.
- UI code must preserve the same pipeline boundary. Do not reimplement filtering, query assembly, CSV export, or XLSX export in JavaScript or UI-specific Python.
- The visible desktop product name is `DataSlicer` with descriptor `Powered by Grant Thornton Brasil`. Do not expose the `GT` acronym, the Mobius symbol, or invented Grant Thornton logo assets in the UI.
- Freezing is Windows-first and uses PyInstaller one-file mode through `packaging/pyinstaller/dataslicer.spec`; use the spec file instead of ad hoc PyInstaller commands.
- Frozen builds must include `ui/web`, `ui/icon.png`, and `filters/grammar.lark` as data files. The built `dist\DataSlicer.exe` is self-contained and must not require Python or `uv` at runtime.
- No async patterns or DI container are used. `DuckDBEngine` owns an in-memory DuckDB connection; instantiate directly unless a test needs monkeypatching.
- Tests prefer real temp files via `tmp_path`, `pytest.raises`, and `typer.testing.CliRunner`; there is no shared `conftest.py`.

## Important Files
- `pyproject.toml`: hatchling build, dependencies, `gt-dataslicer` script, pytest config (`testpaths = ["tests"]`, `addopts = "-q"`).
- `README.md`: user-facing examples and output behavior. Keep it simple, non-technical, and copy/paste oriented; avoid architecture details unless they directly help users.
- `src/gt_dataslicer/cli.py`: localized app factory, `main()`, and commands `inspect`, `validate-filter`, and `filter`.
- `src/gt_dataslicer/ui/app.py`: Pywebview window creation and desktop entry point.
- `src/gt_dataslicer/ui/api.py`: JSON-safe bridge used by the static UI.
- `src/gt_dataslicer/ui/web/`: desktop UI assets; keep copy simple, practical, and non-technical.
- `packaging/pyinstaller/dataslicer.spec`: canonical build definition for `dist\DataSlicer.exe`; it must include UI assets, `filters/grammar.lark`, and the app icon while avoiding test files/brand PDFs.
- `scripts/build-dataslicer.ps1`: PowerShell wrapper for the PyInstaller build; it uses `python` when available and falls back to `uv`.
- `src/gt_dataslicer/i18n.py`: pt-BR/en-US message templates and user-facing error localization.
- `src/gt_dataslicer/config.py`: config file loading, preset selection, CLI/config merge, output format resolution.
- `src/gt_dataslicer/derived.py`: shared CLI/UI/config model for post-filter derived columns, DuckDB SQL compilation, and simple Excel formula generation.
- `src/gt_dataslicer/engine/duckdb_engine.py`: main CSV inspection/filter/export pipeline.
- `src/gt_dataslicer/filters/grammar.lark`: DSL operators and syntax.
- `src/gt_dataslicer/filters/compiler.py`: AST-to-SQL validation and compilation.
- `src/gt_dataslicer/export/excel.py`: XLSX limits, splitting, summary sheet, cell normalization.
- `src/gt_dataslicer/export/parquet.py`: DuckDB-native Parquet writer.
- `tests/integration/test_cli.py`: best reference for supported CLI behavior and exit codes.

## Runtime/Tooling Preferences
- Runtime: Python `>=3.12`.
- Build backend: Hatchling (`hatchling.build`); wheel package is `src/gt_dataslicer`.
- Runtime dependencies: DuckDB, Lark, OpenPyXL, PyYAML, Pywebview, PyZipper, Rich, Typer, XlsxWriter.
- Dev dependencies: pytest, pytest-cov, openpyxl.
- Freeze dependencies: PyInstaller and Pillow via `python -m pip install -e .[freeze]`, or `uv run --extra freeze ...` on machines without a `python` command.
- No formatter/linter/type-checker configuration is present; do not invent a new style tool unless explicitly requested.
- No `docs/`, Makefile, tox/nox, pre-commit, or CI config exists in this repository.

## Testing & QA
- Primary test command: `pytest`.
- Do not repeatedly run the full test suite or rebuild `dist\DataSlicer.exe` after every small edit. During implementation, use static inspection or narrow targeted checks only when needed. Run the relevant tests and rebuild the app as the final verification step immediately before finishing.
- Unit tests cover config precedence, bilingual DSL parsing, SQL compilation, engine row counts, and XLSX safety/summary behavior.
- Integration tests use `CliRunner` for real CLI flows: filtering, validation, config presets, lookups, dedupe/sort, date casting, strict values, rejects, output formats, and localized CLI output.
- For DSL changes, update parser and compiler tests together; grammar-only changes are incomplete without SQL validation coverage.
- For CLI/config/i18n changes, add or update integration coverage in `tests/integration/test_cli.py` because option aliases, command aliases, language defaults, help text, and exit codes are user-facing.
- For UI changes, test the Python bridge, visual filter conversion, job manager, and CLI launch routing. Do not require a live Pywebview window in automated tests; monkeypatch `webview.create_window` and `webview.start` when launch behavior needs coverage.
- For UI asset changes, prefer targeted static checks/tests during development. Defer the full pytest run and PyInstaller rebuild until the final verification pass; do not keep rebuilding the executable after every small edit.
- After applying UI/front-end changes, kill any older local app/static servers left open from previous runs before starting a fresh app/server instance. Then run the app and use the Browser skill (`$browser:control-in-app-browser`) to test the front-end in the in-app browser before finishing. Verify the visible workflow, scrolling, tabs, form controls, and any changed UX states. This browser check is required in addition to automated tests, but it does not require rebuilding the executable unless packaging changed.
- For freezing changes, test the launcher/spec/script as files and imports. Do not require a PyInstaller build in normal tests unless an explicit opt-in environment variable is added.
