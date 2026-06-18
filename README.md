# gt-dataslicer

`gt-dataslicer` filtra arquivos grandes e salva apenas as linhas que você quer.

Por padrão, o resultado sai em CSV. Se você quiser abrir no Excel, salve em XLSX. Se o resultado for grande ou for usado por ferramentas de análise, salve em Parquet.

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

- escolher arquivos CSV, Parquet, Excel ou ZIP;
- colocar vários arquivos em fila;
- montar filtros com campos e valores, sem escrever comandos;
- encontrar colunas rapidamente digitando parte do nome, mesmo em arquivos com muitas colunas;
- salvar em CSV, Excel ou Parquet;
- criar novas colunas limpas, como CPF só com números;
- escolher colunas, remover duplicados e gerar relatório quando precisar.

## Gerar executável do DataSlicer

No Windows, você pode gerar um executável portátil:

```powershell
python -m pip install -e .[dev,freeze]
.\scripts\build-dataslicer.ps1
```

Para repetir o conjunto direto de dependências usado na última verificação de release:

```powershell
python -m pip install -e .[dev,freeze] -c requirements-release.txt
```

Se você não tiver o comando `python`, mas tiver `uv`, o mesmo script usa `uv` automaticamente:

```powershell
uv run --extra freeze python -m PyInstaller packaging\pyinstaller\dataslicer.spec --noconfirm --clean
```

O arquivo final fica em:

```text
dist\DataSlicer.exe
```

Esse executável não precisa de Python nem de `uv` para rodar. Ele usa Pywebview e espera que o WebView2 Runtime esteja instalado no Windows.

## Exemplos rápidos

Salvar em CSV:

```bash
gt-dataslicer filtrar input.csv --saida output.csv --filtro 'STATUS EM ("ATIVO", "SUSPENSO")'
```

Filtrar Parquet:

```bash
gt-dataslicer filtrar input.parquet --saida output.csv --filtro 'STATUS = "ATIVO"'
```

Filtrar Excel:

```bash
gt-dataslicer filtrar input.xlsx --saida output.csv --filtro 'STATUS = "ATIVO"'
```

Se uma célula do Excel tiver fórmula, o DataSlicer usa o valor salvo no arquivo. Ele não recalcula fórmulas. Se uma fórmula ainda não tiver valor salvo, abra a planilha no Excel ou LibreOffice, recalcule, salve e tente de novo.

Arquivos Excel com tamanho interno excessivo, abas demais selecionadas ou uma área usada declarada como grande demais são recusados com uma mensagem de orientação. Isso evita que uma planilha corrompida ou com linhas/colunas vazias até o limite do Excel trave a leitura.

Filtrar todas as abas de um Excel:

```bash
gt-dataslicer filtrar input.xlsx --todas-abas --saida saidas --filtro 'STATUS = "ATIVO"'
```

Filtrar vários arquivos em sequência:

```bash
gt-dataslicer filtrar janeiro.csv fevereiro.parquet --saida filtrado.csv --filtro 'STATUS = "ATIVO"'
```

Filtrar arquivos dentro de um ZIP com senha:

```bash
gt-dataslicer filtrar dados.zip --senha-zip minha-senha --saida filtrado.csv --filtro 'STATUS = "ATIVO"'
```

Salvar em Excel:

```bash
gt-dataslicer filtrar input.csv --saida output.xlsx --filtro 'STATUS = "ATIVO"'
```

No XLSX, valores decimais e números inteiros muito longos podem ser salvos como texto para evitar perda silenciosa de precisão do Excel. Textos maiores que o limite de uma célula do Excel são recusados com uma mensagem clara em vez de serem cortados.

Salvar em Parquet:

```bash
gt-dataslicer filtrar input.csv --saida output.parquet --filtro 'STATUS = "ATIVO"'
```

Ver as colunas do arquivo:

```bash
gt-dataslicer inspecionar input.csv
```

Testar se um filtro está correto antes de gerar o arquivo:

```bash
gt-dataslicer validar-filtro input.csv --filtro 'VALOR_TOTAL > 1000'
```

## Arquivos para teste manual

Para testar a tela visual sem usar dados reais, você pode criar arquivos locais na pasta `manual-test-data/`.

Essa pasta é ignorada pelo Git, então os arquivos de teste não entram nos commits. Um conjunto útil de arquivos é:

```text
manual-test-data\clientes.csv
manual-test-data\clientes.parquet
manual-test-data\clientes.xlsx
```

Use o mesmo filtro nos três formatos para comparar o resultado:

```text
CD_EMPRESA = 1 E ST_CONTRATO != "P" E CD_NATUREZA_OPERACAO NAO EM (14, 15) E CD_MODALIDADE <= 13
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

`STATUS EM ("ATIVO", "SUSPENSO")` quer dizer: o status é um destes valores. Na tela visual, escolha “é um destes valores” e separe os valores com vírgula.

A lista precisa ter pelo menos um valor. Para procurar células vazias ou nulas, use os filtros próprios, como `CPF É NULO`, em vez de colocar `NULL` dentro de `EM (...)`.

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

## Criar novas colunas

Na tela visual, use “Criar novas colunas” para limpar ou formatar uma coluna sem escrever fórmula.

Exemplos comuns:

- manter só números de um CPF;
- remover acentos de nomes;
- deixar texto em maiúsculas;
- adicionar um prefixo ou sufixo;
- formatar CPF, CNPJ ou telefone.

Pela CLI, use o mesmo formato de configuração da tela visual.

Exemplo direto na linha de comando:

```bash
gt-dataslicer filtrar pessoas.csv --saida pessoas_limpas.csv \
  --selecionar NOME \
  --coluna-derivada '{"source":"CPF","name":{"prefix":"LIMPO","separator":"_"},"transforms":[{"operation":"keep_digits"}]}'
```

Exemplo com arquivo `derivadas.yaml`:

```yaml
derived_columns:
  - source: CPF
    name:
      prefix: LIMPO
      separator: "_"
    transforms:
      - operation: keep_digits
```

Rodando:

```bash
gt-dataslicer filtrar pessoas.csv --saida pessoas_limpas.csv --colunas-derivadas-arquivo derivadas.yaml
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
- salvar configuração pela tela visual e reutilizar na CLI;
- usar arquivos externos de consulta com `--consulta`;
- ler arquivos Parquet, Excel `.xlsx` e ZIP;
- salvar o resultado em Parquet com `--formato parquet` ou usando saída `.parquet`;
- excluir o ZIP automaticamente depois de extrair com sucesso usando `--excluir-zip-apos-extrair`;
- remover linhas duplicadas com `--deduplicar`;
- remover linhas duplicadas por chave com `--chave-deduplicacao` junto com `--ordenar`, para deixar claro qual linha fica;
- ordenar o resultado com `--ordenar`;
- gerar relatório com `--relatorio`;
- salvar rejeições de leitura com `--rejeitados`.

Em `--modo-tipado`, todas as colunas do CSV são validadas antes da exportação, mesmo quando `--selecionar` exporta apenas algumas delas. Assim, um valor inválido em uma coluna não selecionada ainda falha a execução ou aparece no arquivo de rejeições quando `--store-rejects` está ativo.

O DataSlicer não permite salvar a saída, o relatório ou o arquivo de rejeições por cima do arquivo de entrada, de consultas externas ou entre si.

Exemplo:

```bash
gt-dataslicer filtrar pessoas.csv --saida ativos.csv \
  --filtro 'ID EM @ids_ativos E STATUS = "ATIVO"' \
  --consulta ids_ativos=ids.csv:ID \
  --deduplicar \
  --ordenar Nome \
  --relatorio relatorio.json
```
