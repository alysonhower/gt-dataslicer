# gt-dataslicer

`gt-dataslicer` é uma CLI Python para filtrar arquivos CSV grandes com uma linguagem de filtros segura e exportar os resultados para CSV por padrão, com suporte opcional a XLSX.

O processamento usa DuckDB para leitura, filtragem, ordenação, deduplicação e exportação CSV. A exportação Excel usa XlsxWriter em modo de memória constante.

## Uso Básico

CSV é o formato padrão:

```bash
gt-dataslicer filter input.csv -o output.csv --where 'CD_EMPRESA = 1 E ST_CONTRATO != "P"'
gt-dataslicer filter input.csv -o output --where 'STATUS EM ("ATIVO", "SUSPENSO")'
```

Para Excel, use `.xlsx` ou `--format xlsx`:

```bash
gt-dataslicer filter input.csv -o output.xlsx --where 'STATUS = "ATIVO"'
gt-dataslicer filter input.csv -o output --format xlsx --where 'STATUS = "ATIVO"'
```

Outros comandos:

```bash
gt-dataslicer inspect input.csv
gt-dataslicer validate-filter input.csv --where 'STATUS EM ("ATIVO", "SUSPENSO")'
```

## Idioma Da CLI

O idioma padrão da saída da CLI é `pt-BR`.

Para exibir mensagens e ajuda em inglês, passe `--lang en-US` antes do comando:

```bash
gt-dataslicer --lang en-US validate-filter input.csv --where 'STATUS IN ("ACTIVE", "SUSPENDED")'
gt-dataslicer --lang en-US --help
```

Valores aceitos:

- `pt-BR`
- `en-US`

## Filtros Em pt-BR E en-US

A linguagem de filtros aceita operadores em português e inglês. A sintaxe em inglês existente continua suportada.

Exemplo em pt-BR:

```text
CD_EMPRESA = 1
E ST_CONTRATO != "P"
E CD_NATUREZA_OPERACAO NAO EM (14, 15)
E CD_MODALIDADE <= 13
```

Exemplo com acentos:

```text
VALOR_TOTAL > 1000
E DATA_ADMISSAO ENTRE "2020-01-01" E "2023-12-31"
E NOME contém "SILVA"
E CPF NÃO É NULO
E STATUS EM ("ATIVO", "SUSPENSO")
E CIDADE regex "^SAO "
E NÃO (TIPO = "TEMPORARIO" OU STATUS = "CANCELADO")
```

Exemplo equivalente em inglês:

```text
VALOR_TOTAL > 1000
AND DATA_ADMISSAO BETWEEN "2020-01-01" AND "2023-12-31"
AND NOME contains "SILVA"
AND CPF IS NOT NULL
AND STATUS IN ("ATIVO", "SUSPENSO")
AND CIDADE regex "^SAO "
AND NOT (TIPO = "TEMPORARIO" OR STATUS = "CANCELADO")
```

Para os operadores pt-BR suportados, os acentos são opcionais:

- `NAO` ou `NÃO`
- `E NULO` ou `É NULO`
- `contem` ou `contém`
- `comeca com` ou `começa com`

Se uma coluna tiver o mesmo nome de uma palavra-chave ou operador, use colchetes ou crases:

```text
[E] = 1
[OU] = "SIM"
[NÃO] = "VALOR"
`STATUS FINAL` = "ATIVO"
```

## Exemplos Com Transformações

```bash
gt-dataslicer filter input.csv -o output.csv \
  --where 'STATUS EM ("ATIVO", "SUSPENSO")' \
  --select NOME \
  --select VALOR_TOTAL \
  --rename NOME=Nome
```

```bash
gt-dataslicer filter pessoas.csv -o ativos.csv \
  --where 'ID EM @ids_ativos E STATUS = "ATIVO"' \
  --lookup ids_ativos=ids.csv:ID \
  --dedupe \
  --sort Nome
```
