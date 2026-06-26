# DataSlicer

DataSlicer is a desktop app for filtering large CSV, Parquet, Excel `.xlsx`, and ZIP-delivered data files, then saving the result as CSV, Excel, or Parquet.

The main experience is the visual app. It lets you choose files, build filters, create cleaned columns, summarize data, and export results without using a command interface.

## Run The Desktop App

From a development checkout:

```bash
uv run python -m gt_dataslicer.ui.app
```

The visible product name is `DataSlicer`.

## Build The Windows App

The Windows build uses the canonical PyInstaller spec:

```powershell
uv run --extra freeze python -m PyInstaller packaging\pyinstaller\dataslicer.spec --noconfirm --clean
```

The generated executable is:

```text
dist\DataSlicer.exe
```

The executable is self-contained and does not require Python or `uv` at runtime. It uses Pywebview and expects the WebView2 Runtime on Windows.

## Visual Workflow

In the app you can:

- choose CSV, Parquet, Excel, or ZIP input files;
- queue multiple files;
- build filters with field/value controls;
- search columns by typing part of the name;
- export to CSV, Excel, or Parquet;
- create cleaned derived columns such as digits-only CPF/CNPJ values;
- choose output columns, rename columns, deduplicate rows, sort rows, summarize groups, and generate reports.

## Manual Test Data

For local testing without real data, create files under `manual-test-data/`.

That directory is ignored by Git. Useful sample filenames are:

```text
manual-test-data\clientes.csv
manual-test-data\clientes.parquet
manual-test-data\clientes.xlsx
```

Use the same filter across formats to compare results:

```text
CD_EMPRESA = 1 E ST_CONTRATO != "P" E CD_NATUREZA_OPERACAO NAO EM (14, 15) E CD_MODALIDADE <= 13
```

## Filter Expressions

The visual builder writes the same safe expression language used by the Python engine.

Common expressions:

```text
STATUS = "ATIVO"
STATUS != "CANCELADO"
STATUS EM ("ATIVO", "SUSPENSO")
CD_NATUREZA_OPERACAO NAO EM (14, 15)
DATA_ADMISSAO ENTRE "2020-01-01" E "2023-12-31"
NOME contém "SILVA"
CPF NÃO É NULO
OBSERVACAO E VAZIO
```

`STATUS EM ("ATIVO", "SUSPENSO")` means the status is one of those values. In the visual app, choose “é um destes valores” and separate values with commas.

You can combine rules with `E`, `OU`, and `NÃO`:

```text
STATUS = "ATIVO" E NÃO (TIPO = "TEMPORARIO" OU CIDADE = "RIO")
```

Accents are optional in Portuguese operators:

```text
NOME contem "SILVA"
NOME contém "SILVA"
CPF NAO E NULO
CPF NÃO É NULO
```

For column names with spaces, accents, punctuation, or operator names, use brackets or backticks:

```text
[Nome completo] contém "SILVA"
[E] = 1
`STATUS FINAL` = "ATIVO"
```

## Derived Columns

Use the app’s “Criar novas colunas” controls to clean or format values without writing formulas.

Common transformations include:

- keeping only digits;
- removing accents;
- converting text to uppercase;
- adding a prefix or suffix;
- formatting CPF, CNPJ, or phone numbers.

Derived columns are compiled and validated in Python/DuckDB as part of the same export pipeline as filters.
