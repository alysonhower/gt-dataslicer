# gt-dataslicer

`gt-dataslicer` filtra arquivos CSV grandes e salva apenas as linhas que você quer.

Por padrão, o resultado sai em CSV. Se você quiser abrir no Excel, também pode salvar em XLSX.

## Usar com tela visual

A forma mais simples de usar é abrir o DataSlicer:

```bash
dataslicer
```

Ou, pelo comando principal:

```bash
gt-dataslicer abrir
```

Na tela visual você pode:

- escolher o arquivo CSV;
- montar filtros com campos e listas, sem escrever comandos;
- salvar em CSV ou Excel;
- escolher colunas, remover duplicados e gerar relatório quando precisar.

## Gerar executável do DataSlicer

No Windows, você pode gerar um executável portátil:

```powershell
python -m pip install -e .[dev,freeze]
.\scripts\build-dataslicer.ps1
```

O arquivo final fica em:

```text
dist\DataSlicer.exe
```

Esse executável usa Pywebview e espera que o WebView2 Runtime esteja instalado no Windows.

## Exemplos rápidos

Salvar em CSV:

```bash
gt-dataslicer filtrar input.csv --saida output.csv --filtro 'STATUS EM ("ATIVO", "SUSPENSO")'
```

Salvar em Excel:

```bash
gt-dataslicer filtrar input.csv --saida output.xlsx --filtro 'STATUS = "ATIVO"'
```

Ver as colunas do arquivo:

```bash
gt-dataslicer inspecionar input.csv
```

Testar se um filtro está correto antes de gerar o arquivo:

```bash
gt-dataslicer validar-filtro input.csv --filtro 'VALOR_TOTAL > 1000'
```

## Como escrever filtros

Use o nome da coluna, um operador e o valor desejado.

```text
STATUS = "ATIVO"
VALOR_TOTAL > 1000
CD_EMPRESA = 1 E ST_CONTRATO != "P"
```

Filtros comuns:

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

Você pode usar `E`, `OU` e `NÃO` para combinar regras:

```text
STATUS = "ATIVO" E NÃO (TIPO = "TEMPORARIO" OU CIDADE = "RIO")
```

Os acentos são opcionais nos operadores em português:

```text
NOME contem "SILVA"
NOME contém "SILVA"
CPF NAO E NULO
CPF NÃO É NULO
```

## Escolher colunas

Para salvar só algumas colunas:

```bash
gt-dataslicer filtrar input.csv --saida output.csv \
  --filtro 'STATUS = "ATIVO"' \
  --selecionar NOME \
  --selecionar VALOR_TOTAL
```

Para renomear uma coluna no arquivo final:

```bash
gt-dataslicer filtrar input.csv --saida output.csv \
  --filtro 'STATUS = "ATIVO"' \
  --selecionar NOME \
  --renomear NOME=Nome
```

## Idioma

A CLI usa português por padrão.

Para ver mensagens em inglês:

```bash
gt-dataslicer --idioma en-US validar-filtro input.csv --filtro 'STATUS IN ("ACTIVE", "SUSPENDED")'
```

## Compatibilidade com comandos em inglês

Os comandos e opções em inglês continuam funcionando:

```bash
gt-dataslicer filter input.csv --output output.csv --where 'STATUS IN ("ATIVO", "SUSPENSO")'
gt-dataslicer validate-filter input.csv --where 'VALOR_TOTAL > 1000'
```

## Colunas com nomes especiais

Se uma coluna tiver espaço, acento, pontuação ou o mesmo nome de um operador, use colchetes ou crases:

```text
[Nome completo] contém "SILVA"
[E] = 1
`STATUS FINAL` = "ATIVO"
```

## Recursos avançados

Você também pode:

- usar arquivos de configuração com `--configuracao`;
- usar listas externas com `--consulta`;
- remover linhas duplicadas com `--deduplicar`;
- ordenar o resultado com `--ordenar`;
- gerar relatório com `--relatorio`;
- salvar rejeições de leitura com `--rejeitados`.

Exemplo:

```bash
gt-dataslicer filtrar pessoas.csv --saida ativos.csv \
  --filtro 'ID EM @ids_ativos E STATUS = "ATIVO"' \
  --consulta ids_ativos=ids.csv:ID \
  --deduplicar \
  --ordenar Nome \
  --relatorio relatorio.json
```
