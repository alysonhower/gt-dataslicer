const state = {
  api: null,
  inputPath: "",
  inputPaths: [],
  outputPath: "",
  outputPaths: [],
  outputNames: [],
  zipPasswords: [],
  resolvedInputs: [],
  columns: [],
  columnTypes: {},
  language: "pt-BR",
  filterMode: "visual",
  pollTimer: null,
  activeJobId: "",
  runStepState: "pending",
  runStepSummary: "",
  columnSuggestionListId: 0,
  eventsBound: false,
  derivedColumnId: 0,
  lookupId: 0,
  outputSplitMode: "sheets",
  outputMaxRowsPerSheet: "",
  outputSheetsPerFile: "",
};

const text = {
  "pt-BR": {
    readyTitle: "Pronto",
    readyText: "Escolha um arquivo de entrada para começar.",
    inspecting: "Lendo o arquivo...",
    validating: "Validando filtro...",
    valid: "Filtro válido.",
    running: "Gerando o arquivo...",
    canceling: "Cancelando...",
    cancelled: "Execução cancelada.",
    closeBlocked: "A execução ainda está em andamento. Cancele ou aguarde terminar antes de fechar.",
    done: "Arquivo gerado com sucesso.",
    error: "Algo precisa de atenção.",
    chooseCsv: "Escolha um arquivo de entrada.",
    chooseOutput: "Escolha onde salvar o resultado.",
    noColumns: "Escolha um arquivo para carregar as colunas.",
    droppedFileNeedsPicker: "Use o botão Procurar arquivo para garantir acesso ao caminho completo do arquivo.",
    noFile: "Nenhum arquivo escolhido",
    columnsLoaded: "colunas carregadas.",
    schemaMismatch: "Colunas ou tipos diferentes do primeiro arquivo.",
    schemaMismatchShort: "Há diferenças na fila.",
    columnSearchPlaceholder: "Buscar coluna",
    inputQueue: "Arquivos na fila",
    outputName: "Nome de saída",
    outputNamePlaceholder: "Opcional",
    zipPasswords: "Senhas de ZIP",
    addZipPassword: "Adicionar senha",
    clearZipPasswords: "Limpar senhas",
    zipPasswordSessionOnly: "Usadas só nesta execução. Não são salvas.",
    zipPasswordsStored: "{count} senha(s) guardada(s) só nesta sessão.",
    allExcelSheets: "Processar todas as abas do Excel",
    reuseSchema: "Reutilizar o esquema do primeiro arquivo",
    deleteZipAfterExtract: "Excluir ZIP após extrair com sucesso",
    rowsWritten: "linhas gravadas.",
    bridgeNotReady: "A ponte com Python ainda não está pronta.",
    bridgeWaiting: "Aguardando a ponte com Python.",
    language: "Idioma",
    stepFile: "1. Arquivo",
    stepFilter: "2. Filtro",
    stepOutput: "3. Saída",
    stepRun: "4. Gerar",
    stageOne: "Etapa 1",
    stageTwo: "Etapa 2",
    stageThree: "Etapa 3",
    stageFour: "Etapa 4",
    stepFileWaiting: "Escolha o arquivo",
    stepFileReady: "{count} arquivo(s)",
    stepFileWarning: "Verifique a fila",
    stepFilterNoRules: "Sem regras",
    stepFilterReady: "{count} regra(s)",
    stepFilterNeedsFix: "Complete ou remova a regra",
    stepFilterAdvanced: "Expressão avançada",
    stepFilterVisualWithInactiveAdvanced: "{count} regra(s); avançado inativo",
    stepFilterNoRulesWithInactiveAdvanced: "Sem regras; avançado inativo",
    stepFilterAdvancedWithInactiveVisual: "Expressão avançada; visual inativo",
    stepFilterNoAdvancedWithInactiveVisual: "Sem expressão; visual inativo",
    stepOutputWaiting: "Escolha o destino",
    stepOutputReady: "{format} escolhido",
    stepRunBlocked: "Aguardando etapas",
    stepRunReady: "Pronto para gerar",
    stepRunRunning: "Gerando",
    stepRunDone: "Concluído",
    stepRunCancelled: "Cancelado",
    stepRunError: "Precisa de atenção",
    chooseFile: "Escolha o arquivo",
    browseInput: "Procurar arquivo",
    dropStrong: "Arraste o arquivo aqui",
    dropHelp: "ou use o botão para procurar no computador.",
    fileLabel: "Arquivo",
    sizeLabel: "Tamanho",
    columnsLabel: "Colunas",
    readOptions: "Opções de leitura",
    encoding: "Codificação",
    delimiter: "Delimitador",
    nullValue: "Valor nulo",
    emptyPlaceholder: "vazio",
    buildFilter: "Monte o filtro",
    filterMode: "Modo de filtro",
    visual: "Visual",
    advanced: "Avançado",
    combineRules: "Combinar regras",
    allRules: "todas as regras",
    anyRule: "qualquer regra",
    addRule: "Adicionar regra",
    noFilterHint: "Sem regras, todas as linhas serão exportadas.",
    advancedFilter: "Filtro avançado",
    checkExpression: "Verificar expressão",
    chooseOutputTitle: "Escolha a saída",
    chooseDestination: "Escolher destino",
    summarize: "Gerar resumo",
    summaryOnly: "Gerar apenas o resumo",
    summaryGroupBy: "Agrupar por",
    summaryTotals: "Somar colunas no resumo",
    summaryColumnPlaceholder: "Uma coluna por linha",
    format: "Formato",
    formatCsvTitle: "CSV",
    formatCsvHelp: "Bom para compartilhar e abrir em planilhas.",
    formatExcelTitle: "Excel",
    formatExcelHelp: "Pronto para abrir no Excel, com divisão quando necessário.",
    formatParquetTitle: "Parquet",
    formatParquetHelp: "Melhor para bases grandes e ferramentas analíticas.",
    splitXlsxNoticeTitle: "Excel pode gerar mais de um arquivo",
    splitXlsxNoticeText: "Se a saída for dividida, os arquivos serão criados na mesma pasta usando o padrão {pattern}.",
    saveAs: "Salvar em",
    chooseSavePlaceholder: "Escolha onde salvar",
    derivedColumnsTitle: "Criar novas colunas",
    derivedColumnsHelp: "Opcional: crie colunas limpas a partir das colunas filtradas.",
    addDerivedColumn: "Adicionar coluna",
    noDerivedColumns: "Nenhuma coluna nova será criada.",
    loadConfig: "Carregar configuração",
    configLoaded: "Configuração carregada.",
    saveConfig: "Salvar configuração",
    configSaved: "Configuração salva.",
    lookupFilesTitle: "Consultas CSV",
    lookupFilesHelp: "Opcional: use CSVs de apoio no filtro avançado.",
    addLookup: "Adicionar consulta",
    noLookups: "Nenhuma consulta CSV será usada.",
    removeLookup: "Remover consulta",
    lookupName: "Nome",
    lookupNamePlaceholder: "empresas",
    lookupPath: "CSV de consulta",
    lookupPathPlaceholder: "Escolha um CSV",
    lookupColumn: "Coluna",
    lookupColumnPlaceholder: "ID",
    chooseLookup: "Escolher CSV",
    lookupNameRequired: "Informe um nome para esta consulta.",
    lookupPathRequired: "Escolha o CSV desta consulta.",
    lookupColumnRequired: "Informe a coluna desta consulta.",
    lookupSummary: "Consulta `{name}` usando `{column}`.",
    sourceColumn: "Coluna de origem",
    derivedOutputName: "Nome da nova coluna",
    derivedOutputNamePlaceholder: "Ex.: CPF limpo",
    namePrefix: "Prefixo",
    nameSuffix: "Sufixo",
    nameSeparator: "Separador",
    prefixPlaceholder: "LIMPO",
    suffixPlaceholder: "FORMATADO",
    addTransformation: "Adicionar transformação",
    removeDerivedColumn: "Remover coluna",
    removeTransformation: "Remover transformação",
    moveTransformationUp: "Mover transformação para cima",
    moveTransformationDown: "Mover transformação para baixo",
    derivedPosition: "Posição",
    positionAppend: "No fim da tabela",
    positionBefore: "Antes de uma coluna",
    positionAfter: "Depois de uma coluna",
    positionTarget: "Coluna de referência",
    newColumn: "Nova coluna",
    derivedSummaryEmpty: "Escolha uma coluna de origem e uma transformação.",
    derivedSummary: "Criar coluna `{name}` a partir de `{source}`.",
    derivedSampleValue: "Exemplo",
    derivedSamplePlaceholder: "Ex.: 123.456.789-01",
    derivedSampleBefore: "Antes",
    derivedSampleAfter: "Depois",
    derivedSourceRequired: "Escolha a coluna de origem desta nova coluna.",
    derivedPositionTargetRequired: "Escolha a coluna de referência para esta posição.",
    derivedTransformOperationRequired: "Escolha a transformação.",
    derivedTransformValueRequired: "Informe o valor desta transformação.",
    derivedTransformCountRequired: "Informe uma quantidade maior que zero.",
    derivedTransformCaseConflict: "Use apenas uma transformação de maiúsculas/minúsculas nesta coluna.",
    advancedOptions: "Opções avançadas",
    advancedSummaryGroup: "Resumo",
    advancedColumnsGroup: "Colunas",
    advancedOrganizationGroup: "Organização",
    advancedDiagnosticsGroup: "Diagnóstico",
    columnsToSave: "Colunas para salvar",
    oneColumnPerLine: "Uma coluna por linha",
    renameColumns: "Renomear colunas",
    renamePlaceholder: "ANTIGO=Novo nome",
    sortBy: "Ordenar por",
    sortPlaceholder: "COLUNA ou COLUNA:desc",
    dedupeKey: "Chave de deduplicação",
    columnPlaceholder: "COLUNA",
    removeDuplicates: "Remover linhas duplicadas",
    caseInsensitive: "Não diferenciar maiúsculas em nomes de colunas",
    jsonReport: "Relatório JSON",
    rejectsCsv: "Rejeitados CSV",
    optional: "Opcional",
    chooseReport: "Escolher relatório",
    chooseRejects: "Escolher rejeitados",
    generateFile: "Gerar arquivo",
    generateResult: "Gerar resultado",
    previewRows: "Ver prévia",
    previewTitle: "Prévia das linhas",
    previewing: "Carregando prévia...",
    previewEmpty: "Nenhuma linha encontrada para a configuração atual.",
    previewLoaded: "{count} linha(s) de prévia de {path}",
    previewLoadedQueue: "{count} linha(s) de prévia do primeiro arquivo ({path}); {total} arquivo(s) na fila.",
    previewEmptyQueue: "Nenhuma linha encontrada no primeiro arquivo da fila ({path}).",
    cancelRun: "Cancelar",
    openFolder: "Abrir pasta",
    newRun: "Nova execução",
    opEquals: "igual a",
    opNotEquals: "diferente de",
    opGt: "maior que",
    opGte: "maior ou igual a",
    opLt: "menor que",
    opLte: "menor ou igual a",
    opIn: "é um destes valores",
    opNotIn: "não é nenhum destes valores",
    opBetween: "entre",
    opContains: "contém",
    opStartsWith: "começa com",
    opEndsWith: "termina com",
    opIsNull: "é nulo",
    opIsNotNull: "não é nulo",
    opIsEmpty: "é vazio",
    opIsNotEmpty: "não é vazio",
    opIsBlank: "é branco",
    opIsNotBlank: "não é branco",
    value: "Valor",
    finalValue: "Valor final",
    valueList: "Separe os valores com vírgula",
    filterColumnRequired: "Escolha uma coluna para esta regra.",
    filterValueRequired: "Informe um valor para esta regra.",
    filterBetweenRequired: "Informe os dois valores do intervalo.",
    filterListRequired: "Informe pelo menos um valor na lista.",
    removeRule: "Remover regra",
    txTrim: "Aparar espaços",
    txRemoveExtraSpaces: "Remover espaços repetidos",
    txUppercase: "Maiúsculas",
    txLowercase: "Minúsculas",
    txTitleCase: "Título",
    txReplaceText: "Substituir texto",
    txAddPrefix: "Adicionar texto antes",
    txAddSuffix: "Adicionar texto depois",
    txKeepDigits: "Manter só números",
    txKeepLetters: "Manter só letras",
    txRemoveAccents: "Remover acentos",
    txRemovePunctuation: "Remover pontuação e símbolos",
    txRemoveSpaces: "Remover espaços",
    txPadLeft: "Preencher à esquerda",
    txPadRight: "Preencher à direita",
    txTakeFirst: "Pegar primeiros caracteres",
    txTakeLast: "Pegar últimos caracteres",
    txRemoveFirst: "Remover primeiros caracteres",
    txRemoveLast: "Remover últimos caracteres",
    txExtractBefore: "Extrair antes de separador",
    txExtractAfter: "Extrair depois de separador",
    txDefaultIfBlank: "Usar padrão se vazio/nulo",
    txFormatCpf: "Formatar CPF",
    txFormatCnpj: "Formatar CNPJ",
    txFormatPhone: "Formatar telefone",
    transformGroupClean: "Limpar texto",
    transformGroupChange: "Alterar texto",
    transformGroupExtract: "Extrair texto",
    transformGroupFormat: "Formatar identificadores",
    transformValue: "Valor",
    transformNewValue: "Novo valor",
    transformCount: "Quantidade",
    transformFill: "Preenchimento",
    transformSeparator: "Separador",
    transformDefault: "Valor padrão",
    filesCreated: "Arquivos gerados",
    rowsSaved: "Linhas salvas",
    filesProcessed: "Arquivos processados",
    warnings: "Avisos",
    filesFailed: "Não foi possível processar",
    queuePartialDone: "Alguns arquivos foram gerados, mas outros precisam de atenção.",
    queueAllFailed: "Nenhum arquivo foi gerado. Veja os itens que precisam de atenção.",
    technicalDetails: "Detalhes técnicos",
    likelyCause: "Provável causa",
    nextStep: "Próximo passo",
    zipPasswordNeeded: "Este ZIP precisa de senha.",
    zipPasswordAsk: "Digite a senha do ZIP para tentar novamente.",
    confirmZipDelete: "Excluir o ZIP original após extrair?\n\n{paths}\n\nEssa ação remove o arquivo do computador.",
    confirmOverwrite: "Substituir arquivos existentes?\n\n{paths}\n\nEssa ação substitui o conteúdo desses arquivos.",
    reviewAndTryAgain: "Revise as informações acima e tente novamente.",
  },
  "en-US": {
    readyTitle: "Ready",
    readyText: "Choose an input file to begin.",
    inspecting: "Reading file...",
    validating: "Validating filter...",
    valid: "Filter is valid.",
    running: "Creating output file...",
    canceling: "Cancelling...",
    cancelled: "Run cancelled.",
    closeBlocked: "A run is still in progress. Cancel it or wait for it to finish before closing.",
    done: "Output file created.",
    error: "Something needs attention.",
    chooseCsv: "Choose an input file.",
    chooseOutput: "Choose where to save the result.",
    noColumns: "Choose a file to load columns.",
    droppedFileNeedsPicker: "Use Browse file so the app can access the full file path.",
    noFile: "No file selected",
    columnsLoaded: "columns loaded.",
    schemaMismatch: "Columns or types differ from the first file.",
    schemaMismatchShort: "Queue differences found.",
    columnSearchPlaceholder: "Search column",
    inputQueue: "Files in queue",
    outputName: "Output name",
    outputNamePlaceholder: "Optional",
    zipPasswords: "ZIP passwords",
    addZipPassword: "Add password",
    clearZipPasswords: "Clear passwords",
    zipPasswordSessionOnly: "Used only for this run. Never saved.",
    zipPasswordsStored: "{count} password(s) kept only for this session.",
    allExcelSheets: "Process all Excel sheets",
    reuseSchema: "Reuse the first file schema",
    deleteZipAfterExtract: "Delete ZIP after successful extraction",
    rowsWritten: "rows written.",
    bridgeNotReady: "The Python bridge is not ready yet.",
    bridgeWaiting: "Waiting for the Python bridge.",
    language: "Language",
    stepFile: "1. File",
    stepFilter: "2. Filter",
    stepOutput: "3. Output",
    stepRun: "4. Create",
    stageOne: "Step 1",
    stageTwo: "Step 2",
    stageThree: "Step 3",
    stageFour: "Step 4",
    stepFileWaiting: "Choose the file",
    stepFileReady: "{count} file(s)",
    stepFileWarning: "Review the queue",
    stepFilterNoRules: "No rules",
    stepFilterReady: "{count} rule(s)",
    stepFilterNeedsFix: "Complete or remove the rule",
    stepFilterAdvanced: "Advanced expression",
    stepFilterVisualWithInactiveAdvanced: "{count} rule(s); advanced inactive",
    stepFilterNoRulesWithInactiveAdvanced: "No rules; advanced inactive",
    stepFilterAdvancedWithInactiveVisual: "Advanced expression; visual inactive",
    stepFilterNoAdvancedWithInactiveVisual: "No expression; visual inactive",
    stepOutputWaiting: "Choose the destination",
    stepOutputReady: "{format} selected",
    stepRunBlocked: "Waiting for steps",
    stepRunReady: "Ready to create",
    stepRunRunning: "Creating",
    stepRunDone: "Done",
    stepRunCancelled: "Cancelled",
    stepRunError: "Needs attention",
    chooseFile: "Choose the file",
    browseInput: "Browse file",
    dropStrong: "Drop the file here",
    dropHelp: "or use the button to browse your computer.",
    fileLabel: "File",
    sizeLabel: "Size",
    columnsLabel: "Columns",
    readOptions: "Read options",
    encoding: "Encoding",
    delimiter: "Delimiter",
    nullValue: "Null value",
    emptyPlaceholder: "empty",
    buildFilter: "Build the filter",
    filterMode: "Filter mode",
    visual: "Visual",
    advanced: "Advanced",
    combineRules: "Combine rules",
    allRules: "all rules",
    anyRule: "any rule",
    addRule: "Add rule",
    noFilterHint: "With no rules, all rows will be exported.",
    advancedFilter: "Advanced filter",
    checkExpression: "Check expression",
    chooseOutputTitle: "Choose the output",
    chooseDestination: "Choose destination",
    summarize: "Generate summary",
    summaryOnly: "Generate only summary",
    summaryGroupBy: "Group by",
    summaryTotals: "Sum columns in summary",
    summaryColumnPlaceholder: "One column per line",
    format: "Format",
    formatCsvTitle: "CSV",
    formatCsvHelp: "Good for sharing and opening in spreadsheets.",
    formatExcelTitle: "Excel",
    formatExcelHelp: "Ready to open in Excel, with splitting when needed.",
    formatParquetTitle: "Parquet",
    formatParquetHelp: "Best for large datasets and analytics tools.",
    splitXlsxNoticeTitle: "Excel may create more than one file",
    splitXlsxNoticeText: "If the output is split, files will be created in the same folder using the pattern {pattern}.",
    saveAs: "Save as",
    chooseSavePlaceholder: "Choose where to save",
    derivedColumnsTitle: "Create new columns",
    derivedColumnsHelp: "Optional: create cleaned columns from filtered columns.",
    addDerivedColumn: "Add column",
    noDerivedColumns: "No new column will be created.",
    loadConfig: "Load configuration",
    configLoaded: "Configuration loaded.",
    saveConfig: "Save configuration",
    configSaved: "Configuration saved.",
    lookupFilesTitle: "CSV lookups",
    lookupFilesHelp: "Optional: use support CSVs in the advanced filter.",
    addLookup: "Add lookup",
    noLookups: "No CSV lookup will be used.",
    removeLookup: "Remove lookup",
    lookupName: "Name",
    lookupNamePlaceholder: "companies",
    lookupPath: "Lookup CSV",
    lookupPathPlaceholder: "Choose a CSV",
    lookupColumn: "Column",
    lookupColumnPlaceholder: "ID",
    chooseLookup: "Choose CSV",
    lookupNameRequired: "Enter a name for this lookup.",
    lookupPathRequired: "Choose this lookup CSV.",
    lookupColumnRequired: "Enter this lookup column.",
    lookupSummary: "Lookup `{name}` using `{column}`.",
    sourceColumn: "Source column",
    derivedOutputName: "New column name",
    derivedOutputNamePlaceholder: "Example: Clean CPF",
    namePrefix: "Prefix",
    nameSuffix: "Suffix",
    nameSeparator: "Separator",
    prefixPlaceholder: "CLEAN",
    suffixPlaceholder: "FORMATTED",
    addTransformation: "Add transformation",
    removeDerivedColumn: "Remove column",
    removeTransformation: "Remove transformation",
    moveTransformationUp: "Move transformation up",
    moveTransformationDown: "Move transformation down",
    derivedPosition: "Position",
    positionAppend: "At the end of the table",
    positionBefore: "Before a column",
    positionAfter: "After a column",
    positionTarget: "Reference column",
    newColumn: "New column",
    derivedSummaryEmpty: "Choose a source column and a transformation.",
    derivedSummary: "Create column `{name}` from `{source}`.",
    derivedSampleValue: "Example",
    derivedSamplePlaceholder: "Example: 123.456.789-01",
    derivedSampleBefore: "Before",
    derivedSampleAfter: "After",
    derivedSourceRequired: "Choose the source column for this new column.",
    derivedPositionTargetRequired: "Choose the reference column for this position.",
    derivedTransformOperationRequired: "Choose the transformation.",
    derivedTransformValueRequired: "Enter the value for this transformation.",
    derivedTransformCountRequired: "Enter a count greater than zero.",
    derivedTransformCaseConflict: "Use only one uppercase/lowercase transformation in this column.",
    advancedOptions: "Advanced options",
    advancedSummaryGroup: "Summary",
    advancedColumnsGroup: "Columns",
    advancedOrganizationGroup: "Organization",
    advancedDiagnosticsGroup: "Diagnostics",
    columnsToSave: "Columns to save",
    oneColumnPerLine: "One column per line",
    renameColumns: "Rename columns",
    renamePlaceholder: "OLD=New name",
    sortBy: "Sort by",
    sortPlaceholder: "COLUMN or COLUMN:desc",
    dedupeKey: "Deduplication key",
    columnPlaceholder: "COLUMN",
    removeDuplicates: "Remove duplicate rows",
    caseInsensitive: "Ignore case in column names",
    jsonReport: "JSON report",
    rejectsCsv: "Rejected rows CSV",
    optional: "Optional",
    chooseReport: "Choose report",
    chooseRejects: "Choose rejected rows",
    generateFile: "Create file",
    generateResult: "Create result",
    previewRows: "Preview rows",
    previewTitle: "Row preview",
    previewing: "Loading preview...",
    previewEmpty: "No rows found for the current setup.",
    previewLoaded: "{count} preview row(s) from {path}",
    previewLoadedQueue: "{count} preview row(s) from the first file ({path}); {total} file(s) in the queue.",
    previewEmptyQueue: "No rows found in the first queued file ({path}).",
    cancelRun: "Cancel",
    openFolder: "Open folder",
    newRun: "New run",
    opEquals: "equals",
    opNotEquals: "does not equal",
    opGt: "greater than",
    opGte: "greater than or equal",
    opLt: "less than",
    opLte: "less than or equal",
    opIn: "is one of these values",
    opNotIn: "is none of these values",
    opBetween: "between",
    opContains: "contains",
    opStartsWith: "starts with",
    opEndsWith: "ends with",
    opIsNull: "is null",
    opIsNotNull: "is not null",
    opIsEmpty: "is empty",
    opIsNotEmpty: "is not empty",
    opIsBlank: "is blank",
    opIsNotBlank: "is not blank",
    value: "Value",
    finalValue: "Final value",
    valueList: "Separate values with commas",
    filterColumnRequired: "Choose a column for this rule.",
    filterValueRequired: "Enter a value for this rule.",
    filterBetweenRequired: "Enter both range values.",
    filterListRequired: "Enter at least one list value.",
    removeRule: "Remove rule",
    txTrim: "Trim spaces",
    txRemoveExtraSpaces: "Remove repeated spaces",
    txUppercase: "Uppercase",
    txLowercase: "Lowercase",
    txTitleCase: "Title Case",
    txReplaceText: "Replace text",
    txAddPrefix: "Add text before",
    txAddSuffix: "Add text after",
    txKeepDigits: "Keep only numbers",
    txKeepLetters: "Keep only letters",
    txRemoveAccents: "Remove accents",
    txRemovePunctuation: "Remove punctuation and symbols",
    txRemoveSpaces: "Remove spaces",
    txPadLeft: "Pad left",
    txPadRight: "Pad right",
    txTakeFirst: "Take first characters",
    txTakeLast: "Take last characters",
    txRemoveFirst: "Remove first characters",
    txRemoveLast: "Remove last characters",
    txExtractBefore: "Extract before separator",
    txExtractAfter: "Extract after separator",
    txDefaultIfBlank: "Use default when empty/null",
    txFormatCpf: "Format CPF",
    txFormatCnpj: "Format CNPJ",
    txFormatPhone: "Format phone",
    transformGroupClean: "Clean text",
    transformGroupChange: "Change text",
    transformGroupExtract: "Extract text",
    transformGroupFormat: "Format identifiers",
    transformValue: "Value",
    transformNewValue: "New value",
    transformCount: "Count",
    transformFill: "Fill",
    transformSeparator: "Separator",
    transformDefault: "Default value",
    filesCreated: "Files created",
    rowsSaved: "Rows saved",
    filesProcessed: "Files processed",
    warnings: "Warnings",
    filesFailed: "Could not process",
    queuePartialDone: "Some files were created, but others need attention.",
    queueAllFailed: "No file was created. Review the items that need attention.",
    technicalDetails: "Technical details",
    likelyCause: "Likely cause",
    nextStep: "Next step",
    zipPasswordNeeded: "This ZIP needs a password.",
    zipPasswordAsk: "Enter the ZIP password to try again.",
    confirmZipDelete: "Delete the original ZIP after extraction?\n\n{paths}\n\nThis removes the file from this computer.",
    confirmOverwrite: "Replace existing files?\n\n{paths}\n\nThis will replace the contents of these files.",
    reviewAndTryAgain: "Review the information above and try again.",
  },
};

function t(key) {
  return (text[state.language] || text["pt-BR"])[key] || key;
}

function byId(id) {
  return document.getElementById(id);
}

function setStatus(title, detail, variant = "idle") {
  byId("statusTitle").textContent = title;
  byId("statusText").textContent = detail;
  byId("statusDot").className = `status-dot ${variant}`;
}

function formatMessage(template, values) {
  return Object.entries(values).reduce((textValue, [key, value]) => textValue.replace(`{${key}}`, String(value)), template);
}

function queueInputCount() {
  return (state.resolvedInputs && state.resolvedInputs.length) || state.inputPaths.length;
}

function stepState(key, stateName, summary) {
  const link = document.querySelector(`[data-step-link="${key}"]`);
  const summaryElement = document.querySelector(`[data-step-summary="${key}"]`);
  if (!link || !summaryElement) {
    return;
  }
  link.dataset.stepState = stateName;
  summaryElement.textContent = summary;
}

function currentFilterStep() {
  const inactiveVisual = inactiveVisualRulesExist();
  const inactiveAdvanced = inactiveAdvancedFilterExists();
  if (state.filterMode === "advanced") {
    return byId("rawFilterInput").value.trim()
      ? {
          state: "ready",
          summary: inactiveVisual ? t("stepFilterAdvancedWithInactiveVisual") : t("stepFilterAdvanced"),
          blocking: false,
        }
      : {
          state: "ready",
          summary: inactiveVisual ? t("stepFilterNoAdvancedWithInactiveVisual") : t("stepFilterNoRules"),
          blocking: false,
        };
  }
  const rows = Array.from(document.querySelectorAll(".filter-row"));
  if (!rows.length) {
    return {
      state: "ready",
      summary: inactiveAdvanced ? t("stepFilterNoRulesWithInactiveAdvanced") : t("stepFilterNoRules"),
      blocking: false,
    };
  }
  const incomplete = rows.some((row) => !visualConditionIsComplete(row));
  if (incomplete) {
    const submitted = rows.some((row) => row.classList.contains("filter-row-invalid"));
    return { state: submitted ? "error" : "warning", summary: t("stepFilterNeedsFix"), blocking: true };
  }
  return {
    state: "ready",
    summary: formatMessage(
      inactiveAdvanced ? t("stepFilterVisualWithInactiveAdvanced") : t("stepFilterReady"),
      { count: rows.length },
    ),
    blocking: false,
  };
}

function inactiveAdvancedFilterExists() {
  return state.filterMode === "visual" && Boolean(byId("rawFilterInput").value.trim());
}

function inactiveVisualRulesExist() {
  return (
    state.filterMode === "advanced" &&
    Array.from(document.querySelectorAll(".filter-row")).some(visualConditionIsComplete)
  );
}

function currentFileStep() {
  const count = queueInputCount();
  if (!count) {
    return { state: "pending", summary: t("stepFileWaiting"), blocking: true };
  }
  const hasSchemaWarning = (state.resolvedInputs || []).some((item) => item.schema_matches_first === false);
  return {
    state: hasSchemaWarning ? "warning" : "ready",
    summary: hasSchemaWarning ? t("stepFileWarning") : formatMessage(t("stepFileReady"), { count }),
    blocking: false,
  };
}

function currentOutputStep() {
  const outputPath = byId("outputPathInput").value.trim();
  if (!outputPath) {
    return { state: "pending", summary: t("stepOutputWaiting"), blocking: true };
  }
  return {
    state: "ready",
    summary: formatMessage(t("stepOutputReady"), { format: byId("formatSelect").value.toUpperCase() }),
    blocking: false,
  };
}

function currentRunStep(fileStep, filterStep, outputStep) {
  if (state.activeJobId || state.runStepState === "running") {
    return { state: "running", summary: state.runStepSummary || t("stepRunRunning") };
  }
  if (state.runStepState === "done") {
    return { state: "done", summary: state.runStepSummary || t("stepRunDone") };
  }
  if (state.runStepState === "cancelled") {
    return { state: "done", summary: t("stepRunCancelled") };
  }
  if (state.runStepState === "error") {
    return { state: "error", summary: state.runStepSummary || t("stepRunError") };
  }
  if (fileStep.blocking || filterStep.blocking || outputStep.blocking) {
    return { state: "pending", summary: t("stepRunBlocked") };
  }
  return { state: "ready", summary: t("stepRunReady") };
}

function updateWorkflowSteps() {
  const fileStep = currentFileStep();
  const filterStep = currentFilterStep();
  const outputStep = currentOutputStep();
  const runStep = currentRunStep(fileStep, filterStep, outputStep);
  stepState("file", fileStep.state, fileStep.summary);
  stepState("filter", filterStep.state, filterStep.summary);
  stepState("output", outputStep.state, outputStep.summary);
  stepState("run", runStep.state, runStep.summary);
}

function markSetupChanged() {
  if (!state.activeJobId) {
    state.runStepState = "pending";
    state.runStepSummary = "";
  }
  resetPreview();
  updateWorkflowSteps();
}

function setRunStep(stateName, summary = "") {
  state.runStepState = stateName;
  state.runStepSummary = summary;
  updateWorkflowSteps();
}

function showDetails(value) {
  const detailsWrapper = byId("technicalDetails");
  const details = byId("detailsBox");
  if (!value) {
    detailsWrapper.classList.add("hidden");
    details.textContent = "";
    return;
  }
  details.textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  detailsWrapper.classList.remove("hidden");
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function showFriendlyError(error) {
  const box = byId("friendlyErrorBox");
  if (!error) {
    box.classList.add("hidden");
    box.innerHTML = "";
    return;
  }
  const message = error.message || t("error");
  const isZipPassword = error.type === "ZipPasswordRequiredError" || String(message).toLowerCase().includes("zip");
  const cause = isZipPassword ? t("zipPasswordNeeded") : message;
  const next = isZipPassword ? t("zipPasswordAsk") : t("reviewAndTryAgain");
  box.innerHTML = `
    <strong>${escapeHtml(message)}</strong>
    <p><b>${t("likelyCause")}:</b> ${escapeHtml(cause)}</p>
    <p><b>${t("nextStep")}:</b> ${escapeHtml(next)}</p>
  `;
  box.classList.remove("hidden");
}

function handleResponse(response) {
  if (response && response.ok) {
    return response.data;
  }
  const error = response && response.error ? response.error : { message: t("error") };
  setStatus(t("error"), error.message, "error");
  showFriendlyError(error);
  showDetails(error.details || error);
  const thrown = new Error(error.message);
  Object.assign(thrown, error);
  throw thrown;
}

function bridgeUnavailableResponse() {
  return Promise.resolve({
    ok: false,
    error: {
      message: t("bridgeNotReady"),
      details: t("bridgeWaiting"),
    },
  });
}

function createBrowserFallbackApi() {
  return {
    get_app_info: () =>
      Promise.resolve({
        ok: true,
        data: {
          version: "",
          language: state.language,
          output_formats: ["csv", "xlsx", "parquet"],
        },
      }),
    set_language: (language) => {
      state.language = language;
      return Promise.resolve({ ok: true, data: { language } });
    },
    choose_input_files: bridgeUnavailableResponse,
    choose_config_file: bridgeUnavailableResponse,
    choose_lookup_file: bridgeUnavailableResponse,
    choose_output_file: bridgeUnavailableResponse,
    choose_report_file: bridgeUnavailableResponse,
    choose_rejects_file: bridgeUnavailableResponse,
    load_config: bridgeUnavailableResponse,
    save_config: bridgeUnavailableResponse,
    inspect_csv: bridgeUnavailableResponse,
    validate_filter: bridgeUnavailableResponse,
    preview_rows: bridgeUnavailableResponse,
    start_filter_run: bridgeUnavailableResponse,
    cancel_job: bridgeUnavailableResponse,
    get_job_status: bridgeUnavailableResponse,
    open_output_folder: bridgeUnavailableResponse,
  };
}

function linesFromTextarea(id) {
  return byId(id)
    .value.split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function setInputPath(path) {
  setInputPaths(path ? [path] : []);
}

function setInputPaths(paths) {
  state.inputPaths = (paths || []).filter(Boolean);
  state.inputPath = state.inputPaths[0] || "";
  state.outputNames = [];
  state.resolvedInputs = [];
  state.columnTypes = {};
  clearZipPasswords();
  byId("inputPathText").textContent = state.inputPath || t("noFile");
  renderQueue();
  showInputWarnings([]);
  updateInputOptionVisibility();
  markSetupChanged();
}

function setOutputPath(path) {
  state.outputPath = path || "";
  byId("outputPathInput").value = state.outputPath;
  updateOutputArtifactNotice();
  markSetupChanged();
}

function applyLanguage() {
  document.documentElement.lang = state.language;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.setAttribute("placeholder", t(element.dataset.i18nPlaceholder));
  });
  document.querySelectorAll("[data-i18n-title]").forEach((element) => {
    element.setAttribute("title", t(element.dataset.i18nTitle));
  });
  document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
    element.setAttribute("aria-label", t(element.dataset.i18nAriaLabel));
  });
  document.querySelectorAll("[data-i18n-label]").forEach((element) => {
    element.setAttribute("label", t(element.dataset.i18nLabel));
  });
  if (!state.inputPath) {
    byId("inputPathText").textContent = t("noFile");
  }
  document.querySelectorAll(".filter-column").forEach((input) => updateColumnOptions(input));
  document.querySelectorAll(".lookup-card").forEach(updateLookupCard);
  document.querySelectorAll(".derived-transform-row").forEach(updateTransformRow);
  document.querySelectorAll(".derived-column-card").forEach(updateDerivedCard);
  updateFilterHint();
  updateSummaryMode();
  updateDerivedEmptyState();
  updateInputOptionVisibility();
  updateOutputArtifactNotice();
  updateWorkflowSteps();
}

function updateFilterHint() {
  const hasActiveRules = Array.from(document.querySelectorAll(".filter-row")).some(visualConditionIsComplete);
  byId("noFilterHint").classList.toggle("hidden", hasActiveRules);
  updateWorkflowSteps();
}

function updateSummaryMode() {
  const summarizeInput = byId("summarizeInput");
  if (!summarizeInput) {
    return;
  }
  const summarize = summarizeInput.checked;
  const summaryOnlyInput = byId("summaryOnlyInput");
  const summaryFields = byId("summaryFields");
  if (!summarize) {
    summaryOnlyInput.checked = false;
    summaryFields.classList.add("hidden");
  } else {
    summaryFields.classList.remove("hidden");
  }
  summaryOnlyInput.disabled = !summarize;
  Array.from(summaryFields.querySelectorAll("input, textarea")).forEach((field) => {
    field.disabled = !summarize;
  });
  updateWorkflowSteps();
}

function setColumns(columns, types = {}) {
  state.columns = columns || [];
  state.columnTypes = types || {};
  byId("columnCountText").textContent = state.columns.length ? String(state.columns.length) : "-";
  document.querySelectorAll(".filter-column").forEach((input) => updateColumnOptions(input));
  document.querySelectorAll(".filter-row").forEach(updateFilterRow);
  updateWorkflowSteps();
}

function renderQueue(inputs = state.resolvedInputs) {
  const panel = byId("queuePanel");
  const list = byId("queueList");
  const items = inputs && inputs.length ? inputs : state.inputPaths.map((path) => ({ label: path, format: "" }));
  list.innerHTML = "";
  if (!items.length) {
    panel.classList.add("hidden");
    updateInputOptionVisibility();
    updateWorkflowSteps();
    return;
  }
  items.forEach((item, index) => {
    const row = document.createElement("div");
    row.className = "queue-item";
    const label = item.label || item.display_name || item.source_path || item.path;
    const columnCount = Number.isInteger(item.column_count) ? `${item.column_count} ${t("columnsLabel")}` : "";
    const meta = [item.format, columnCount, item.excel_sheet ? `aba: ${item.excel_sheet}` : "", item.zip_source ? "ZIP" : ""]
      .filter(Boolean)
      .join(" · ");
    const title = document.createElement("strong");
    title.textContent = `${index + 1}. ${label}`;
    const metaText = document.createElement("span");
    metaText.textContent = meta;
    const outputLabel = document.createElement("label");
    outputLabel.className = "queue-output-name";
    const outputLabelText = document.createElement("span");
    outputLabelText.textContent = t("outputName");
    const outputInput = document.createElement("input");
    outputInput.type = "text";
    outputInput.value = state.outputNames[index] || item.output_name || "";
    outputInput.placeholder = t("outputNamePlaceholder");
    outputInput.addEventListener("input", () => {
      state.outputNames[index] = outputInput.value;
    });
    outputLabel.append(outputLabelText, outputInput);
    row.append(title, metaText);
    if (item.schema_matches_first === false) {
      const schemaWarning = document.createElement("span");
      schemaWarning.className = "queue-schema-warning";
      schemaWarning.textContent = t("schemaMismatch");
      row.appendChild(schemaWarning);
    }
    row.appendChild(outputLabel);
    list.appendChild(row);
  });
  panel.classList.remove("hidden");
  updateInputOptionVisibility();
  updateWorkflowSteps();
}

function inferredInputFormat(path) {
  const lower = String(path || "").toLowerCase();
  if (lower.endsWith(".csv")) {
    return "csv";
  }
  if (lower.endsWith(".xlsx")) {
    return "xlsx";
  }
  if (lower.endsWith(".parquet") || lower.endsWith(".pq")) {
    return "parquet";
  }
  if (lower.endsWith(".zip")) {
    return "zip";
  }
  return "";
}

function inputDescriptors() {
  if (state.resolvedInputs && state.resolvedInputs.length) {
    return state.resolvedInputs;
  }
  return state.inputPaths.map((path) => ({
    path,
    source_path: path,
    format: inferredInputFormat(path),
    zip_source: inferredInputFormat(path) === "zip" ? path : "",
  }));
}

function currentInputKinds() {
  const descriptors = inputDescriptors();
  const kinds = new Set();
  descriptors.forEach((item) => {
    const path = item.source_path || item.path || item.label || "";
    const format = String(item.format || inferredInputFormat(path)).toLowerCase();
    if (format === "csv") {
      kinds.add("csv");
    } else if (format === "xlsx" || format === "excel") {
      kinds.add("excel");
    } else if (format === "parquet" || format === "pq") {
      kinds.add("parquet");
    } else if (format === "zip") {
      kinds.add("zip");
      kinds.add("csv");
      kinds.add("excel");
    }
    if (item.zip_source) {
      kinds.add("zip");
    }
  });
  if (descriptors.length > 1) {
    kinds.add("queue");
  }
  return kinds;
}

function inputOptionGroupVisible(groupName, kinds) {
  if (groupName === "csv") {
    return kinds.has("csv");
  }
  if (groupName === "excel") {
    return kinds.has("excel");
  }
  if (groupName === "zip") {
    return kinds.has("zip");
  }
  if (groupName === "queue") {
    return kinds.has("queue");
  }
  return true;
}

function updateInputOptionVisibility() {
  const kinds = currentInputKinds();
  const hasInput = Boolean(inputDescriptors().length);
  byId("readOptionsDetails").classList.toggle("hidden", !hasInput);
  document.querySelectorAll("[data-input-option-group]").forEach((group) => {
    const visible = hasInput && inputOptionGroupVisible(group.dataset.inputOptionGroup, kinds);
    group.classList.toggle("hidden", !visible);
    group.querySelectorAll("button, input, textarea, select").forEach((control) => {
      control.disabled = !visible;
    });
  });
  updateZipPasswordStatus();
}

function showInputWarnings(warnings = []) {
  const panel = byId("inputWarningsPanel");
  const list = byId("inputWarningsList");
  list.innerHTML = "";
  if (!warnings.length) {
    panel.classList.add("hidden");
    return;
  }
  warnings.forEach((warning) => {
    const item = document.createElement("li");
    item.textContent = warning;
    list.appendChild(item);
  });
  panel.classList.remove("hidden");
}

function prepareColumnSearch(input) {
  const suggestions = input.parentElement.querySelector(".filter-column-suggestions");
  if (!suggestions.id) {
    state.columnSuggestionListId += 1;
    suggestions.id = `filterColumnSuggestions${state.columnSuggestionListId}`;
    input.setAttribute("aria-controls", suggestions.id);
  }
}

function updateColumnOptions(input) {
  prepareColumnSearch(input);
  const suggestions = input.parentElement.querySelector(".filter-column-suggestions");
  const current = input.value;
  suggestions.innerHTML = "";
  input.dataset.activeIndex = "-1";
  input.removeAttribute("aria-activedescendant");
  if (!state.columns.length) {
    input.disabled = true;
    input.placeholder = t("noColumns");
    closeColumnSuggestions(input);
    return;
  }

  input.disabled = false;
  input.placeholder = t("columnSearchPlaceholder");
  rankedColumns(current).forEach((column) => {
    const option = document.createElement("button");
    option.type = "button";
    option.className = "column-suggestion";
    option.setAttribute("role", "option");
    option.textContent = column;
    option.title = column;
    option.dataset.value = column;
    option.tabIndex = -1;
    option.addEventListener("mousedown", (event) => event.preventDefault());
    option.addEventListener("click", () => chooseColumnSuggestion(input, column));
    suggestions.appendChild(option);
  });
  suggestions.classList.toggle("hidden", document.activeElement !== input || !suggestions.children.length);
  input.setAttribute("aria-expanded", suggestions.classList.contains("hidden") ? "false" : "true");
}

function closeColumnSuggestions(input) {
  const suggestions = input.parentElement.querySelector(".filter-column-suggestions");
  suggestions.classList.add("hidden");
  suggestions.querySelectorAll(".column-suggestion").forEach((option) => option.classList.remove("active"));
  input.setAttribute("aria-expanded", "false");
  input.dataset.activeIndex = "-1";
  input.removeAttribute("aria-activedescendant");
}

function chooseColumnSuggestion(input, column) {
  input.value = column;
  closeColumnSuggestions(input);
  updateFilterHint();
  input.dispatchEvent(new Event("change", { bubbles: true }));
}

function setActiveColumnSuggestion(input, nextIndex) {
  const suggestions = input.parentElement.querySelector(".filter-column-suggestions");
  const options = Array.from(suggestions.querySelectorAll(".column-suggestion"));
  if (!options.length) {
    return;
  }
  const index = Math.max(0, Math.min(nextIndex, options.length - 1));
  options.forEach((option) => option.classList.remove("active"));
  const active = options[index];
  active.classList.add("active");
  active.setAttribute("id", active.id || `${suggestions.id}Option${index}`);
  input.dataset.activeIndex = String(index);
  input.setAttribute("aria-activedescendant", active.id);
  active.scrollIntoView({ block: "nearest" });
}

function moveColumnSuggestion(input, direction) {
  const suggestions = input.parentElement.querySelector(".filter-column-suggestions");
  if (suggestions.classList.contains("hidden") || !suggestions.children.length) {
    updateColumnOptions(input);
  }
  const options = suggestions.querySelectorAll(".column-suggestion");
  if (!options.length) {
    return;
  }
  const currentIndex = Number(input.dataset.activeIndex || "-1");
  const nextIndex = currentIndex < 0 ? (direction > 0 ? 0 : options.length - 1) : (currentIndex + direction + options.length) % options.length;
  setActiveColumnSuggestion(input, nextIndex);
}

function chooseActiveColumnSuggestion(input) {
  const suggestions = input.parentElement.querySelector(".filter-column-suggestions");
  const options = Array.from(suggestions.querySelectorAll(".column-suggestion"));
  const activeIndex = Number(input.dataset.activeIndex || "-1");
  if (activeIndex < 0 || activeIndex >= options.length) {
    return false;
  }
  chooseColumnSuggestion(input, options[activeIndex].dataset.value);
  return true;
}

function chooseFirstColumnSuggestion(input) {
  const suggestions = input.parentElement.querySelector(".filter-column-suggestions");
  const firstOption = suggestions.querySelector(".column-suggestion");
  if (!firstOption) {
    closeColumnSuggestions(input);
    return false;
  }
  chooseColumnSuggestion(input, firstOption.dataset.value);
  return true;
}

function normalizeForSearch(value) {
  return String(value)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function columnSearchParts(value) {
  const normalized = normalizeForSearch(value).trim();
  const tokens = normalized.split(/[^a-z0-9]+/).filter(Boolean);
  return {
    normalized,
    compact: tokens.join(""),
    initials: tokens.map((token) => token[0]).join(""),
    tokens,
  };
}

function everyQueryTokenMatches(candidateTokens, queryTokens, matcher) {
  return queryTokens.length > 0 && queryTokens.every((queryToken) => candidateTokens.some((candidateToken) => matcher(candidateToken, queryToken)));
}

function fuzzyScore(candidate, query) {
  const candidateParts = columnSearchParts(candidate);
  const queryParts = columnSearchParts(query);
  if (!queryParts.compact) {
    return 0;
  }
  if (candidateParts.normalized === queryParts.normalized || candidateParts.compact === queryParts.compact) {
    return 100000;
  }
  if (candidateParts.normalized.startsWith(queryParts.normalized) || candidateParts.compact.startsWith(queryParts.compact)) {
    return 90000 - candidateParts.compact.length;
  }
  if (candidateParts.tokens.some((token) => token === queryParts.compact)) {
    return 85000 - candidateParts.compact.length;
  }
  if (everyQueryTokenMatches(candidateParts.tokens, queryParts.tokens, (candidateToken, queryToken) => candidateToken.startsWith(queryToken))) {
    return 82000 - candidateParts.compact.length;
  }
  if (candidateParts.initials.startsWith(queryParts.compact)) {
    return 78000 - candidateParts.compact.length;
  }
  if (candidateParts.normalized.includes(queryParts.normalized)) {
    return 72000 - candidateParts.normalized.indexOf(queryParts.normalized) * 20 - candidateParts.compact.length;
  }
  const containsIndex = candidateParts.compact.indexOf(queryParts.compact);
  if (containsIndex >= 0) {
    return 68000 - containsIndex * 20 - candidateParts.compact.length;
  }
  if (everyQueryTokenMatches(candidateParts.tokens, queryParts.tokens, (candidateToken, queryToken) => candidateToken.includes(queryToken))) {
    return 62000 - candidateParts.compact.length;
  }

  return Number.NEGATIVE_INFINITY;
}

function rankedColumns(query) {
  return state.columns
    .map((column, index) => ({ column, index, score: fuzzyScore(column, query) }))
    .filter((item) => item.score > Number.NEGATIVE_INFINITY)
    .sort((left, right) => right.score - left.score || left.index - right.index)
    .slice(0, 50)
    .map((item) => item.column);
}

const FILTER_OPERATORS_BY_TYPE = {
  text: [
    "equals",
    "not_equals",
    "in",
    "not_in",
    "contains",
    "starts_with",
    "ends_with",
    "is_null",
    "is_not_null",
    "is_empty",
    "is_not_empty",
    "is_blank",
    "is_not_blank",
  ],
  numeric: ["equals", "not_equals", "gt", "gte", "lt", "lte", "in", "not_in", "between", "is_null", "is_not_null"],
  date: ["equals", "not_equals", "gt", "gte", "lt", "lte", "between", "is_null", "is_not_null"],
  datetime: ["equals", "not_equals", "gt", "gte", "lt", "lte", "between", "is_null", "is_not_null"],
  boolean: ["equals", "not_equals", "is_null", "is_not_null"],
};

function semanticColumnType(column) {
  const rawType = String(state.columnTypes[column] || "").toUpperCase();
  if (/BOOL/.test(rawType)) {
    return "boolean";
  }
  if (/DATE/.test(rawType) && !/TIME|TIMESTAMP/.test(rawType)) {
    return "date";
  }
  if (/TIMESTAMP|DATETIME|TIME/.test(rawType)) {
    return "datetime";
  }
  if (/INT|DECIMAL|NUMERIC|DOUBLE|FLOAT|REAL|HUGEINT|UBIGINT|UINTEGER|USMALLINT|UTINYINT/.test(rawType)) {
    return "numeric";
  }
  return "text";
}

function allowedOperatorsForColumn(column) {
  return FILTER_OPERATORS_BY_TYPE[semanticColumnType(column)] || FILTER_OPERATORS_BY_TYPE.text;
}

function refreshFilterOperatorOptions(row) {
  const column = row.querySelector(".filter-column").value.trim();
  const operator = row.querySelector(".filter-operator");
  const allowed = allowedOperatorsForColumn(column);
  Array.from(operator.options).forEach((option) => {
    option.hidden = !allowed.includes(option.value);
  });
  if (!allowed.includes(operator.value)) {
    operator.value = allowed[0];
  }
}

function updateFilterValueInputTypes(row) {
  const column = row.querySelector(".filter-column").value.trim();
  const semanticType = semanticColumnType(column);
  const operator = row.querySelector(".filter-operator").value;
  const inputs = [row.querySelector(".filter-value"), row.querySelector(".filter-value2")];
  inputs.forEach((input) => {
    input.type = "text";
    input.inputMode = "";
    input.removeAttribute("step");
  });
  if (semanticType === "numeric" && !["in", "not_in"].includes(operator)) {
    inputs.forEach((input) => {
      input.inputMode = "decimal";
    });
  } else if (semanticType === "date") {
    inputs.forEach((input) => {
      input.type = "date";
    });
  } else if (semanticType === "datetime") {
    inputs.forEach((input) => {
      input.type = "datetime-local";
      input.step = "1";
    });
  } else if (semanticType === "boolean") {
    inputs.forEach((input) => {
      input.placeholder = "true / false";
    });
  }
}

function updateFilterRow(row) {
  refreshFilterOperatorOptions(row);
  const operator = row.querySelector(".filter-operator").value;
  const value = row.querySelector(".filter-value");
  const value2 = row.querySelector(".filter-value2");
  const noValue = ["is_null", "is_not_null", "is_empty", "is_not_empty", "is_blank", "is_not_blank"].includes(operator);
  const between = operator === "between";
  row.classList.toggle("no-value", noValue);
  row.classList.toggle("is-between", between && !noValue);
  value.classList.toggle("hidden", noValue);
  value2.classList.toggle("hidden", !between || noValue);
  value.placeholder = operator === "in" || operator === "not_in" ? t("valueList") : t("value");
  updateFilterValueInputTypes(row);
}

function clearFilterRowValidation(row) {
  row.classList.remove("filter-row-invalid");
  row.querySelectorAll("[aria-invalid='true']").forEach((field) => field.removeAttribute("aria-invalid"));
  const message = row.querySelector(".filter-inline-error");
  if (message) {
    message.remove();
  }
}

function markFilterRowInvalid(row, field, message) {
  row.classList.add("filter-row-invalid");
  field.setAttribute("aria-invalid", "true");
  let error = row.querySelector(".filter-inline-error");
  if (!error) {
    error = document.createElement("div");
    error.className = "filter-inline-error";
    row.appendChild(error);
  }
  error.textContent = message;
  field.focus();
  field.scrollIntoView({ block: "center", inline: "nearest" });
  setStatus(t("error"), message, "error");
  showFriendlyError({ message, details: message });
  updateWorkflowSteps();
}

function validateVisualRowsBeforeSubmit() {
  if (state.filterMode !== "visual") {
    return true;
  }
  const rows = Array.from(document.querySelectorAll(".filter-row"));
  rows.forEach(clearFilterRowValidation);
  for (const row of rows) {
    const column = row.querySelector(".filter-column");
    const operator = row.querySelector(".filter-operator").value;
    const value = row.querySelector(".filter-value");
    const value2 = row.querySelector(".filter-value2");
    if (!column.value.trim()) {
      markFilterRowInvalid(row, column, t("filterColumnRequired"));
      return false;
    }
    if (["is_null", "is_not_null", "is_empty", "is_not_empty", "is_blank", "is_not_blank"].includes(operator)) {
      continue;
    }
    if (operator === "between" && (!value.value.trim() || !value2.value.trim())) {
      markFilterRowInvalid(row, !value.value.trim() ? value : value2, t("filterBetweenRequired"));
      return false;
    }
    if ((operator === "in" || operator === "not_in") && !value.value.split(",").some((item) => item.trim())) {
      markFilterRowInvalid(row, value, t("filterListRequired"));
      return false;
    }
    if (!value.value.trim()) {
      markFilterRowInvalid(row, value, t("filterValueRequired"));
      return false;
    }
  }
  updateWorkflowSteps();
  return true;
}

function visualConditionIsComplete(row) {
  const condition = {
    column: row.querySelector(".filter-column").value.trim(),
    operator: row.querySelector(".filter-operator").value,
    value: row.querySelector(".filter-value").value.trim(),
    value2: row.querySelector(".filter-value2").value.trim(),
  };
  return conditionIsComplete(condition);
}

function conditionIsComplete(condition) {
  if (!condition.column) {
    return false;
  }
  if (["is_null", "is_not_null", "is_empty", "is_not_empty", "is_blank", "is_not_blank"].includes(condition.operator)) {
    return true;
  }
  if (condition.operator === "between") {
    return Boolean(condition.value && condition.value2);
  }
  return Boolean(condition.value);
}

function inferredTypeForCondition(operator, value, column) {
  const semanticType = semanticColumnType(column);
  if (semanticType === "numeric") {
    return "number";
  }
  if (semanticType === "date") {
    return "date";
  }
  if (semanticType === "datetime") {
    return "datetime";
  }
  if (semanticType === "boolean") {
    return "boolean";
  }
  if (["gt", "gte", "lt", "lte"].includes(operator)) {
    const text = String(value || "").trim();
    if (/^\d{4}-\d{2}-\d{2}(?:[T ][0-2]\d:[0-5]\d(?::[0-5]\d(?:\.\d+)?)?)?$/.test(text)) {
      return "auto";
    }
    return "number";
  }
  if (operator === "between") {
    return "auto";
  }
  return "string";
}

function addFilterRow(initial = {}) {
  const template = byId("filterRowTemplate");
  const row = template.content.firstElementChild.cloneNode(true);
  const column = row.querySelector(".filter-column");
  const operator = row.querySelector(".filter-operator");
  const value = row.querySelector(".filter-value");
  const value2 = row.querySelector(".filter-value2");

  prepareColumnSearch(column);
  if (initial.column) column.value = initial.column;
  updateColumnOptions(column);
  if (initial.operator) operator.value = initial.operator;
  if (initial.value) value.value = initial.value;
  if (initial.value2) value2.value = initial.value2;

  column.addEventListener("focus", () => updateColumnOptions(column));
  column.addEventListener("input", () => {
    clearFilterRowValidation(row);
    updateColumnOptions(column);
    updateFilterHint();
  });
  column.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      moveColumnSuggestion(column, 1);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      moveColumnSuggestion(column, -1);
    } else if (event.key === "Enter") {
      event.preventDefault();
      chooseActiveColumnSuggestion(column) || chooseFirstColumnSuggestion(column);
    } else if (event.key === "Tab") {
      event.preventDefault();
      moveColumnSuggestion(column, event.shiftKey ? -1 : 1);
    } else if (event.key === "Escape") {
      closeColumnSuggestions(column);
    }
  });
  column.addEventListener("blur", () => {
    setTimeout(() => closeColumnSuggestions(column), 120);
  });
  column.addEventListener("change", () => {
    clearFilterRowValidation(row);
    updateFilterRow(row);
    updateFilterHint();
  });
  operator.addEventListener("change", () => {
    clearFilterRowValidation(row);
    updateFilterRow(row);
    updateFilterHint();
  });
  value.addEventListener("input", () => {
    clearFilterRowValidation(row);
    updateFilterHint();
  });
  value2.addEventListener("input", () => {
    clearFilterRowValidation(row);
    updateFilterHint();
  });
  row.querySelector(".remove-filter").addEventListener("click", () => {
    row.remove();
    updateFilterHint();
    markSetupChanged();
  });
  byId("filterRows").appendChild(row);
  applyLanguage();
  updateFilterRow(row);
  updateFilterHint();
  markSetupChanged();
}

function visualConditions() {
  return Array.from(document.querySelectorAll(".filter-row")).map((row) => ({
    column: row.querySelector(".filter-column").value,
    operator: row.querySelector(".filter-operator").value,
    value: row.querySelector(".filter-value").value,
    value2: row.querySelector(".filter-value2").value,
    value_type: inferredTypeForCondition(
      row.querySelector(".filter-operator").value,
      row.querySelector(".filter-value").value,
      row.querySelector(".filter-column").value,
    ),
  }));
}

function addLookup(initial = {}) {
  const template = byId("lookupTemplate");
  const card = template.content.firstElementChild.cloneNode(true);
  state.lookupId += 1;
  card.dataset.lookupId = String(state.lookupId);
  card.querySelector(".lookup-name").value = initial.name || "";
  card.querySelector(".lookup-path").value = initial.path || "";
  card.querySelector(".lookup-column").value = initial.column || "";
  card.querySelectorAll("input").forEach((input) => {
    input.addEventListener("input", () => {
      clearLookupValidation(card);
      updateLookupCard(card);
      markSetupChanged();
    });
  });
  card.querySelector(".browse-lookup-file").addEventListener("click", async () => {
    const data = handleResponse(await state.api.choose_lookup_file());
    if (data.path) {
      card.querySelector(".lookup-path").value = data.path;
      clearLookupValidation(card);
      updateLookupCard(card);
      markSetupChanged();
    }
  });
  card.querySelector(".remove-lookup").addEventListener("click", () => {
    card.remove();
    updateLookupEmptyState();
    markSetupChanged();
  });
  byId("lookupList").appendChild(card);
  applyLanguage();
  updateLookupCard(card);
  updateLookupEmptyState();
  markSetupChanged();
}

function updateLookupCard(card) {
  const name = card.querySelector(".lookup-name").value.trim();
  const column = card.querySelector(".lookup-column").value.trim();
  card.querySelector(".lookup-preview").textContent =
    name && column ? t("lookupSummary").replace("{name}", name).replace("{column}", column) : t("lookupFilesTitle");
}

function updateLookupEmptyState() {
  byId("noLookupsText").classList.toggle("hidden", Boolean(document.querySelectorAll(".lookup-card").length));
}

function lookupPayload(card) {
  return {
    name: card.querySelector(".lookup-name").value.trim(),
    path: card.querySelector(".lookup-path").value.trim(),
    column: card.querySelector(".lookup-column").value.trim(),
  };
}

function visualLookups() {
  return Array.from(document.querySelectorAll(".lookup-card")).map(lookupPayload);
}

function clearLookupValidation(card) {
  card.classList.remove("lookup-card-invalid");
  card.querySelectorAll("[aria-invalid='true']").forEach((field) => field.removeAttribute("aria-invalid"));
  const message = card.querySelector(".lookup-inline-error");
  if (message) {
    message.remove();
  }
}

function markLookupInvalid(card, field, message) {
  card.classList.add("lookup-card-invalid");
  field.setAttribute("aria-invalid", "true");
  let error = card.querySelector(".lookup-inline-error");
  if (!error) {
    error = document.createElement("div");
    error.className = "lookup-inline-error";
    card.appendChild(error);
  }
  error.textContent = message;
  field.focus();
  field.scrollIntoView({ block: "center", inline: "nearest" });
  setStatus(t("error"), message, "error");
  showFriendlyError({ message, details: message });
}

function validateLookupRowsBeforeSubmit() {
  const cards = Array.from(document.querySelectorAll(".lookup-card"));
  cards.forEach(clearLookupValidation);
  for (const card of cards) {
    const name = card.querySelector(".lookup-name");
    const path = card.querySelector(".lookup-path");
    const column = card.querySelector(".lookup-column");
    if (!name.value.trim()) {
      markLookupInvalid(card, name, t("lookupNameRequired"));
      return false;
    }
    if (!path.value.trim()) {
      markLookupInvalid(card, path, t("lookupPathRequired"));
      return false;
    }
    if (!column.value.trim()) {
      markLookupInvalid(card, column, t("lookupColumnRequired"));
      return false;
    }
  }
  return true;
}

function formatDerivedName(source, outputName, prefix, suffix, separator) {
  if (outputName) {
    return outputName;
  }
  if (!source) {
    return t("newColumn");
  }
  const before = prefix ? `${prefix}${separator && !prefix.endsWith(separator) ? separator : ""}` : "";
  const after = suffix ? `${separator && !suffix.startsWith(separator) ? separator : ""}${suffix}` : "";
  return `${before}${source}${after}`;
}

function derivedNameParts(initial = {}) {
  const parts = {
    output: initial.output_name || initial.output || "",
    prefix: "",
    suffix: "",
    separator: "_",
  };
  const rawName = initial.name;
  if (typeof rawName === "string") {
    parts.output = rawName;
  } else if (rawName && typeof rawName === "object") {
    parts.output = rawName.output || rawName.value || parts.output;
    parts.prefix = rawName.prefix || "";
    parts.suffix = rawName.suffix || "";
    parts.separator = rawName.separator ?? "_";
  }
  return parts;
}

function visualDerivedColumns() {
  return Array.from(document.querySelectorAll(".derived-column-card")).map((card) => {
    const source = card.querySelector(".derived-source-column").value.trim();
    const outputName = card.querySelector(".derived-output-name").value.trim();
    const prefix = card.querySelector(".derived-prefix").value.trim();
    const suffix = card.querySelector(".derived-suffix").value.trim();
    const separator = card.querySelector(".derived-separator").value;
    const mode = card.querySelector(".derived-position-mode").value;
    const target = card.querySelector(".derived-position-target").value.trim();
    const transforms = Array.from(card.querySelectorAll(".derived-transform-row")).map(transformPayload);
    return {
      source,
      name: { value: outputName, prefix, suffix, separator },
      position: { mode, target },
      transforms,
    };
  });
}

function transformPayload(row) {
  const operation = row.querySelector(".derived-transform-operation").value;
  const value = row.querySelector(".derived-transform-value").value;
  const extra = row.querySelector(".derived-transform-extra").value;
  if (operation === "replace_text") {
    return { operation, old: value, new: extra };
  }
  if (["pad_left", "pad_right"].includes(operation)) {
    return { operation, count: value, fill: extra || " " };
  }
  if (["take_first", "take_last", "remove_first", "remove_last"].includes(operation)) {
    return { operation, count: value };
  }
  if (["add_prefix", "add_suffix", "extract_before", "extract_after", "default_if_blank"].includes(operation)) {
    return { operation, text: value };
  }
  return { operation };
}

function clearDerivedValidation(card) {
  card.classList.remove("derived-column-card-invalid");
  card.querySelectorAll("[aria-invalid='true']").forEach((field) => field.removeAttribute("aria-invalid"));
  const message = card.querySelector(".derived-inline-error");
  if (message) {
    message.remove();
  }
}

function markDerivedInvalid(card, field, message) {
  card.classList.add("derived-column-card-invalid");
  field.setAttribute("aria-invalid", "true");
  const details = field.closest("details");
  if (details) {
    details.open = true;
  }
  let error = card.querySelector(".derived-inline-error");
  if (!error) {
    error = document.createElement("div");
    error.className = "derived-inline-error";
    card.appendChild(error);
  }
  error.textContent = message;
  field.focus();
  field.scrollIntoView({ block: "center", inline: "nearest" });
  setStatus(t("error"), message, "error");
  showFriendlyError({ message, details: message });
}

function derivedTextParamRequired(operation) {
  return ["add_prefix", "add_suffix", "extract_before", "extract_after", "default_if_blank"].includes(operation);
}

function derivedCountParamRequired(operation) {
  return ["pad_left", "pad_right", "take_first", "take_last", "remove_first", "remove_last"].includes(operation);
}

function validateDerivedRowsBeforeSubmit() {
  const cards = Array.from(document.querySelectorAll(".derived-column-card"));
  cards.forEach(clearDerivedValidation);
  for (const card of cards) {
    const source = card.querySelector(".derived-source-column");
    if (!source.value.trim()) {
      markDerivedInvalid(card, source, t("derivedSourceRequired"));
      return false;
    }
    const positionMode = card.querySelector(".derived-position-mode").value;
    const positionTarget = card.querySelector(".derived-position-target");
    if (["before", "after"].includes(positionMode) && !positionTarget.value.trim()) {
      markDerivedInvalid(card, positionTarget, t("derivedPositionTargetRequired"));
      return false;
    }

    const transformRows = Array.from(card.querySelectorAll(".derived-transform-row"));
    const caseRows = transformRows.filter((row) =>
      ["uppercase", "lowercase", "title_case"].includes(row.querySelector(".derived-transform-operation").value),
    );
    if (caseRows.length > 1) {
      markDerivedInvalid(
        card,
        caseRows[1].querySelector(".derived-transform-operation"),
        t("derivedTransformCaseConflict"),
      );
      return false;
    }

    for (const row of transformRows) {
      const operation = row.querySelector(".derived-transform-operation");
      const value = row.querySelector(".derived-transform-value");
      if (!operation.value) {
        markDerivedInvalid(card, operation, t("derivedTransformOperationRequired"));
        return false;
      }
      if ((operation.value === "replace_text" || derivedTextParamRequired(operation.value)) && !value.value.trim()) {
        markDerivedInvalid(card, value, t("derivedTransformValueRequired"));
        return false;
      }
      if (derivedCountParamRequired(operation.value) && !positiveSampleCount(value.value)) {
        markDerivedInvalid(card, value, t("derivedTransformCountRequired"));
        return false;
      }
    }
  }
  return true;
}

function applyDerivedSampleTransforms(value, transforms) {
  return transforms.reduce((current, transform) => applyDerivedSampleTransform(current, transform), String(value));
}

function applyDerivedSampleTransform(value, transform) {
  const text = String(value);
  const operation = transform.operation;
  const parameter = transform.text ?? transform.old ?? transform.count ?? "";
  if (operation === "replace_text") {
    const oldText = transform.old ?? "";
    return oldText ? text.replaceAll(oldText, transform.new ?? "") : text;
  }
  if (operation === "uppercase") {
    return text.toUpperCase();
  }
  if (operation === "lowercase") {
    return text.toLowerCase();
  }
  if (operation === "title_case") {
    return text
      .toLowerCase()
      .trim()
      .split(/\s+/)
      .filter(Boolean)
      .map((word) => `${word.charAt(0).toUpperCase()}${word.slice(1)}`)
      .join(" ");
  }
  if (operation === "trim") {
    return text.trim();
  }
  if (operation === "remove_extra_spaces") {
    return text.trim().replace(/\s+/g, " ");
  }
  if (operation === "add_prefix") {
    return `${parameter}${text}`;
  }
  if (operation === "add_suffix") {
    return `${text}${parameter}`;
  }
  if (operation === "keep_digits") {
    return digitsOnly(text);
  }
  if (operation === "keep_letters") {
    return text.replace(/[^\p{L}]/gu, "");
  }
  if (operation === "remove_accents") {
    return text.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }
  if (operation === "remove_punctuation") {
    return text.replace(/[^\p{L}\p{N}\s]/gu, "");
  }
  if (operation === "remove_spaces") {
    return text.replace(/\s+/g, "");
  }
  if (operation === "pad_left") {
    const count = positiveSampleCount(transform.count);
    return count ? text.padStart(count, transform.fill || " ") : text;
  }
  if (operation === "pad_right") {
    const count = positiveSampleCount(transform.count);
    return count ? text.padEnd(count, transform.fill || " ") : text;
  }
  if (operation === "take_first") {
    const count = positiveSampleCount(transform.count);
    return count ? text.slice(0, count) : text;
  }
  if (operation === "take_last") {
    const count = positiveSampleCount(transform.count);
    return count ? text.slice(-count) : text;
  }
  if (operation === "remove_first") {
    const count = positiveSampleCount(transform.count);
    return count ? text.slice(count) : text;
  }
  if (operation === "remove_last") {
    const count = positiveSampleCount(transform.count);
    return count ? text.slice(0, Math.max(0, text.length - count)) : text;
  }
  if (operation === "extract_before") {
    const separator = transform.text || "";
    const index = separator ? text.indexOf(separator) : -1;
    return index >= 0 ? text.slice(0, index) : text;
  }
  if (operation === "extract_after") {
    const separator = transform.text || "";
    const index = separator ? text.indexOf(separator) : -1;
    return index >= 0 ? text.slice(index + separator.length) : "";
  }
  if (operation === "default_if_blank") {
    return text.trim() ? text : transform.text || "";
  }
  if (operation === "format_cpf") {
    return formatCpfSample(text);
  }
  if (operation === "format_cnpj") {
    return formatCnpjSample(text);
  }
  if (operation === "format_phone") {
    return formatPhoneSample(text);
  }
  return text;
}

function positiveSampleCount(value) {
  const count = Number.parseInt(value, 10);
  return Number.isFinite(count) && count > 0 ? count : null;
}

function digitsOnly(value) {
  return String(value).replace(/[^0-9]/g, "");
}

function formatCpfSample(value) {
  const digits = digitsOnly(value);
  return digits.length === 11 ? `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}` : digits;
}

function formatCnpjSample(value) {
  const digits = digitsOnly(value);
  return digits.length === 14
    ? `${digits.slice(0, 2)}.${digits.slice(2, 5)}.${digits.slice(5, 8)}/${digits.slice(8, 12)}-${digits.slice(12)}`
    : digits;
}

function formatPhoneSample(value) {
  const digits = digitsOnly(value);
  if (digits.length === 11) {
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
  }
  if (digits.length === 10) {
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 6)}-${digits.slice(6)}`;
  }
  return digits;
}

function outputNameItems() {
  const count = (state.resolvedInputs && state.resolvedInputs.length) || state.inputPaths.length;
  return Array.from({ length: count }, (_item, index) => (state.outputNames[index] || "").trim());
}

function outputNeedsFolder() {
  const count = (state.resolvedInputs && state.resolvedInputs.length) || state.inputPaths.length;
  return count > 1;
}

function splitXlsxCanCreateMultipleFiles() {
  return byId("formatSelect").value === "xlsx" && ["files", "both"].includes(state.outputSplitMode);
}

function splitXlsxOutputPattern() {
  const path = byId("outputPathInput").value.trim() || "resultado.xlsx";
  const separatorIndex = Math.max(path.lastIndexOf("/"), path.lastIndexOf("\\"));
  const directory = separatorIndex >= 0 ? path.slice(0, separatorIndex + 1) : "";
  const name = separatorIndex >= 0 ? path.slice(separatorIndex + 1) : path;
  const dotIndex = name.toLowerCase().endsWith(".xlsx") ? name.length - 5 : name.length;
  const stem = name.slice(0, dotIndex) || "resultado";
  return `${directory}${stem}_001.xlsx, ${directory}${stem}_002.xlsx`;
}

function updateOutputArtifactNotice() {
  const notice = byId("splitXlsxNotice");
  if (!splitXlsxCanCreateMultipleFiles()) {
    notice.classList.add("hidden");
    byId("splitXlsxNoticeText").textContent = "";
    return;
  }
  byId("splitXlsxNoticeText").textContent = t("splitXlsxNoticeText").replace("{pattern}", splitXlsxOutputPattern());
  notice.classList.remove("hidden");
}

function configList(value) {
  if (!value) {
    return [];
  }
  if (Array.isArray(value)) {
    return value.map((item) => String(item));
  }
  return [String(value)];
}

function configKeyValueLines(value) {
  if (!value) {
    return [];
  }
  if (Array.isArray(value) || typeof value === "string") {
    return configList(value);
  }
  if (typeof value === "object") {
    return Object.entries(value).map(([key, item]) => `${key}=${item}`);
  }
  return [];
}

function parseLookupConfigItem(value) {
  if (!value) {
    return null;
  }
  if (typeof value === "object") {
    return {
      name: String(value.name || "").trim(),
      path: String(value.path || "").trim(),
      column: String(value.column || "").trim(),
    };
  }
  const textValue = String(value).trim();
  const equalsIndex = textValue.indexOf("=");
  const colonIndex = textValue.lastIndexOf(":");
  if (equalsIndex <= 0 || colonIndex <= equalsIndex + 1 || colonIndex >= textValue.length - 1) {
    return { name: textValue, path: "", column: "" };
  }
  return {
    name: textValue.slice(0, equalsIndex).trim(),
    path: textValue.slice(equalsIndex + 1, colonIndex).trim(),
    column: textValue.slice(colonIndex + 1).trim(),
  };
}

function lookupDefinitionsFromConfig(value) {
  const items = Array.isArray(value) ? value : value ? [value] : [];
  return items
    .map(parseLookupConfigItem)
    .filter(Boolean);
}

function configBool(value) {
  if (value === true || value === false) {
    return value;
  }
  if (typeof value === "string") {
    const normalized = value.trim().toLowerCase();
    if (["true", "1", "yes", "y", "sim"].includes(normalized)) {
      return true;
    }
    if (["false", "0", "no", "n", "nao", "não"].includes(normalized)) {
      return false;
    }
  }
  if (value === 1) {
    return true;
  }
  if (value === 0 || value == null || value === "") {
    return false;
  }
  return false;
}

function setTextareaLines(id, value) {
  byId(id).value = configList(value).join("\n");
}

function applyLoadedConfig(config = {}) {
  if (["csv", "xlsx", "parquet"].includes(config.output_format)) {
    setOutputFormat(String(config.output_format));
  }
  state.outputSplitMode = ["sheets", "files", "both"].includes(config.split_mode) ? String(config.split_mode) : "sheets";
  state.outputMaxRowsPerSheet = config.max_rows_per_sheet || "";
  state.outputSheetsPerFile = config.sheets_per_file || "";
  const csv = config.csv_options && typeof config.csv_options === "object" ? config.csv_options : {};
  byId("encodingInput").value = csv.encoding || "";
  byId("delimiterInput").value = csv.delimiter || "";
  byId("nullValueInput").value = configList(csv.null_values || csv.null_value)[0] || "";

  const where = configList(config.where);
  byId("rawFilterInput").value = where.join("\n");
  byId("filterRows").innerHTML = "";
  setFilterMode(where.length ? "advanced" : "visual");
  updateFilterHint();

  byId("lookupList").innerHTML = "";
  lookupDefinitionsFromConfig(config.lookup || config.lookups).forEach(addLookup);
  updateLookupEmptyState();

  setTextareaLines("selectColumnsInput", config.select);
  byId("renamesInput").value = configKeyValueLines(config.rename || config.renames).join("\n");
  setTextareaLines("sortInput", config.sort);
  byId("dedupeInput").checked = configBool(config.dedupe);
  byId("caseInsensitiveInput").checked = configBool(config.case_insensitive_columns);
  byId("summarizeInput").checked =
    configBool(config.summarize) ||
    configBool(config.summary_only) ||
    configList(config.summary_group_by).length > 0 ||
    configList(config.summary_totals).length > 0;
  byId("summaryOnlyInput").checked = configBool(config.summary_only);
  setTextareaLines("summaryGroupByInput", config.summary_group_by);
  setTextareaLines("summaryTotalsInput", config.summary_totals);
  updateSummaryMode();
  setTextareaLines("dedupeKeyInput", config.dedupe_keys || config.dedupe_key);
  state.outputNames = configList(config.output_names || config.output_name);
  renderQueue();

  byId("derivedColumnsList").innerHTML = "";
  const derivedColumns = Array.isArray(config.derived_columns) ? config.derived_columns : [];
  derivedColumns.forEach((item) => {
    if (item && typeof item === "object") {
      addDerivedColumn(item);
    }
  });
  updateDerivedEmptyState();
  updateOutputArtifactNotice();
  markSetupChanged();
}

function addDerivedColumn(initial = {}) {
  const template = byId("derivedColumnTemplate");
  const card = template.content.firstElementChild.cloneNode(true);
  state.derivedColumnId += 1;
  card.dataset.derivedId = String(state.derivedColumnId);
  const source = card.querySelector(".derived-source-column");
  const target = card.querySelector(".derived-position-target");
  [source, target].forEach((input) =>
    bindColumnSearchInput(input, () => {
      clearDerivedValidation(card);
      updateDerivedCard(card);
    }),
  );
  if (initial.source) source.value = initial.source;
  const nameParts = derivedNameParts(initial);
  card.querySelector(".derived-output-name").value = nameParts.output;
  card.querySelector(".derived-prefix").value = nameParts.prefix;
  card.querySelector(".derived-suffix").value = nameParts.suffix;
  card.querySelector(".derived-separator").value = nameParts.separator;
  card.querySelector(".derived-position-mode").value = initial.position?.mode || "append";
  card.querySelector(".derived-position-target").value = initial.position?.target || "";
  card.querySelector(".remove-derived-column").addEventListener("click", () => {
    card.remove();
    updateDerivedEmptyState();
  });
  card.querySelector(".add-derived-transform").addEventListener("click", () => addDerivedTransform(card));
  card
    .querySelectorAll(
      ".derived-output-name, .derived-prefix, .derived-suffix, .derived-separator, .derived-position-mode, .derived-sample-input",
    )
    .forEach((input) => {
      input.addEventListener("input", () => {
        clearDerivedValidation(card);
        updateDerivedCard(card);
      });
      input.addEventListener("change", () => {
        clearDerivedValidation(card);
        updateDerivedCard(card);
      });
    });
  byId("derivedColumnsList").appendChild(card);
  (initial.transforms || [{ operation: "trim" }]).forEach((transform) => addDerivedTransform(card, transform));
  applyLanguage();
  updateDerivedCard(card);
  updateDerivedEmptyState();
}

function addDerivedTransform(card, initial = {}) {
  const template = byId("derivedTransformTemplate");
  const row = template.content.firstElementChild.cloneNode(true);
  const operation = row.querySelector(".derived-transform-operation");
  const value = row.querySelector(".derived-transform-value");
  const extra = row.querySelector(".derived-transform-extra");
  operation.value = initial.operation || "trim";
  value.value = initial.text || initial.old || initial.count || "";
  extra.value = initial.new || initial.fill || "";
  operation.addEventListener("change", () => {
    clearDerivedValidation(card);
    updateTransformRow(row);
    updateDerivedCard(card);
  });
  [value, extra].forEach((input) =>
    input.addEventListener("input", () => {
      clearDerivedValidation(card);
      updateDerivedCard(card);
    }),
  );
  row.querySelector(".remove-derived-transform").addEventListener("click", () => {
    row.remove();
    clearDerivedValidation(card);
    updateTransformMoveButtons(card);
    updateDerivedCard(card);
  });
  const moveUp = row.querySelector(".move-derived-transform-up");
  const moveDown = row.querySelector(".move-derived-transform-down");
  moveUp.addEventListener("click", () => moveDerivedTransform(card, row, -1));
  moveUp.addEventListener("keydown", (event) => handleDerivedMoveKeydown(event, card, row, -1));
  moveDown.addEventListener("click", () => moveDerivedTransform(card, row, 1));
  moveDown.addEventListener("keydown", (event) => handleDerivedMoveKeydown(event, card, row, 1));
  card.querySelector(".derived-transforms").appendChild(row);
  updateTransformRow(row);
  updateTransformMoveButtons(card);
  updateDerivedCard(card);
}

function handleDerivedMoveKeydown(event, card, row, direction) {
  if (!["Enter", " ", "Spacebar"].includes(event.key)) {
    return;
  }
  event.preventDefault();
  if (event.currentTarget.disabled) {
    return;
  }
  moveDerivedTransform(card, row, direction);
}

function moveDerivedTransform(card, row, direction) {
  const container = card.querySelector(".derived-transforms");
  const rows = Array.from(container.querySelectorAll(".derived-transform-row"));
  const index = rows.indexOf(row);
  if (index < 0) {
    return;
  }
  if (direction < 0 && index > 0) {
    container.insertBefore(row, rows[index - 1]);
  } else if (direction > 0 && index < rows.length - 1) {
    container.insertBefore(rows[index + 1], row);
  }
  row.querySelector(".derived-transform-operation").focus();
  updateTransformMoveButtons(card);
  updateDerivedCard(card);
}

function updateTransformMoveButtons(card) {
  const rows = Array.from(card.querySelectorAll(".derived-transform-row"));
  rows.forEach((row, index) => {
    row.querySelector(".move-derived-transform-up").disabled = index === 0;
    row.querySelector(".move-derived-transform-down").disabled = index === rows.length - 1;
  });
}

function updateTransformRow(row) {
  const operation = row.querySelector(".derived-transform-operation").value;
  const value = row.querySelector(".derived-transform-value");
  const extra = row.querySelector(".derived-transform-extra");
  const valueLabel = row.querySelector(".derived-transform-value-label");
  const extraLabel = row.querySelector(".derived-transform-extra-label");
  const valueWrapper = value.closest(".derived-transform-param");
  const extraWrapper = extra.closest(".derived-transform-param");
  const noValue = [
    "trim",
    "remove_extra_spaces",
    "uppercase",
    "lowercase",
    "title_case",
    "keep_digits",
    "keep_letters",
    "remove_accents",
    "remove_punctuation",
    "remove_spaces",
    "format_cpf",
    "format_cnpj",
    "format_phone",
  ].includes(operation);
  valueWrapper.classList.toggle("hidden", noValue);
  extraWrapper.classList.toggle("hidden", noValue || !["replace_text", "pad_left", "pad_right"].includes(operation));
  if (operation === "replace_text") {
    valueLabel.textContent = t("transformValue");
    extraLabel.textContent = t("transformNewValue");
    value.placeholder = t("transformValue");
    extra.placeholder = t("transformNewValue");
  } else if (["pad_left", "pad_right"].includes(operation)) {
    valueLabel.textContent = t("transformCount");
    extraLabel.textContent = t("transformFill");
    value.placeholder = t("transformCount");
    extra.placeholder = t("transformFill");
  } else if (["take_first", "take_last", "remove_first", "remove_last"].includes(operation)) {
    valueLabel.textContent = t("transformCount");
    value.placeholder = t("transformCount");
  } else if (["extract_before", "extract_after"].includes(operation)) {
    valueLabel.textContent = t("transformSeparator");
    value.placeholder = t("transformSeparator");
  } else if (operation === "default_if_blank") {
    valueLabel.textContent = t("transformDefault");
    value.placeholder = t("transformDefault");
  } else {
    valueLabel.textContent = t("transformValue");
    extraLabel.textContent = t("transformNewValue");
    value.placeholder = t("transformValue");
    extra.placeholder = t("transformNewValue");
  }
}

function updateDerivedCard(card) {
  const source = card.querySelector(".derived-source-column").value.trim();
  const name = formatDerivedName(
    source,
    card.querySelector(".derived-output-name").value.trim(),
    card.querySelector(".derived-prefix").value.trim(),
    card.querySelector(".derived-suffix").value.trim(),
    card.querySelector(".derived-separator").value,
  );
  card.querySelector(".derived-preview").textContent = name;
  const transformLabels = Array.from(card.querySelectorAll(".derived-transform-operation"))
    .map((select) => select.options[select.selectedIndex]?.textContent.trim())
    .filter(Boolean);
  const summary = source
    ? t("derivedSummary").replace("{name}", name).replace("{source}", source)
    : t("derivedSummaryEmpty");
  card.querySelector(".derived-summary").textContent = transformLabels.length
    ? `${summary} ${transformLabels.join(", ")}.`
    : summary;
  updateDerivedSample(card);
}

function updateDerivedSample(card) {
  const sample = card.querySelector(".derived-sample-input").value;
  const before = card.querySelector(".derived-sample-before");
  const after = card.querySelector(".derived-sample-after");
  if (!sample) {
    before.textContent = "-";
    after.textContent = "-";
    return;
  }
  const transforms = Array.from(card.querySelectorAll(".derived-transform-row")).map(transformPayload);
  before.textContent = sample;
  after.textContent = applyDerivedSampleTransforms(sample, transforms);
}

function updateDerivedEmptyState() {
  byId("noDerivedColumnsText").classList.toggle("hidden", Boolean(document.querySelector(".derived-column-card")));
}

function bindColumnSearchInput(input, onChange) {
  prepareColumnSearch(input);
  updateColumnOptions(input);
  input.addEventListener("focus", () => updateColumnOptions(input));
  input.addEventListener("input", () => {
    updateColumnOptions(input);
    onChange();
  });
  input.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      moveColumnSuggestion(input, 1);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      moveColumnSuggestion(input, -1);
    } else if (event.key === "Enter") {
      event.preventDefault();
      chooseActiveColumnSuggestion(input) || chooseFirstColumnSuggestion(input);
      onChange();
    } else if (event.key === "Tab") {
      event.preventDefault();
      moveColumnSuggestion(input, event.shiftKey ? -1 : 1);
    } else if (event.key === "Escape") {
      closeColumnSuggestions(input);
    }
  });
  input.addEventListener("blur", () => {
    setTimeout(() => closeColumnSuggestions(input), 120);
  });
  input.addEventListener("change", onChange);
}

function payload() {
  const format = byId("formatSelect").value;
  const rawFilter = byId("rawFilterInput").value.trim();
  const summarize = byId("summarizeInput").checked;
  const summaryOnly = byId("summaryOnlyInput").checked && summarize;
  const nullValue = byId("nullValueInput").value;
  const inputKinds = currentInputKinds();
  const hasCsvOptions = inputKinds.has("csv");
  const hasZipOptions = inputKinds.has("zip");
  const hasExcelOptions = inputKinds.has("excel");
  const hasQueueOptions = inputKinds.has("queue");
  return {
    input_path: state.inputPath,
    input_paths: state.inputPaths,
    output_path: byId("outputPathInput").value.trim(),
    output_format: format,
    split_mode: state.outputSplitMode,
    max_rows_per_sheet: state.outputMaxRowsPerSheet,
    sheets_per_file: state.outputSheetsPerFile,
    output_names: outputNameItems(),
    summarize,
    summary_only: summaryOnly,
    summary_group_by: summarize ? linesFromTextarea("summaryGroupByInput") : [],
    summary_totals: summarize ? linesFromTextarea("summaryTotalsInput") : [],
    filters:
      state.filterMode === "advanced"
        ? { mode: "raw", raw: rawFilter }
        : { mode: "visual", combine: byId("combineSelect").value, conditions: visualConditions() },
    select: linesFromTextarea("selectColumnsInput"),
    lookups: visualLookups(),
    derived_columns: visualDerivedColumns(),
    renames: linesFromTextarea("renamesInput"),
    dedupe: byId("dedupeInput").checked,
    dedupe_keys: linesFromTextarea("dedupeKeyInput"),
    sort: linesFromTextarea("sortInput"),
    case_insensitive_columns: byId("caseInsensitiveInput").checked,
    zip_passwords: hasZipOptions ? [...state.zipPasswords] : [],
    all_excel_sheets: hasExcelOptions && byId("allExcelSheetsInput").checked,
    reuse_schema: hasQueueOptions && byId("reuseSchemaInput").checked,
    delete_zip_after_extract: hasZipOptions && byId("deleteZipInput").checked,
    report_path: byId("reportPathInput").value.trim(),
    rejects_path: byId("rejectsPathInput").value.trim(),
    csv_options: hasCsvOptions
      ? {
          encoding: byId("encodingInput").value.trim(),
          delimiter: byId("delimiterInput").value.trim(),
          null_values: nullValue ? [nullValue] : [],
        }
      : {},
  };
}

function confirmZipDeletionBeforeRun(runPayload) {
  if (!runPayload.delete_zip_after_extract) {
    return true;
  }
  const zipPaths = (runPayload.input_paths || []).filter((path) => String(path).toLowerCase().endsWith(".zip"));
  const paths = zipPaths.length ? zipPaths.join("\n") : runPayload.input_path;
  if (!window.confirm(t("confirmZipDelete").replace("{paths}", paths))) {
    return false;
  }
  runPayload.confirm_delete_zip_after_extract = true;
  return true;
}

function setRunControlsRunning(running, options = {}) {
  const canCancel = options.canCancel !== false;
  byId("runBtn").disabled = running;
  byId("cancelRunBtn").classList.toggle("hidden", !running);
  byId("cancelRunBtn").disabled = running && !canCancel;
  byId("cancelRunBtn").textContent = t("cancelRun");
}

function setRunControlsCanceling() {
  byId("runBtn").disabled = true;
  byId("cancelRunBtn").classList.remove("hidden");
  byId("cancelRunBtn").disabled = true;
  byId("cancelRunBtn").textContent = t("canceling");
}

function notifyCloseBlocked() {
  setStatus(t("readyTitle"), t("closeBlocked"), "running");
  setRunStep("running", t("closeBlocked"));
}

async function inspectInput() {
  if (!state.inputPath) {
    setStatus(t("error"), t("chooseCsv"), "error");
    return;
  }
  setStatus(t("readyTitle"), t("inspecting"), "running");
  showDetails("");
  showFriendlyError(null);
  try {
    const data = handleResponse(await state.api.inspect_csv(payload()));
    byId("inputSizeText").textContent = formatBytes(data.size_bytes);
    state.resolvedInputs = data.inputs || [];
    renderQueue();
    showInputWarnings(data.warnings || []);
    setColumns(data.columns, data.types || {});
    const schemaNote = data.schema_compatible === false ? ` ${t("schemaMismatchShort")}` : "";
    setStatus(t("readyTitle"), `${data.columns.length} ${t("columnsLoaded")}${schemaNote}`, "done");
  } catch (error) {
    await maybePromptForZipPasswordAndRetryInspect(error);
  }
}

async function validateFilter() {
  if (!state.inputPath) {
    setStatus(t("error"), t("chooseCsv"), "error");
    return;
  }
  if (!validateVisualRowsBeforeSubmit()) {
    return;
  }
  if (!validateLookupRowsBeforeSubmit()) {
    return;
  }
  if (!validateDerivedRowsBeforeSubmit()) {
    return;
  }
  setStatus(t("readyTitle"), t("validating"), "running");
  showDetails("");
  const data = handleResponse(await state.api.validate_filter(payload()));
  setStatus(t("readyTitle"), t("valid"), "done");
  showDetails({ filtros: data.normalized_filters, sql: data.sql });
}

async function previewRows() {
  if (!state.inputPath) {
    setStatus(t("error"), t("chooseCsv"), "error");
    return;
  }
  if (!validateVisualRowsBeforeSubmit()) {
    return;
  }
  if (!validateLookupRowsBeforeSubmit()) {
    return;
  }
  if (!validateDerivedRowsBeforeSubmit()) {
    return;
  }
  setStatus(t("readyTitle"), t("previewing"), "running");
  showDetails("");
  showFriendlyError(null);
  try {
    const data = handleResponse(await state.api.preview_rows({ ...payload(), limit: 20 }));
    renderPreview(data);
    setStatus(t("readyTitle"), previewMetaText(data, data.rows.length), "done");
  } catch (error) {
    showFriendlyError(error);
    showDetails(error.details || error);
  }
}

function resetPreview() {
  const panel = byId("previewPanel");
  if (!panel) {
    return;
  }
  panel.classList.add("hidden");
  byId("previewMeta").textContent = "";
  byId("previewTableWrap").innerHTML = "";
}

function renderPreview(data) {
  const panel = byId("previewPanel");
  const meta = byId("previewMeta");
  const wrap = byId("previewTableWrap");
  wrap.innerHTML = "";
  const rows = data.rows || [];
  meta.textContent = previewMetaText(data, rows.length);
  if (rows.length) {
    const table = document.createElement("table");
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    (data.columns || []).forEach((column) => {
      const cell = document.createElement("th");
      cell.textContent = column;
      headerRow.appendChild(cell);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
    const tbody = document.createElement("tbody");
    rows.forEach((row) => {
      const tr = document.createElement("tr");
      row.forEach((value) => {
        const cell = document.createElement("td");
        cell.textContent = value == null ? "" : String(value);
        tr.appendChild(cell);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    wrap.appendChild(table);
  }
  panel.classList.remove("hidden");
}

function previewMetaText(data, rowCount) {
  const total = Number(data.input_count || 1);
  const path = data.input_path || "";
  if (!rowCount) {
    return total > 1 ? formatMessage(t("previewEmptyQueue"), { path, total }) : t("previewEmpty");
  }
  if (total > 1) {
    return formatMessage(t("previewLoadedQueue"), { count: rowCount, path, total });
  }
  return formatMessage(t("previewLoaded"), { count: rowCount, path });
}

async function startRun(runPayload) {
  const data = handleResponse(await state.api.start_filter_run(runPayload));
  state.activeJobId = data.job_id;
  setRunControlsRunning(true);
  setRunStep("running", t("stepRunRunning"));
  pollJob(data.job_id);
}

async function runFilter() {
  if (!state.inputPath) {
    setStatus(t("error"), t("chooseCsv"), "error");
    return;
  }
  if (!validateVisualRowsBeforeSubmit()) {
    return;
  }
  if (!validateLookupRowsBeforeSubmit()) {
    return;
  }
  if (!validateDerivedRowsBeforeSubmit()) {
    return;
  }
  if (!byId("outputPathInput").value.trim()) {
    setStatus(t("error"), t("chooseOutput"), "error");
    return;
  }
  const runPayload = payload();
  if (!confirmZipDeletionBeforeRun(runPayload)) {
    return;
  }
  setStatus(t("readyTitle"), t("running"), "running");
  showDetails("");
  showFriendlyError(null);
  resetResultCards();
  setRunControlsRunning(true, { canCancel: false });
  setRunStep("running", t("stepRunRunning"));
  byId("openFolderBtn").classList.add("hidden");
  try {
    await startRun(runPayload);
  } catch (error) {
    if (await maybeConfirmOverwriteAndRetry(error, runPayload)) {
      return;
    }
    const retried = await maybePromptForZipPasswordAndRetry(error);
    if (!retried) {
      setRunStep("error", t("stepRunError"));
      setRunControlsRunning(false);
    }
  }
}

async function cancelCurrentJob() {
  if (!state.activeJobId) {
    return;
  }
  setRunControlsCanceling();
  setStatus(t("readyTitle"), t("canceling"), "running");
  setRunStep("running", t("canceling"));
  try {
    const data = handleResponse(await state.api.cancel_job(state.activeJobId));
    updateJobStatus(data);
  } catch (error) {
    showFriendlyError(error);
    showDetails(error.details || error);
  }
}

async function maybeConfirmOverwriteAndRetry(error, runPayload) {
  if (!error || error.type !== "overwrite_confirmation_required") {
    return false;
  }
  const paths = Array.isArray(error.paths) && error.paths.length ? error.paths.join("\n") : error.details || "";
  if (!window.confirm(t("confirmOverwrite").replace("{paths}", paths))) {
    showFriendlyError(error);
    showDetails(error.details || error);
    return false;
  }
  runPayload.confirm_overwrite = true;
  setStatus(t("readyTitle"), t("running"), "running");
  showDetails("");
  showFriendlyError(null);
  try {
    await startRun(runPayload);
    return true;
  } catch (_retryError) {
    setRunStep("error", t("stepRunError"));
    return false;
  }
}

async function maybePromptForZipPasswordAndRetry(error) {
  if (await promptForZipPassword(error)) {
    await runFilter();
    return true;
  }
  return false;
}

async function maybePromptForZipPasswordAndRetryInspect(error) {
  if (await promptForZipPassword(error)) {
    await inspectInput();
    return true;
  }
  return false;
}

async function promptForZipPassword(error) {
  if (!isZipPasswordError(error)) {
    return false;
  }
  const password = window.prompt(t("zipPasswordAsk"));
  if (!password) {
    return false;
  }
  addZipPassword(password);
  return true;
}

function addZipPassword(password) {
  const value = String(password || "");
  if (!value) {
    return;
  }
  state.zipPasswords.push(value);
  updateZipPasswordStatus();
}

function clearZipPasswords() {
  state.zipPasswords = [];
  updateZipPasswordStatus();
}

function updateZipPasswordStatus() {
  const status = byId("zipPasswordStatus");
  if (!status) {
    return;
  }
  const count = state.zipPasswords.length;
  status.textContent = count
    ? formatMessage(t("zipPasswordsStored"), { count })
    : t("zipPasswordSessionOnly");
  const clearButton = byId("clearZipPasswordsBtn");
  if (clearButton) {
    const group = clearButton.closest("[data-input-option-group]");
    clearButton.disabled = !group || group.classList.contains("hidden") || count === 0;
  }
}

function isZipPasswordError(error) {
  if (!error) {
    return false;
  }
  return error.type === "ZipPasswordRequiredError" || String(error.message || error).toLowerCase().includes("zip");
}

function pollJob(jobId) {
  clearInterval(state.pollTimer);
  state.pollTimer = setInterval(async () => {
    try {
      const data = handleResponse(await state.api.get_job_status(jobId));
      if (!data.running) {
        state.activeJobId = "";
      }
      updateJobStatus(data);
      if (!data.running) {
        clearInterval(state.pollTimer);
        setRunControlsRunning(false);
        updateWorkflowSteps();
      }
    } catch (_error) {
      clearInterval(state.pollTimer);
      state.activeJobId = "";
      setRunStep("error", t("stepRunError"));
      setRunControlsRunning(false);
    }
  }, 850);
}

function updateJobStatus(job) {
  if (job.phase === "cancelled") {
    setStatus(t("readyTitle"), t("cancelled"), "done");
    setRunStep("cancelled", t("stepRunCancelled"));
    clearZipPasswords();
    showFriendlyError(null);
    showDetails("");
    resetResultCards();
    state.outputPaths = [];
    return;
  }
  if (job.error) {
    setStatus(t("error"), job.error.message, "error");
    setRunStep("error", t("stepRunError"));
    clearZipPasswords();
    showFriendlyError(job.error);
    showDetails(job.error.details || job.error);
    if (isZipPasswordError(job.error)) {
      setTimeout(() => {
        maybePromptForZipPasswordAndRetry(job.error);
      }, 50);
    }
    return;
  }
  if (job.running) {
    if (job.cancel_requested || job.phase === "canceling") {
      setRunControlsCanceling();
      setStatus(t("readyTitle"), t("canceling"), "running");
      setRunStep("running", t("canceling"));
    } else {
      setStatus(t("readyTitle"), phaseLabel(job.phase), "running");
      setRunStep("running", phaseLabel(job.phase));
    }
    return;
  }
  const report = job.report || {};
  state.outputPaths = report.output_paths || [];
  const failed = report.failed_inputs || (report.errors || []).length || 0;
  if (failed) {
    const message = state.outputPaths.length ? t("queuePartialDone") : t("queueAllFailed");
    setStatus(t("error"), message, "error");
    setRunStep("error", t("stepRunError"));
    clearZipPasswords();
    showFriendlyError({
      message,
      details: JSON.stringify(report.errors || report, null, 2),
    });
    showResultCards(report);
    showDetails(report);
    if (state.outputPaths.length) {
      byId("openFolderBtn").classList.remove("hidden");
    }
    return;
  }
  setStatus(t("readyTitle"), `${t("done")} ${report.output_rows || 0} ${t("rowsWritten")}`, "done");
  setRunStep("done", t("stepRunDone"));
  clearZipPasswords();
  showResultCards(report);
  showDetails(report);
  if (state.outputPaths.length) {
    byId("openFolderBtn").classList.remove("hidden");
  }
}

function resetResultCards() {
  byId("resultCards").classList.add("hidden");
  byId("outputList").classList.add("hidden");
  byId("outputList").innerHTML = "";
  ["filesCreatedValue", "rowsSavedValue", "filesProcessedValue", "warningsValue", "filesFailedValue"].forEach((id) => {
    byId(id).textContent = "0";
  });
}

function showResultCards(report) {
  const paths = report.output_paths || [];
  const runs = report.runs || [];
  const warnings = report.warnings || [];
  const failed = report.failed_inputs || (report.errors || []).length || 0;
  byId("filesCreatedValue").textContent = String(paths.length);
  byId("rowsSavedValue").textContent = String(report.output_rows || 0);
  byId("filesProcessedValue").textContent = String(report.processed_inputs || (runs.length || (paths.length ? 1 : 0)));
  byId("warningsValue").textContent = String(warnings.length);
  byId("filesFailedValue").textContent = String(failed);
  byId("resultCards").classList.remove("hidden");

  const outputList = byId("outputList");
  outputList.innerHTML = "";
  paths.forEach((path) => {
    const row = document.createElement("button");
    row.type = "button";
    row.className = "output-row";
    row.textContent = path;
    row.addEventListener("click", async () => handleResponse(await state.api.open_output_folder(path)));
    outputList.appendChild(row);
  });
  (report.errors || []).forEach((error) => {
    const row = document.createElement("div");
    row.className = "output-row output-error";
    const source = error.input_path ? `<strong>${escapeHtml(error.input_path)}</strong>` : "";
    const message = escapeHtml(error.message || t("error"));
    row.innerHTML = `${source}<span>${message}</span>`;
    outputList.appendChild(row);
  });
  outputList.classList.toggle("hidden", !paths.length && !(report.errors || []).length);
}

function phaseLabel(phase) {
  const labels = {
    queued: state.language === "en-US" ? "Queued" : "Na fila",
    inspecting: state.language === "en-US" ? "Reading file" : "Lendo o arquivo",
    validating: state.language === "en-US" ? "Validating filter" : "Validando o filtro",
    exporting: state.language === "en-US" ? "Creating output file" : "Gerando o arquivo",
    finishing: state.language === "en-US" ? "Finishing" : "Finalizando",
    canceling: t("canceling"),
    cancelled: t("cancelled"),
  };
  return labels[phase] || phase || t("running");
}

function formatBytes(bytes) {
  if (!bytes) return "-";
  const units = ["B", "KB", "MB", "GB"];
  let value = Number(bytes);
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return `${value.toFixed(unit === 0 ? 0 : 1)} ${units[unit]}`;
}

function setFilterMode(mode) {
  state.filterMode = mode;
  document.querySelectorAll("[data-filter-tab]").forEach((tab) => {
    const active = tab.dataset.filterTab === mode;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-selected", active ? "true" : "false");
    tab.tabIndex = active ? 0 : -1;
  });
  byId("visualFilterPanel").classList.toggle("hidden", mode !== "visual");
  byId("advancedFilterPanel").classList.toggle("hidden", mode !== "advanced");
  markSetupChanged();
}

function handleFilterTabKeydown(event, tab) {
  const tabs = Array.from(document.querySelectorAll("[data-filter-tab]"));
  const currentIndex = tabs.indexOf(tab);
  if (currentIndex < 0) {
    return;
  }
  let nextIndex = currentIndex;
  if (event.key === "ArrowRight" || event.key === "ArrowDown") {
    nextIndex = (currentIndex + 1) % tabs.length;
  } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
    nextIndex = (currentIndex - 1 + tabs.length) % tabs.length;
  } else if (event.key === "Home") {
    nextIndex = 0;
  } else if (event.key === "End") {
    nextIndex = tabs.length - 1;
  } else if (event.key !== "Enter" && event.key !== " ") {
    return;
  }
  event.preventDefault();
  const nextTab = tabs[nextIndex];
  setFilterMode(nextTab.dataset.filterTab);
  nextTab.focus();
}

function setOutputFormat(format) {
  byId("formatSelect").value = format;
  document.querySelectorAll("[data-format-card]").forEach((card) => {
    const active = card.dataset.formatCard === format;
    card.classList.toggle("active", active);
    card.setAttribute("aria-checked", active ? "true" : "false");
    card.tabIndex = active ? 0 : -1;
  });
  syncOutputSuffixWithFormat();
  updateOutputArtifactNotice();
  markSetupChanged();
}

function handleOutputFormatKeydown(event, card) {
  const cards = Array.from(document.querySelectorAll("[data-format-card]"));
  const currentIndex = cards.indexOf(card);
  if (currentIndex < 0) {
    return;
  }
  let nextIndex = currentIndex;
  if (event.key === "ArrowRight" || event.key === "ArrowDown") {
    nextIndex = (currentIndex + 1) % cards.length;
  } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
    nextIndex = (currentIndex - 1 + cards.length) % cards.length;
  } else if (event.key === "Home") {
    nextIndex = 0;
  } else if (event.key === "End") {
    nextIndex = cards.length - 1;
  } else if (event.key !== "Enter" && event.key !== " ") {
    return;
  }
  event.preventDefault();
  const nextCard = cards[nextIndex];
  setOutputFormat(nextCard.dataset.formatCard);
  nextCard.focus();
}

function syncOutputSuffixWithFormat() {
  const input = byId("outputPathInput");
  const path = input.value.trim();
  const format = byId("formatSelect").value;
  if (!path) {
    return;
  }
  const suffixes = { csv: ".csv", xlsx: ".xlsx", parquet: ".parquet" };
  const expectedSuffix = suffixes[format] || ".csv";
  if (/\.(csv|xlsx|parquet)$/i.test(path) && !path.toLowerCase().endsWith(expectedSuffix)) {
    setOutputPath(path.replace(/\.(csv|xlsx|parquet)$/i, expectedSuffix));
  }
}

function bindEvents() {
  if (state.eventsBound) {
    return;
  }
  state.eventsBound = true;
  const workspace = document.querySelector(".workspace");
  workspace.addEventListener("input", (event) => {
    if (event.target.matches("input, textarea, select")) {
      markSetupChanged();
    }
  });
  workspace.addEventListener("change", (event) => {
    if (event.target.matches("input, textarea, select")) {
      markSetupChanged();
    }
  });

  byId("browseInputBtn").addEventListener("click", async () => {
    const data = handleResponse(await state.api.choose_input_files());
    const paths = data.paths && data.paths.length ? data.paths : data.path ? [data.path] : [];
    if (paths.length) {
      setInputPaths(paths);
      await inspectInput();
    }
  });

  byId("browseOutputBtn").addEventListener("click", async () => {
    const data = handleResponse(await state.api.choose_output_file(byId("formatSelect").value, outputNeedsFolder()));
    if (data.path) setOutputPath(data.path);
  });

  byId("addZipPasswordBtn").addEventListener("click", () => {
    const password = window.prompt(t("zipPasswordAsk"));
    if (password) {
      addZipPassword(password);
    }
  });

  byId("clearZipPasswordsBtn").addEventListener("click", clearZipPasswords);

  byId("browseReportBtn").addEventListener("click", async () => {
    const data = handleResponse(await state.api.choose_report_file());
    if (data.path) byId("reportPathInput").value = data.path;
  });

  byId("browseRejectsBtn").addEventListener("click", async () => {
    const data = handleResponse(await state.api.choose_rejects_file());
    if (data.path) byId("rejectsPathInput").value = data.path;
  });

  byId("formatSelect").addEventListener("change", () => setOutputFormat(byId("formatSelect").value));
  byId("outputPathInput").addEventListener("input", updateOutputArtifactNotice);
  byId("summarizeInput").addEventListener("change", updateSummaryMode);
  document.querySelectorAll("[data-format-card]").forEach((card) => {
    card.addEventListener("click", () => setOutputFormat(card.dataset.formatCard));
    card.addEventListener("keydown", (event) => handleOutputFormatKeydown(event, card));
  });

  byId("addFilterBtn").addEventListener("click", () => addFilterRow());
  byId("addLookupBtn").addEventListener("click", () => addLookup());
  byId("addDerivedColumnBtn").addEventListener("click", () => addDerivedColumn());
  byId("loadConfigBtn").addEventListener("click", async () => {
    const chosen = handleResponse(await state.api.choose_config_file());
    if (!chosen.path) {
      return;
    }
    const data = handleResponse(await state.api.load_config({ config_path: chosen.path }));
    applyLoadedConfig(data.config || {});
    setStatus(t("readyTitle"), `${t("configLoaded")} ${data.path}`, "done");
  });
  byId("saveConfigBtn").addEventListener("click", async () => {
    if (!validateLookupRowsBeforeSubmit()) {
      return;
    }
    if (!validateDerivedRowsBeforeSubmit()) {
      return;
    }
    const data = handleResponse(await state.api.save_config(payload()));
    if (data.path) {
      setStatus(t("readyTitle"), `${t("configSaved")} ${data.path}`, "done");
    }
  });
  byId("visualTab").addEventListener("click", () => setFilterMode("visual"));
  byId("advancedTab").addEventListener("click", () => setFilterMode("advanced"));
  document.querySelectorAll("[data-filter-tab]").forEach((tab) => {
    tab.addEventListener("keydown", (event) => handleFilterTabKeydown(event, tab));
  });
  byId("checkExpressionBtn").addEventListener("click", validateFilter);
  byId("previewRowsBtn").addEventListener("click", previewRows);
  byId("runBtn").addEventListener("click", runFilter);
  byId("cancelRunBtn").addEventListener("click", cancelCurrentJob);
  byId("resetBtn").addEventListener("click", () => window.location.reload());

  byId("openFolderBtn").addEventListener("click", async () => {
    const firstPath = state.outputPaths[0] || byId("outputPathInput").value;
    if (firstPath) handleResponse(await state.api.open_output_folder(firstPath));
  });

  byId("languageSelect").addEventListener("change", async (event) => {
    state.language = event.target.value;
    await state.api.set_language(state.language);
    applyLanguage();
    setStatus(t("readyTitle"), t("readyText"));
  });

  const dropZone = byId("dropZone");
  dropZone.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      byId("browseInputBtn").click();
    }
  });
  dropZone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropZone.classList.add("dragging");
  });
  dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragging"));
  dropZone.addEventListener("drop", async (event) => {
    event.preventDefault();
    dropZone.classList.remove("dragging");
    const paths = Array.from(event.dataTransfer.files || [])
      .map((file) => file && (file.path || file.pywebviewFullPath))
      .filter(Boolean);
    if (paths.length) {
      setInputPaths(paths);
      await inspectInput();
    } else {
      setStatus(t("readyTitle"), t("droppedFileNeedsPicker"));
    }
  });

  document.querySelectorAll(".step-link").forEach((link) => {
    link.addEventListener("click", () => {
      document.querySelectorAll(".step-link").forEach((item) => {
        item.classList.remove("active");
        item.removeAttribute("aria-current");
      });
      link.classList.add("active");
      link.setAttribute("aria-current", "step");
    });
  });
  setOutputFormat(byId("formatSelect").value || "csv");
  updateLookupEmptyState();
  updateDerivedEmptyState();
  updateWorkflowSteps();
}

async function initialize() {
  if (!window.pywebview || !window.pywebview.api) {
    state.api = createBrowserFallbackApi();
    applyLanguage();
    bindEvents();
    setStatus("Pywebview", t("bridgeNotReady"), "error");
    return;
  }
  state.api = window.pywebview.api;
  const info = handleResponse(await state.api.get_app_info());
  state.language = info.language || "pt-BR";
  byId("languageSelect").value = state.language;
  applyLanguage();
  bindEvents();
  setStatus(t("readyTitle"), t("readyText"));
}

window.addEventListener("pywebviewready", initialize);
window.dataslicerNotifyCloseBlocked = notifyCloseBlocked;

window.addEventListener("load", () => {
  setTimeout(() => {
    if (!state.api) {
      state.api = createBrowserFallbackApi();
      applyLanguage();
      bindEvents();
      setStatus("Pywebview", t("bridgeWaiting"), "running");
    }
  }, 600);
});
