# gt-dataslicer

`gt-dataslicer` is a Python CLI for filtering large CSV files with a safe expression language and exporting matching rows to `.xlsx`.

```bash
gt-dataslicer filter input.csv -o output.xlsx --where 'CD_EMPRESA = 1 AND ST_CONTRATO != "P"'
gt-dataslicer inspect input.csv
gt-dataslicer validate-filter input.csv --where 'STATUS IN ("ATIVO", "SUSPENSO")'
```

The tool uses DuckDB for CSV scanning/filtering and XlsxWriter for constant-memory Excel output.

