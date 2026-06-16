# gt-dataslicer

`gt-dataslicer` is a Python CLI for filtering large CSV files with a safe expression language and exporting matching rows to `.csv` by default, with optional `.xlsx` output.

```bash
gt-dataslicer filter input.csv -o output.csv --where 'CD_EMPRESA = 1 AND ST_CONTRATO != "P"'
gt-dataslicer filter input.csv -o output.xlsx --where 'STATUS = "ATIVO"'
gt-dataslicer filter input.csv -o output --format xlsx --where 'STATUS = "ATIVO"'
gt-dataslicer inspect input.csv
gt-dataslicer validate-filter input.csv --where 'STATUS IN ("ATIVO", "SUSPENSO")'
```

The tool uses DuckDB for CSV scanning/filtering and native CSV export. Excel output uses XlsxWriter in constant-memory mode.
