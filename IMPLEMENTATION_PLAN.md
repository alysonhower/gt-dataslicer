# Implementar Saída Parquet, Etapa 3 Visual e Colunas Derivadas Com Paridade CLI/UI

## Summary

Adicionar Parquet como formato de saída, melhorar visualmente a Etapa 3 e permitir colunas derivadas pós-filtro. A UI será simples e guiada, mas a CLI terá compatibilidade 1:1: tudo que o usuário conseguir configurar visualmente também poderá ser executado pela CLI e salvo em config YAML/JSON/TOML.

## Key Changes

### Saída Parquet

- Expandir `OutputFormat` para `csv|xlsx|parquet`.
- Suportar:
  - UI: cartão visual “Parquet”.
  - CLI: `--formato parquet` / `--format parquet`.
  - Config: `output_format: parquet`.
  - Sufixo: `.parquet`.
- Exportar Parquet via DuckDB:
  - `COPY ({query}) TO 'output.parquet' (FORMAT PARQUET)`.
- CSV continua padrão; Excel continua opcional.
- Multi-input usa a mesma regra de nomes para CSV, XLSX e Parquet.

### Etapa 3 Visual

- Substituir seletor simples por cartões:
  - CSV: recomendado para a maioria dos casos.
  - Excel: bom para abrir no Excel, com aviso de limite.
  - Parquet: bom para bases grandes e ferramentas analíticas.
- “Escolher destino” vira ação principal.
- Campo de caminho permanece como controle manual secundário.
- Ao trocar formato, atualizar extensão `.csv`, `.xlsx` ou `.parquet`.
- Opções avançadas continuam recolhidas.

### Colunas Derivadas

- Criar modelo único usado por UI, CLI e config:
  ```yaml
  derived_columns:
    - source: CPF
      name:
        prefix: LIMPO
        suffix: ""
        separator: "_"
      position:
        mode: append
      transforms:
        - operation: keep_digits
        - operation: add_prefix
          text: BR_
  ```
- UI:
  - seção “Criar novas colunas” na Etapa 3;
  - busca fuzzy da coluna origem;
  - preview do nome final;
  - lista visual de transformações;
  - posicionamento em opções avançadas.
- CLI:
  - `--colunas-derivadas-arquivo PATH` / `--derived-columns-file PATH` para YAML/JSON/TOML com a mesma lista acima.
  - `--coluna-derivada JSON` / `--derived-column JSON`, repetível, para uso direto em linha de comando.
  - CLI e UI aceitam exatamente o mesmo schema.
- Config:
  - `derived_columns` no preset principal.
  - CLI override combina com config: itens passados via CLI são adicionados após os itens do config.
- UI deve oferecer ação futura simples “Salvar configuração” usando esse mesmo schema, para reproduzir a execução pela CLI sem perda de capacidade.

### Transformações V1

- Implementar:
  - substituir texto;
  - maiúsculas;
  - minúsculas;
  - título;
  - aparar espaços;
  - remover espaços repetidos;
  - adicionar texto antes/depois;
  - manter só números;
  - manter só letras;
  - remover acentos;
  - remover pontuação/símbolos;
  - remover espaços;
  - preencher à esquerda/direita;
  - pegar primeiros/últimos N caracteres;
  - remover primeiros/últimos N caracteres;
  - extrair antes/depois de separador;
  - valor padrão para vazio/nulo;
  - formatar CPF, CNPJ e telefone a partir de dígitos.
- Adiar:
  - transformações numéricas;
  - transformações de data;
  - mapeamento por pares;
  - mascaramento de privacidade;
  - split por índice;
  - extrair entre separadores.

### Pipeline

- Colunas derivadas são aplicadas depois do filtro e antes da exportação.
- CSV e Parquet recebem valores materializados via DuckDB SQL.
- Excel:
  - usa fórmula gerada apenas quando a transformação é simples e segura;
  - caso contrário, usa valor materializado;
  - usuário nunca digita nem vê fórmula na UI principal.
- Colunas derivadas podem ser:
  - anexadas ao fim;
  - inseridas antes de uma coluna;
  - inseridas depois de uma coluna.
- Validar nomes duplicados, fonte ausente, parâmetros obrigatórios e cadeias conflitantes.

## Test Plan

- Parquet:
  - `--formato parquet`;
  - `.parquet`;
  - config `output_format: parquet`;
  - conflito de extensão falha claramente.
- Paridade CLI/UI:
  - payload gerado pela UI é aceito pela CLI via `--coluna-derivada JSON`;
  - arquivo usado por `--colunas-derivadas-arquivo` produz o mesmo resultado que a UI;
  - config YAML/JSON/TOML cobre todas as transformações v1.
- Colunas derivadas:
  - cada transformação v1 gera saída correta;
  - transformações encadeadas preservam ordem;
  - posicionamento append/before/after funciona;
  - multi-input aplica as mesmas colunas em todos os arquivos.
- Excel:
  - fórmulas simples funcionam;
  - transformações complexas são materializadas;
  - referências permanecem corretas após seleção/renomeação/reordenação.
- UI:
  - Step 3 visual;
  - cartões de formato;
  - picker de destino;
  - preview de colunas derivadas;
  - validações amigáveis.
- Final:
  - rodar testes focados durante desenvolvimento;
  - rodar `python -m pytest -q` uma vez no final;
  - usar Browser skill para validar front-end;
  - rebuild só se empacotamento/assets exigirem.

## Assumptions

- “CLI e UI 1:1” significa mesma capacidade funcional e mesmo schema interno, não necessariamente a mesma ergonomia visual.
- CLI pode usar JSON inline ou arquivo YAML/JSON/TOML para representar recursos complexos.
- CSV permanece padrão.
- Parquet usa `.parquet` como extensão de saída.
- Nenhuma lógica de filtro/exportação será duplicada em JavaScript.
