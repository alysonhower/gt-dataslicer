const state = {
  api: null,
  inputPath: "",
  inputPaths: [],
  outputPath: "",
  outputPaths: [],
  outputNames: [],
  outputNameTouchedIndexes: new Set(),
  outputNameSuffix: "",
  outputNameSuffixTouched: false,
  summarizationOutputSuffix: "",
  summarizationOutputSuffixTouched: false,
  outputFormatExplicit: false,
  resolvedInputs: [],
  columns: [],
  language: "pt-BR",
  filterMode: "visual",
  pollTimer: null,
  columnSuggestionListId: 0,
  eventsBound: false,
  inputPickerOpen: false,
  derivedColumnId: 0,
  operatorPickerId: 0,
};

const FILTER_OPERATOR_OPTIONS = [
  { id: "equals", symbol: "=", labelKey: "opEquals" },
  { id: "not_equals", symbol: "≠", labelKey: "opNotEquals" },
  { id: "gt", symbol: ">", labelKey: "opGt" },
  { id: "gte", symbol: "≥", labelKey: "opGte" },
  { id: "lt", symbol: "<", labelKey: "opLt" },
  { id: "lte", symbol: "≤", labelKey: "opLte" },
  { id: "in", symbol: "∈", labelKey: "opIn" },
  { id: "not_in", symbol: "∉", labelKey: "opNotIn" },
  { id: "between", symbol: "≤ x ≤", labelKey: "opBetween" },
  { id: "contains", symbol: "…x…", labelKey: "opContains" },
  { id: "starts_with", symbol: "x…", labelKey: "opStartsWith" },
  { id: "ends_with", symbol: "…x", labelKey: "opEndsWith" },
  { id: "regex", symbol: ".*", labelKey: "opRegex" },
  { id: "is_blank", symbol: "∅", labelKey: "opIsBlank" },
  { id: "is_not_blank", symbol: "≠ ∅", labelKey: "opIsNotBlank" },
];

const text = {
  "pt-BR": {
    readyTitle: "Pronto",
    readyText: "Escolha um arquivo de entrada para começar.",
    inspecting: "Lendo o arquivo...",
    validating: "Validando filtro...",
    valid: "Filtro válido.",
    running: "Gerando o arquivo...",
    done: "Arquivo gerado com sucesso.",
    error: "Algo precisa de atenção.",
    chooseCsv: "Escolha um arquivo de entrada.",
    chooseOutput: "Escolha a pasta de destino antes de continuar.",
    chooseOutputDirectory: "Escolha a pasta de destino.",
    noColumns: "Escolha um arquivo para carregar as colunas.",
    droppedFileNeedsPicker: "Clique na área do arquivo para escolher pelo computador e liberar o caminho completo.",
    noFile: "Nenhum arquivo escolhido",
    columnsLoaded: "colunas carregadas.",
    columnSearchPlaceholder: "Buscar coluna",
    inputQueue: "Arquivos na fila",
    outputName: "Nome de saída",
    outputNamePlaceholder: "Opcional",
    zipPasswords: "Senhas de ZIP",
    onePasswordPerLine: "Uma senha por linha",
    allExcelSheets: "Processar todas as abas do Excel",
    reuseSchema: "Reutilizar o esquema do primeiro arquivo",
    deleteZipAfterExtract: "Excluir ZIP após extrair com sucesso",
    rowsWritten: "linhas gravadas.",
    progressTitle: "Andamento",
    progressItem: "Item {index} de {total}",
    progressArtifactFiltered: "Base filtrada",
    progressArtifactSummarization: "Sumarização",
    progressArtifactOutput: "Saída",
    progressPercentLabel: "{percent}% concluído",
    progressIndeterminateLabel: "Andamento em execução sem percentual confiável",
    bridgeNotReady: "A ponte com Python ainda não está pronta.",
    bridgeWaiting: "Aguardando a ponte com Python.",
    language: "Idioma",
    stepFile: "Arquivo",
    stepFilter: "Filtro",
    stepDerived: "Novas colunas",
    stepSummarization: "Sumarização",
    stepOutput: "Saída",
    stepRun: "Gerar",
    stepEyebrow: "Etapa {number}",
    chooseFile: "Escolha o arquivo",
    browseInput: "Escolher arquivo",
    dropStrong: "Clique ou arraste o arquivo aqui",
    dropHelp: "Pressione Enter ou Espaço para escolher pelo computador.",
    fileLabel: "Arquivo",
    sizeLabel: "Tamanho",
    columnsLabel: "Colunas",
    readOptions: "Opções de leitura",
    encoding: "Codificação",
    delimiter: "Delimitador",
    nullValue: "Valor nulo",
    emptyPlaceholder: "vazio",
    buildFilter: "Monte o filtro",
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
    chooseOutputFolder: "Escolha a pasta de saída",
    chooseDestination: "Escolher destino",
    chooseFolder: "Escolher pasta",
    routeModeTitle: "O que você quer gerar?",
    routeModeHelp: "Sumarização aqui significa uma análise agrupada com totais, no estilo IDEA.",
    cleanBase: "Limpar base",
    cleanBaseHelp: "Filtra e salva a base limpa.",
    cleanThenSummarization: "Limpar e sumarizar base limpa",
    cleanThenSummarizationHelp: "Salva a base limpa e também a sumarização agrupada com totais.",
    summarizationOnly: "Sumarizar bases de entrada",
    summarizationOnlyHelp: "Gera somente a sumarização agrupada com totais.",
    summarization: "Gerar sumarização",
    summarizationOnlyOption: "Gerar apenas a sumarização",
    summarizationGroupBy: "Agrupar por",
    summarizationTotals: "Somar colunas na sumarização",
    summarizationColumnPlaceholder: "Uma coluna por linha",
    summarizationSetupTitle: "Configure a sumarização",
    summarizationSetupHelp: "Escolha as colunas de agrupamento e as colunas numéricas que serão totalizadas.",
    format: "Formato",
    formatCsvTitle: "CSV",
    formatExcelTitle: "Excel",
    formatParquetTitle: "Parquet",
    saveAs: "Pasta de destino",
    saveToFolder: "Pasta de destino",
    chooseSavePlaceholder: "Escolha uma pasta",
    chooseFolderPlaceholder: "Escolha uma pasta",
    outputNamesTitle: "Nomes",
    cleanupOutputTitle: "Base limpa",
    cleanupOutputHelp: "Escolha o formato da base filtrada.",
    summarizationOutputTitle: "Sumarização",
    summarizationOutputHelp: "Escolha o formato da sumarização agrupada.",
    generatedOutputNamesTitle: "Nomes dos arquivos",
    generatedOutputNamesHelp: "Edite apenas o nome base. O formato define a extensão.",
    outputNameSuffix: "Sufixo da base limpa",
    outputNameStemPlaceholder: "Nome base",
    resetOutputNames: "Redefinir nomes gerados",
    defaultOutputSuffix: "_tratada",
    summarizationOutputSuffix: "Sufixo da sumarização",
    defaultSummarizationOutputSuffix: "_sumarizacao",
    derivedColumnsTitle: "Criar novas colunas",
    derivedColumnsHelp: "Opcional: crie colunas limpas a partir das colunas filtradas.",
    addDerivedColumn: "Adicionar coluna",
    noDerivedColumns: "Nenhuma coluna nova será criada.",
    saveConfig: "Salvar configuração",
    configSaved: "Configuração salva.",
    sourceColumn: "Coluna de origem",
    namePrefix: "Prefixo",
    nameSuffix: "Sufixo",
    nameSeparator: "Separador",
    prefixPlaceholder: "LIMPO",
    suffixPlaceholder: "FORMATADO",
    addTransformation: "Adicionar transformação",
    removeDerivedColumn: "Remover coluna",
    removeTransformation: "Remover transformação",
    derivedPosition: "Posição",
    positionAppend: "No fim da tabela",
    positionBefore: "Antes de uma coluna",
    positionAfter: "Depois de uma coluna",
    positionTarget: "Coluna de referência",
    newColumn: "Nova coluna",
    derivedSummaryEmpty: "Escolha a coluna de origem e pelo menos uma ação.",
    derivedSummary: "Criar coluna `{name}` a partir de `{source}`.",
    advancedOptions: "Opções avançadas",
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
    opRegex: "expressão regular",
    opIsBlank: "é branco ou vazio",
    opIsNotBlank: "não é branco nem vazio",
    operatorAriaLabel: "Operador: {symbol}, {meaning}",
    value: "Valor",
    finalValue: "Valor final",
    valueList: "Separe os valores com vírgula",
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
    reviewAndTryAgain: "Revise as informações acima e tente novamente.",
  },
  "en-US": {
    readyTitle: "Ready",
    readyText: "Choose an input file to begin.",
    inspecting: "Reading file...",
    validating: "Validating filter...",
    valid: "Filter is valid.",
    running: "Creating output file...",
    done: "Output file created.",
    error: "Something needs attention.",
    chooseCsv: "Choose an input file.",
    chooseOutput: "Choose a destination folder before continuing.",
    chooseOutputDirectory: "Choose the destination folder.",
    noColumns: "Choose a file to load columns.",
    droppedFileNeedsPicker: "Click the file area to choose from your computer and allow access to the full path.",
    noFile: "No file selected",
    columnsLoaded: "columns loaded.",
    columnSearchPlaceholder: "Search column",
    inputQueue: "Files in queue",
    outputName: "Output name",
    outputNamePlaceholder: "Optional",
    zipPasswords: "ZIP passwords",
    onePasswordPerLine: "One password per line",
    allExcelSheets: "Process all Excel sheets",
    reuseSchema: "Reuse the first file schema",
    deleteZipAfterExtract: "Delete ZIP after successful extraction",
    rowsWritten: "rows written.",
    progressTitle: "Progress",
    progressItem: "Item {index} of {total}",
    progressArtifactFiltered: "Filtered base",
    progressArtifactSummarization: "Summarization",
    progressArtifactOutput: "Output",
    progressPercentLabel: "{percent}% complete",
    progressIndeterminateLabel: "Running without a reliable percentage",
    bridgeNotReady: "The Python bridge is not ready yet.",
    bridgeWaiting: "Waiting for the Python bridge.",
    language: "Language",
    stepFile: "File",
    stepFilter: "Filter",
    stepDerived: "New columns",
    stepSummarization: "Summarization",
    stepOutput: "Output",
    stepRun: "Create",
    stepEyebrow: "Step {number}",
    chooseFile: "Choose the file",
    browseInput: "Choose file",
    dropStrong: "Click or drop the file here",
    dropHelp: "Press Enter or Space to choose from your computer.",
    fileLabel: "File",
    sizeLabel: "Size",
    columnsLabel: "Columns",
    readOptions: "Read options",
    encoding: "Encoding",
    delimiter: "Delimiter",
    nullValue: "Null value",
    emptyPlaceholder: "empty",
    buildFilter: "Build the filter",
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
    chooseOutputFolder: "Choose the output folder",
    chooseDestination: "Choose destination",
    chooseFolder: "Choose folder",
    routeModeTitle: "What do you want to create?",
    routeModeHelp: "Summarization means IDEA-style grouped data analysis with totals.",
    cleanBase: "Clean base",
    cleanBaseHelp: "Filter and save the clean base.",
    cleanThenSummarization: "Clean, then run summarization",
    cleanThenSummarizationHelp: "Save the clean base and the grouped summarization with totals.",
    summarizationOnly: "Run summarization only",
    summarizationOnlyHelp: "Create only the grouped summarization with totals.",
    summarization: "Generate summarization",
    summarizationOnlyOption: "Generate only summarization",
    summarizationGroupBy: "Group by",
    summarizationTotals: "Sum columns in summarization",
    summarizationColumnPlaceholder: "One column per line",
    summarizationSetupTitle: "Configure summarization",
    summarizationSetupHelp: "Choose grouping columns and numeric columns to total.",
    format: "Format",
    formatCsvTitle: "CSV",
    formatExcelTitle: "Excel",
    formatParquetTitle: "Parquet",
    saveAs: "Destination folder",
    saveToFolder: "Destination folder",
    chooseSavePlaceholder: "Choose a folder",
    chooseFolderPlaceholder: "Choose a folder",
    outputNamesTitle: "Names",
    cleanupOutputTitle: "Cleaned base",
    cleanupOutputHelp: "Choose the filtered base format.",
    summarizationOutputTitle: "Summarization",
    summarizationOutputHelp: "Choose the grouped summarization format.",
    generatedOutputNamesTitle: "File names",
    generatedOutputNamesHelp: "Edit only the base name. The format controls the extension.",
    outputNameSuffix: "Cleaned base suffix",
    outputNameStemPlaceholder: "Base name",
    resetOutputNames: "Reset generated names",
    defaultOutputSuffix: "_treated",
    summarizationOutputSuffix: "Summarization suffix",
    defaultSummarizationOutputSuffix: "_summarization",
    derivedColumnsTitle: "Create new columns",
    derivedColumnsHelp: "Optional: create cleaned columns from filtered columns.",
    addDerivedColumn: "Add column",
    noDerivedColumns: "No new column will be created.",
    saveConfig: "Save configuration",
    configSaved: "Configuration saved.",
    sourceColumn: "Source column",
    namePrefix: "Prefix",
    nameSuffix: "Suffix",
    nameSeparator: "Separator",
    prefixPlaceholder: "CLEAN",
    suffixPlaceholder: "FORMATTED",
    addTransformation: "Add transformation",
    removeDerivedColumn: "Remove column",
    removeTransformation: "Remove transformation",
    derivedPosition: "Position",
    positionAppend: "At the end of the table",
    positionBefore: "Before a column",
    positionAfter: "After a column",
    positionTarget: "Reference column",
    newColumn: "New column",
    derivedSummaryEmpty: "Choose the source column and at least one action.",
    derivedSummary: "Create column `{name}` from `{source}`.",
    advancedOptions: "Advanced options",
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
    opRegex: "regular expression",
    opIsBlank: "is blank or empty",
    opIsNotBlank: "is not blank or empty",
    operatorAriaLabel: "Operator: {symbol}, {meaning}",
    value: "Value",
    finalValue: "Final value",
    valueList: "Separate values with commas",
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
    reviewAndTryAgain: "Review the information above and try again.",
  },
};

function t(key) {
  return (text[state.language] || text["pt-BR"])[key] || key;
}

function byId(id) {
  return document.getElementById(id);
}

function numberedStepLabel(number, key) {
  return `${number}. ${t(key)}`;
}

function stepEyebrowLabel(number) {
  return t("stepEyebrow").replace("{number}", String(number));
}

function updateVisibleStepNumbers() {
  const visibleLinks = [];
  Array.from(document.querySelectorAll("[data-workflow-step]"))
    .filter((step) => !step.classList.contains("hidden"))
    .forEach((step, index) => {
      const number = index + 1;
      const link = document.querySelector(`.step-link[href="#${step.id}"]`);
      const eyebrow = step.querySelector("[data-step-eyebrow]");
      if (link) {
        link.textContent = numberedStepLabel(number, link.dataset.stepLabelKey);
        visibleLinks.push(link);
      }
      if (eyebrow) {
        eyebrow.textContent = stepEyebrowLabel(number);
      }
    });
  const activeLink = document.querySelector(".step-link.active");
  if (activeLink && activeLink.classList.contains("hidden")) {
    activeLink.classList.remove("active");
  }
  if (!visibleLinks.some((link) => link.classList.contains("active")) && visibleLinks[0]) {
    visibleLinks[0].classList.add("active");
  }
}

function setStatus(title, detail, variant = "idle") {
  byId("statusTitle").textContent = title;
  byId("statusText").textContent = detail;
  byId("statusDot").className = `status-dot ${variant}`;
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
    choose_output_file: bridgeUnavailableResponse,
    choose_output_directory: bridgeUnavailableResponse,
    choose_report_file: bridgeUnavailableResponse,
    choose_rejects_file: bridgeUnavailableResponse,
    save_config: bridgeUnavailableResponse,
    inspect_csv: bridgeUnavailableResponse,
    validate_filter: bridgeUnavailableResponse,
    start_filter_run: bridgeUnavailableResponse,
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
  state.outputNameTouchedIndexes = new Set();
  state.resolvedInputs = [];
  byId("inputPathText").textContent = state.inputPath || t("noFile");
  renderQueue();
  renderOutputNames();
  showInputWarnings([]);
}

function setOutputPath(path) {
  state.outputPath = path || "";
  byId("outputPathInput").value = state.outputPath;
}

function applyLanguage() {
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.setAttribute("placeholder", t(element.dataset.i18nPlaceholder));
  });
  document.querySelectorAll("[data-i18n-title]").forEach((element) => {
    element.setAttribute("title", t(element.dataset.i18nTitle));
  });
  if (!state.inputPath) {
    byId("inputPathText").textContent = t("noFile");
  }
  document.querySelectorAll(".filter-column").forEach((input) => updateColumnOptions(input));
  document.querySelectorAll(".filter-row").forEach(updateOperatorPicker);
  document.querySelectorAll(".derived-transform-row").forEach(updateTransformRow);
  document.querySelectorAll(".derived-column-card").forEach(updateDerivedCard);
  refreshOutputNameDefaults();
  syncSummarizationOutputSuffixField();
  updateFilterHint();
  updateSummarizationMode();
  refreshSummarizationColumnPickers();
  updateDerivedEmptyState();
}

function updateFilterHint() {
  const hasActiveRules = Array.from(document.querySelectorAll(".filter-row")).some(visualConditionIsComplete);
  byId("noFilterHint").classList.toggle("hidden", hasActiveRules);
}

function updateSummarizationMode() {
  const mode = routeMode();
  const summarize = mode !== "cleanBase";
  const cleanup = mode !== "summarizationOnly";
  const summarizationSection = byId("step-summarization");
  document.querySelectorAll(".route-card").forEach((card) => {
    const input = card.querySelector('input[name="routeMode"]');
    card.classList.toggle("active", input.checked);
  });
  summarizationSection.classList.toggle("hidden", !summarize);
  document.querySelectorAll(".summarization-only-section").forEach((element) => {
    element.classList.toggle("hidden", !summarize);
  });
  document.querySelectorAll(".cleanup-only-section, .cleanup-option").forEach((element) => {
    element.classList.toggle("hidden", !cleanup);
  });
  Array.from(summarizationSection.querySelectorAll("input")).forEach((field) => {
    field.disabled = !summarize;
  });
  document.querySelectorAll("#step-filter input, #step-filter select, #step-filter textarea, #step-filter button, .derived-section input, .derived-section select, .derived-section textarea, .derived-section button, .cleanup-option input, .cleanup-option select, .cleanup-option textarea").forEach((field) => {
    field.disabled = !cleanup;
  });
  updateVisibleStepNumbers();
}

function routeMode() {
  const mode = document.querySelector('input[name="routeMode"]:checked')?.value;
  return ["cleanBase", "cleanThenSummarization", "summarizationOnly"].includes(mode) ? mode : "cleanBase";
}

function setColumns(columns) {
  state.columns = columns || [];
  byId("columnCountText").textContent = state.columns.length ? String(state.columns.length) : "-";
  document.querySelectorAll(".filter-column").forEach((input) => updateColumnOptions(input));
  updateSummarizationMode();
  refreshSummarizationColumnPickers();
}

function renderQueue(inputs = state.resolvedInputs) {
  const panel = byId("queuePanel");
  const list = byId("queueList");
  const items = inputs && inputs.length ? inputs : state.inputPaths.map((path) => ({ label: path, format: "" }));
  list.innerHTML = "";
  if (!items.length) {
    panel.classList.add("hidden");
    return;
  }
  items.forEach((item, index) => {
    const row = document.createElement("div");
    row.className = "queue-item";
    const label = item.label || item.display_name || item.source_path || item.path;
    const meta = [item.format, item.excel_sheet ? `aba: ${item.excel_sheet}` : "", item.zip_source ? "ZIP" : ""]
      .filter(Boolean)
      .join(" · ");
    const title = document.createElement("strong");
    title.textContent = `${index + 1}. ${label}`;
    const metaText = document.createElement("span");
    metaText.textContent = meta;
    row.append(title, metaText);
    list.appendChild(row);
  });
  panel.classList.remove("hidden");
}

function outputItems(inputs = state.resolvedInputs) {
  return inputs && inputs.length ? inputs : state.inputPaths.map((path) => ({ label: path, format: "" }));
}

function extensionForFormat(format) {
  const suffixes = { csv: ".csv", xlsx: ".xlsx", parquet: ".parquet" };
  return suffixes[format] || ".csv";
}

function outputExtension() {
  return extensionForFormat(byId("formatSelect")?.value || "csv");
}

function summaryOutputExtension() {
  return extensionForFormat(byId("summaryFormatSelect")?.value || "xlsx");
}

function outputNameExtension() {
  return routeMode() === "summarizationOnly" ? summaryOutputExtension() : outputExtension();
}

function outputStemFromPath(path) {
  const leaf = String(path || "").split(/[\\/]/).filter(Boolean).pop() || "input";
  return leaf.replace(/\.(csv|xlsx|parquet|pq)$/i, "");
}

function safeOutputStem(value) {
  const withoutExtension = String(value || "").trim().replace(/\.(csv|xlsx|parquet)$/i, "");
  let safe = withoutExtension.replace(/[^A-Za-z0-9._-]+/g, "_").replace(/^[._-]+|[._-]+$/g, "");
  if (!safe) {
    safe = "input";
  }
  const reservedStem = safe.split(".")[0].toUpperCase();
  if (["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"].includes(reservedStem)) {
    safe = `input_${safe}`;
  }
  return safe;
}

function outputNameStemValue(value) {
  const text = String(value || "").trim();
  return text ? safeOutputStem(text) : "";
}

function outputBaseStem(item) {
  const source = item.display_name || outputStemFromPath(item.label || item.source_path || item.path);
  return safeOutputStem(item.excel_sheet ? `${source}_${item.excel_sheet}` : source);
}

function defaultOutputNames(items = outputItems()) {
  const suffix = routeMode() === "summarizationOnly"
    ? summarizationOutputSuffixValue()
    : state.outputNameSuffix || t("defaultOutputSuffix");
  const used = new Set();
  return items.map((item) => {
    const base = safeOutputStem(`${outputBaseStem(item)}${suffix}`);
    let candidate = base;
    let counter = 2;
    while (used.has(candidate.toLowerCase())) {
      candidate = `${base}_${String(counter).padStart(3, "0")}`;
      counter += 1;
    }
    used.add(candidate.toLowerCase());
    return candidate;
  });
}

function syncOutputSuffixField() {
  const suffixInput = byId("outputNameSuffixInput");
  if (suffixInput) {
    suffixInput.value = state.outputNameSuffix || t("defaultOutputSuffix");
    suffixInput.placeholder = t("defaultOutputSuffix");
  }
}

function summarizationOutputSuffixValue() {
  const value = (state.summarizationOutputSuffix || t("defaultSummarizationOutputSuffix")).trim();
  return value || t("defaultSummarizationOutputSuffix");
}

function syncSummarizationOutputSuffixField() {
  const suffixInput = byId("summarizationOutputSuffixInput");
  if (suffixInput) {
    suffixInput.value = state.summarizationOutputSuffix || t("defaultSummarizationOutputSuffix");
    suffixInput.placeholder = t("defaultSummarizationOutputSuffix");
  }
}

function refreshOutputNameDefaults(inputs = outputItems(), options = {}) {
  if (!inputs.length) {
    return;
  }
  if (options.resetSuffix || !state.outputNameSuffixTouched) {
    state.outputNameSuffix = t("defaultOutputSuffix");
  }
  syncOutputSuffixField();
  const defaults = defaultOutputNames(inputs);
  state.outputNames = defaults.map((name, index) => {
    if (options.resetNames || !state.outputNameTouchedIndexes.has(index)) {
      return name;
    }
    return outputNameStemValue(state.outputNames[index]) || name;
  });
  state.outputNames.length = inputs.length;
  state.outputNameTouchedIndexes = new Set(
    Array.from(state.outputNameTouchedIndexes).filter((index) => index < inputs.length),
  );
}

function resetOutputNamesToDefaults() {
  state.outputNameSuffixTouched = false;
  state.summarizationOutputSuffixTouched = false;
  state.summarizationOutputSuffix = t("defaultSummarizationOutputSuffix");
  state.outputNameTouchedIndexes = new Set();
  refreshOutputNameDefaults(outputItems(), { resetNames: true, resetSuffix: true });
  syncSummarizationOutputSuffixField();
  renderOutputNames();
}

function outputNamePreview(stem) {
  const mode = routeMode();
  if (mode === "summarizationOnly") {
    return `${t("summarizationOutputTitle")}: ${stem}${summaryOutputExtension()}`;
  }
  const cleanupName = `${stem}${outputExtension()}`;
  if (mode === "cleanThenSummarization") {
    const summaryStem = safeOutputStem(`${stem}${summarizationOutputSuffixValue()}`);
    return `${t("cleanupOutputTitle")}: ${cleanupName} · ${t("summarizationOutputTitle")}: ${summaryStem}${summaryOutputExtension()}`;
  }
  return `${t("cleanupOutputTitle")}: ${cleanupName}`;
}

function renderOutputNames(inputs = state.resolvedInputs) {
  const panel = byId("outputNamesPanel");
  const list = byId("outputNamesList");
  const items = inputs && inputs.length ? inputs : state.inputPaths.map((path) => ({ label: path, format: "" }));
  list.innerHTML = "";
  if (!items.length) {
    panel.classList.add("hidden");
    return;
  }
  refreshOutputNameDefaults(items);
  const extension = outputNameExtension();
  items.forEach((item, index) => {
    const label = document.createElement("label");
    label.className = "queue-output-name";
    const labelText = document.createElement("span");
    labelText.className = "output-source-label";
    labelText.textContent = `${index + 1}. ${item.label || item.display_name || item.source_path || item.path}`;
    const editor = document.createElement("div");
    editor.className = "output-name-editor";
    const input = document.createElement("input");
    input.type = "text";
    input.value = outputNameStemValue(state.outputNames[index] || item.output_name || "");
    input.placeholder = t("outputNameStemPlaceholder");
    const extensionBadge = document.createElement("span");
    extensionBadge.className = "output-extension-badge";
    extensionBadge.textContent = extension;
    const preview = document.createElement("span");
    preview.className = "output-name-preview";
    preview.textContent = outputNamePreview(input.value);
    input.addEventListener("input", () => {
      const rawValue = input.value;
      const withoutExtension = rawValue.replace(/\.(csv|xlsx|parquet)$/i, "");
      const extensionWasTyped = withoutExtension !== rawValue;
      const storedValue = extensionWasTyped ? outputNameStemValue(withoutExtension) : withoutExtension;
      if (extensionWasTyped) {
        input.value = storedValue;
      }
      state.outputNames[index] = storedValue;
      state.outputNameTouchedIndexes.add(index);
      preview.textContent = outputNamePreview(outputNameStemValue(storedValue));
      normalizeDestinationForOutputNames();
    });
    editor.append(input, extensionBadge);
    label.append(labelText, editor, preview);
    list.appendChild(label);
  });
  panel.classList.remove("hidden");
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

function updateColumnOptions(input, columns = state.columns) {
  prepareColumnSearch(input);
  const suggestions = input.parentElement.querySelector(".filter-column-suggestions");
  const current = input.value;
  suggestions.innerHTML = "";
  input.dataset.activeIndex = "-1";
  input.removeAttribute("aria-activedescendant");
  if (!columns.length) {
    input.disabled = true;
    input.placeholder = t("noColumns");
    closeColumnSuggestions(input);
    return;
  }

  input.disabled = false;
  input.placeholder = t("columnSearchPlaceholder");
  rankedColumns(current, columns).forEach((column) => {
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

function bindEnterFlow(column, onAccept = () => {}) {
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
      onAccept(column);
    } else if (event.key === "Escape") {
      closeColumnSuggestions(column);
    }
  });
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

function rankedColumns(query, columns = state.columns) {
  return columns
    .map((column, index) => ({ column, index, score: fuzzyScore(column, query) }))
    .filter((item) => item.score > Number.NEGATIVE_INFINITY)
    .sort((left, right) => right.score - left.score || left.index - right.index)
    .slice(0, 50)
    .map((item) => item.column);
}

function updateFilterRow(row) {
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
}

function filterOperatorNeedsValue(operator) {
  return !["is_null", "is_not_null", "is_empty", "is_not_empty", "is_blank", "is_not_blank"].includes(operator);
}

function addFilterRowAndFocus() {
  const row = addFilterRow();
  row.querySelector(".filter-column").focus();
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

function inferredTypeForCondition(operator, value) {
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

function operatorOption(operator) {
  return FILTER_OPERATOR_OPTIONS.find((option) => option.id === operator) || FILTER_OPERATOR_OPTIONS[0];
}

function operatorLabel(option) {
  return t(option.labelKey);
}

function operatorAriaLabel(option) {
  return t("operatorAriaLabel")
    .replace("{symbol}", option.symbol)
    .replace("{meaning}", operatorLabel(option));
}

function renderOperatorOptions(row) {
  const menu = row.querySelector(".operator-menu");
  const operator = row.querySelector(".filter-operator");
  menu.innerHTML = "";
  FILTER_OPERATOR_OPTIONS.forEach((option) => {
    const item = document.createElement("button");
    const symbol = document.createElement("span");
    item.type = "button";
    item.className = "operator-option";
    item.dataset.operator = option.id;
    item.setAttribute("role", "option");
    item.setAttribute("aria-selected", String(operator.value === option.id));
    item.setAttribute("aria-label", operatorAriaLabel(option));
    item.title = operatorLabel(option);
    symbol.className = "operator-option-symbol";
    symbol.textContent = option.symbol;
    item.append(symbol);
    item.addEventListener("click", () => chooseOperator(row, option.id));
    menu.appendChild(item);
  });
}

function updateOperatorPicker(row) {
  const operator = row.querySelector(".filter-operator");
  const trigger = row.querySelector(".operator-trigger");
  const symbol = row.querySelector(".operator-symbol");
  const label = row.querySelector(".operator-trigger-label");
  const menu = row.querySelector(".operator-menu");
  const option = operatorOption(operator.value);
  symbol.textContent = option.symbol;
  label.textContent = option.symbol;
  trigger.setAttribute("aria-label", operatorAriaLabel(option));
  trigger.title = operatorLabel(option);
  renderOperatorOptions(row);
  if (menu.classList.contains("hidden")) {
    trigger.setAttribute("aria-expanded", "false");
  }
}

function closeOperatorPicker(row) {
  const trigger = row.querySelector(".operator-trigger");
  const menu = row.querySelector(".operator-menu");
  menu.classList.add("hidden");
  trigger.setAttribute("aria-expanded", "false");
}

function closeOtherOperatorPickers(row) {
  document.querySelectorAll(".filter-row").forEach((otherRow) => {
    if (otherRow !== row) {
      closeOperatorPicker(otherRow);
    }
  });
}

function selectedOperatorButton(row) {
  const operator = row.querySelector(".filter-operator").value;
  return row.querySelector(`.operator-option[data-operator="${operator}"]`) || row.querySelector(".operator-option");
}

function moveOperatorFocus(row, step) {
  const options = Array.from(row.querySelectorAll(".operator-option"));
  const currentIndex = Math.max(0, options.indexOf(document.activeElement));
  const nextIndex = (currentIndex + step + options.length) % options.length;
  options[nextIndex].focus();
}

function openOperatorPicker(row, focusSelected = true) {
  const trigger = row.querySelector(".operator-trigger");
  const menu = row.querySelector(".operator-menu");
  closeOtherOperatorPickers(row);
  renderOperatorOptions(row);
  menu.classList.remove("hidden");
  trigger.setAttribute("aria-expanded", "true");
  if (focusSelected) {
    selectedOperatorButton(row).focus();
  }
}

function chooseOperator(row, operatorId) {
  const operator = row.querySelector(".filter-operator");
  operator.value = operatorId;
  updateOperatorPicker(row);
  closeOperatorPicker(row);
  operator.dispatchEvent(new Event("change", { bubbles: true }));
  row.querySelector(".operator-trigger").focus();
}

function bindOperatorPicker(row) {
  const pickerId = `operator-menu-${++state.operatorPickerId}`;
  const trigger = row.querySelector(".operator-trigger");
  const menu = row.querySelector(".operator-menu");
  menu.id = pickerId;
  menu.setAttribute("role", "listbox");
  trigger.setAttribute("aria-controls", pickerId);
  trigger.addEventListener("click", () => openOperatorPicker(row));
  trigger.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown" || event.key === "ArrowUp" || event.key === " ") {
      event.preventDefault();
      openOperatorPicker(row);
      if (event.key === "ArrowUp") {
        moveOperatorFocus(row, -1);
      }
      return;
    }
    if (event.key !== "Enter") {
      return;
    }
    event.preventDefault();
    if (filterOperatorNeedsValue(row.querySelector(".filter-operator").value)) {
      row.querySelector(".filter-value").focus();
    } else {
      addFilterRowAndFocus();
    }
  });
  menu.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      event.preventDefault();
      closeOperatorPicker(row);
      trigger.focus();
      return;
    }
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      moveOperatorFocus(row, event.key === "ArrowDown" ? 1 : -1);
      return;
    }
    if (event.key === "Home" || event.key === "End") {
      event.preventDefault();
      const options = row.querySelectorAll(".operator-option");
      options[event.key === "Home" ? 0 : options.length - 1].focus();
      return;
    }
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      chooseOperator(row, document.activeElement.dataset.operator);
    }
  });
  updateOperatorPicker(row);
}

function addFilterRow(initial = {}) {
  const template = byId("filterRowTemplate");
  const row = template.content.firstElementChild.cloneNode(true);
  const column = row.querySelector(".filter-column");
  const operator = row.querySelector(".filter-operator");
  const operatorButton = row.querySelector(".operator-trigger");
  const value = row.querySelector(".filter-value");
  const value2 = row.querySelector(".filter-value2");

  prepareColumnSearch(column);
  if (initial.column) column.value = initial.column;
  updateColumnOptions(column);
  if (initial.operator) operator.value = initial.operator;
  if (initial.value) value.value = initial.value;
  if (initial.value2) value2.value = initial.value2;
  bindOperatorPicker(row);

  column.addEventListener("focus", () => updateColumnOptions(column));
  column.addEventListener("input", () => {
    updateColumnOptions(column);
    updateFilterHint();
  });
  bindEnterFlow(column, () => {
    updateFilterHint();
    operatorButton.focus();
  });
  column.addEventListener("blur", () => {
    setTimeout(() => closeColumnSuggestions(column), 120);
  });
  column.addEventListener("change", updateFilterHint);
  operator.addEventListener("change", () => {
    updateFilterRow(row);
    updateFilterHint();
  });
  value.addEventListener("input", updateFilterHint);
  value2.addEventListener("input", updateFilterHint);
  value.addEventListener("keydown", (event) => {
    if (event.key !== "Enter") {
      return;
    }
    event.preventDefault();
    if (operator.value === "between" && value.value.trim()) {
      value2.focus();
    } else if (visualConditionIsComplete(row)) {
      addFilterRowAndFocus();
    }
  });
  value2.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && visualConditionIsComplete(row)) {
      event.preventDefault();
      addFilterRowAndFocus();
    }
  });
  row.querySelector(".remove-filter").addEventListener("click", () => {
    row.remove();
    updateFilterHint();
  });
  byId("filterRows").appendChild(row);
  applyLanguage();
  updateFilterRow(row);
  updateFilterHint();
  return row;
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
    ),
  }));
}

function formatDerivedName(source, prefix, suffix, separator) {
  if (!source) {
    return t("newColumn");
  }
  const before = prefix ? `${prefix}${separator && !prefix.endsWith(separator) ? separator : ""}` : "";
  const after = suffix ? `${separator && !suffix.startsWith(separator) ? separator : ""}${suffix}` : "";
  return `${before}${source}${after}`;
}

function visualDerivedColumns() {
  return Array.from(document.querySelectorAll(".derived-column-card")).map((card) => {
    const source = card.querySelector(".derived-source-column").value.trim();
    const prefix = card.querySelector(".derived-prefix").value.trim();
    const suffix = card.querySelector(".derived-suffix").value.trim();
    const separator = card.querySelector(".derived-separator").value;
    const mode = card.querySelector(".derived-position-mode").value;
    const target = card.querySelector(".derived-position-target").value.trim();
    const transforms = Array.from(card.querySelectorAll(".derived-transform-row")).map(transformPayload);
    return {
      source,
      name: { prefix, suffix, separator },
      position: { mode, target },
      transforms,
    };
  });
}

function uniqueColumnNames(columns) {
  const seen = new Set();
  return columns.filter((column) => {
    const name = String(column || "").trim();
    if (!name || seen.has(name)) {
      return false;
    }
    seen.add(name);
    return true;
  });
}

function projectedOutputColumns() {
  const renames = new Map(
    linesFromTextarea("renamesInput")
      .map((item) => {
        const separator = item.indexOf("=");
        if (separator < 0) {
          return [item.trim(), ""];
        }
        return [item.slice(0, separator).trim(), item.slice(separator + 1).trim()];
      })
      .filter(([source, output]) => source && output),
  );
  const selected = linesFromTextarea("selectColumnsInput");
  const baseColumns = selected.length ? selected : state.columns;
  return baseColumns.map((column) => renames.get(column) || column);
}

function derivedOutputNames() {
  return uniqueColumnNames(
    visualDerivedColumns()
      .filter((column) => column.source)
      .map((column) => formatDerivedName(column.source, column.name.prefix, column.name.suffix, column.name.separator)),
  );
}

function summaryColumnCandidates() {
  return uniqueColumnNames([...state.columns, ...projectedOutputColumns(), ...derivedOutputNames()]);
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

function outputNameItems() {
  const count = (state.resolvedInputs && state.resolvedInputs.length) || state.inputPaths.length;
  refreshOutputNameDefaults(outputItems());
  const extension = outputNameExtension();
  return Array.from({ length: count }, (_item, index) => {
    const stem = outputNameStemValue(state.outputNames[index] || "");
    return stem ? `${stem}${extension}` : "";
  });
}

function hasOutputNames() {
  return outputNameItems().some(Boolean);
}

function normalizeDestinationForOutputNames() {
  if (!hasOutputNames()) {
    return;
  }
  const path = byId("outputPathInput").value.trim();
  if (!/\.(csv|xlsx|parquet)$/i.test(path)) {
    return;
  }
  const separatorIndex = Math.max(path.lastIndexOf("\\"), path.lastIndexOf("/"));
  if (separatorIndex >= 0) {
    setOutputPath(path.slice(0, separatorIndex));
  }
}

function defaultFormatForCurrentInput() {
  const resolvedFormat = state.resolvedInputs[0]?.format;
  if (["csv", "xlsx", "parquet"].includes(resolvedFormat)) {
    return resolvedFormat;
  }
  const source = (state.resolvedInputs[0]?.source_path || state.inputPath || "").toLowerCase();
  if (source.endsWith(".xlsx")) {
    return "xlsx";
  }
  if (source.endsWith(".parquet") || source.endsWith(".pq")) {
    return "parquet";
  }
  return "csv";
}

function addDerivedColumn(initial = {}) {
  const template = byId("derivedColumnTemplate");
  const card = template.content.firstElementChild.cloneNode(true);
  state.derivedColumnId += 1;
  card.dataset.derivedId = String(state.derivedColumnId);
  const source = card.querySelector(".derived-source-column");
  const target = card.querySelector(".derived-position-target");
  [source, target].forEach((input) => bindColumnSearchInput(input, () => updateDerivedCard(card)));
  if (initial.source) source.value = initial.source;
  card.querySelector(".derived-prefix").value = initial.name?.prefix || "";
  card.querySelector(".derived-suffix").value = initial.name?.suffix || "";
  card.querySelector(".derived-separator").value = initial.name?.separator ?? "_";
  card.querySelector(".derived-position-mode").value = initial.position?.mode || "append";
  card.querySelector(".derived-position-target").value = initial.position?.target || "";
  card.querySelector(".remove-derived-column").addEventListener("click", () => {
    card.remove();
    updateDerivedEmptyState();
    refreshSummarizationColumnPickers();
  });
  card.querySelector(".add-derived-transform").addEventListener("click", () => addDerivedTransform(card));
  card.querySelectorAll(".derived-prefix, .derived-suffix, .derived-separator, .derived-position-mode").forEach((input) => {
    input.addEventListener("input", () => updateDerivedCard(card));
    input.addEventListener("change", () => updateDerivedCard(card));
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
    updateTransformRow(row);
    updateDerivedCard(card);
  });
  [value, extra].forEach((input) => input.addEventListener("input", () => updateDerivedCard(card)));
  row.querySelector(".remove-derived-transform").addEventListener("click", () => {
    row.remove();
    updateDerivedCard(card);
  });
  card.querySelector(".derived-transforms").appendChild(row);
  updateTransformRow(row);
  updateDerivedCard(card);
}

function updateTransformRow(row) {
  const operation = row.querySelector(".derived-transform-operation").value;
  const value = row.querySelector(".derived-transform-value");
  const extra = row.querySelector(".derived-transform-extra");
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
  value.classList.toggle("hidden", noValue);
  extra.classList.toggle("hidden", noValue || !["replace_text", "pad_left", "pad_right"].includes(operation));
  if (operation === "replace_text") {
    value.placeholder = t("transformValue");
    extra.placeholder = t("transformNewValue");
  } else if (["pad_left", "pad_right"].includes(operation)) {
    value.placeholder = t("transformCount");
    extra.placeholder = t("transformFill");
  } else if (["take_first", "take_last", "remove_first", "remove_last"].includes(operation)) {
    value.placeholder = t("transformCount");
  } else if (["extract_before", "extract_after"].includes(operation)) {
    value.placeholder = t("transformSeparator");
  } else if (operation === "default_if_blank") {
    value.placeholder = t("transformDefault");
  } else {
    value.placeholder = t("transformValue");
  }
}

function updateDerivedCard(card) {
  const source = card.querySelector(".derived-source-column").value.trim();
  const name = formatDerivedName(
    source,
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
  refreshSummarizationColumnPickers();
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
  bindEnterFlow(input, onChange);
  input.addEventListener("blur", () => {
    setTimeout(() => closeColumnSuggestions(input), 120);
  });
  input.addEventListener("change", onChange);
}

function selectedColumnPickerValues(id) {
  return Array.from(byId(id).querySelectorAll(".summarization-picker-chip")).map((chip) => chip.dataset.value).filter(Boolean);
}

function removeUnavailableSummarizationChips(container, candidates) {
  container.querySelectorAll(".summarization-picker-chip").forEach((chip) => {
    if (!candidates.has(chip.dataset.value)) {
      chip.remove();
    }
  });
}

function updateSummaryColumnOptions(input) {
  updateColumnOptions(input, summaryColumnCandidates());
  if (routeMode() === "cleanBase") {
    input.disabled = true;
    closeColumnSuggestions(input);
  }
}

function refreshSummarizationColumnPickers() {
  ["summarizationGroupByInput", "summarizationTotalsInput"].forEach((id) => {
    const container = byId(id);
    const candidates = new Set(summaryColumnCandidates());
    removeUnavailableSummarizationChips(container, candidates);
    updateSummaryColumnOptions(container.querySelector(".summarization-column-input"));
  });
}

function addSummarizationColumn(container, input) {
  const value = input.value.trim();
  const candidates = new Set(summaryColumnCandidates());
  if (!value || !candidates.has(value) || selectedColumnPickerValues(container.id).includes(value)) {
    input.value = "";
    updateSummaryColumnOptions(input);
    return;
  }
  const chip = document.createElement("button");
  chip.type = "button";
  chip.className = "summarization-picker-chip";
  chip.dataset.value = value;
  chip.textContent = value;
  chip.title = value;
  chip.addEventListener("click", () => chip.remove());
  container.querySelector(".summarization-picker-chips").appendChild(chip);
  input.value = "";
  updateSummaryColumnOptions(input);
}

function bindSummarizationColumnPicker(id) {
  const container = byId(id);
  const input = container.querySelector(".summarization-column-input");
  prepareColumnSearch(input);
  updateSummaryColumnOptions(input);
  input.addEventListener("focus", () => updateSummaryColumnOptions(input));
  input.addEventListener("input", () => updateSummaryColumnOptions(input));
  bindEnterFlow(input, () => addSummarizationColumn(container, input));
  input.addEventListener("blur", () => {
    setTimeout(() => closeColumnSuggestions(input), 120);
  });
  input.addEventListener("change", () => addSummarizationColumn(container, input));
}

function payload() {
  refreshSummarizationColumnPickers();
  normalizeDestinationForOutputNames();
  const format = byId("formatSelect").value;
  const rawFilter = byId("rawFilterInput").value.trim();
  const mode = routeMode();
  const summarize = mode === "cleanThenSummarization" || mode === "summarizationOnly";
  const summaryOnly = mode === "summarizationOnly";
  const cleanup = mode !== "summarizationOnly";
  const nullValue = byId("nullValueInput").value;
  const data = {
    input_path: state.inputPath,
    input_paths: state.inputPaths,
    output_path: byId("outputPathInput").value.trim(),
    output_names: outputNameItems(),
    avoid_existing_output_paths: true,
    summarization: summarize,
    summarization_only: summaryOnly,
    summarization_group_by: summarize ? selectedColumnPickerValues("summarizationGroupByInput") : [],
    summarization_totals: summarize ? selectedColumnPickerValues("summarizationTotalsInput") : [],
    summarization_output_suffix: summarize ? summarizationOutputSuffixValue() : "",
    summarization_output_format: summarize ? byId("summaryFormatSelect").value : "",
    filters:
      !cleanup
        ? { mode: "visual", combine: "and", conditions: [] }
        : state.filterMode === "advanced"
        ? { mode: "raw", raw: rawFilter }
        : { mode: "visual", combine: byId("combineSelect").value, conditions: visualConditions() },
    select: cleanup ? linesFromTextarea("selectColumnsInput") : [],
    renames: cleanup ? linesFromTextarea("renamesInput") : [],
    dedupe: cleanup && byId("dedupeInput").checked,
    dedupe_keys: cleanup ? linesFromTextarea("dedupeKeyInput") : [],
    sort: cleanup ? linesFromTextarea("sortInput") : [],
    case_insensitive_columns: byId("caseInsensitiveInput").checked,
    zip_passwords: linesFromTextarea("zipPasswordsInput"),
    all_excel_sheets: byId("allExcelSheetsInput").checked,
    reuse_schema: byId("reuseSchemaInput").checked,
    delete_zip_after_extract: byId("deleteZipInput").checked,
    report_path: byId("reportPathInput").value.trim(),
    rejects_path: byId("rejectsPathInput").value.trim(),
    csv_options: {
      encoding: byId("encodingInput").value.trim(),
      delimiter: byId("delimiterInput").value.trim(),
      null_values: nullValue ? [nullValue] : [],
    },
  };
  if (state.outputFormatExplicit) {
    data.output_format = format;
  }
  const derivedColumns = cleanup ? visualDerivedColumns() : [];
  if (derivedColumns.length) {
    data.derived_columns = derivedColumns;
  }
  return data;
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
    if (!state.outputFormatExplicit) {
      setOutputFormat(defaultFormatForCurrentInput(), false);
    }
    renderQueue();
    renderOutputNames();
    showInputWarnings(data.warnings || []);
    setColumns(data.columns);
    setStatus(t("readyTitle"), `${data.columns.length} ${t("columnsLoaded")}`, "done");
  } catch (error) {
    await maybePromptForZipPasswordAndRetryInspect(error);
  }
}

async function validateFilter() {
  if (!state.inputPath) {
    setStatus(t("error"), t("chooseCsv"), "error");
    return;
  }
  setStatus(t("readyTitle"), t("validating"), "running");
  showDetails("");
  const data = handleResponse(await state.api.validate_filter(payload()));
  setStatus(t("readyTitle"), t("valid"), "done");
  showDetails({ filtros: data.normalized_filters, sql: data.sql });
}

async function runFilter() {
  if (!state.inputPath) {
    setStatus(t("error"), t("chooseCsv"), "error");
    return;
  }
  if (!byId("outputPathInput").value.trim()) {
    setStatus(t("error"), t("chooseOutput"), "error");
    return;
  }
  setStatus(t("readyTitle"), t("running"), "running");
  showDetails("");
  showFriendlyError(null);
  resetResultCards();
  byId("runBtn").disabled = true;
  byId("openFolderBtn").classList.add("hidden");
  try {
    const data = handleResponse(await state.api.start_filter_run(payload()));
    updateJobStatus(data);
    pollJob(data.job_id);
  } catch (error) {
    const retried = await maybePromptForZipPasswordAndRetry(error);
    if (!retried) {
      byId("runBtn").disabled = false;
    }
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
  const field = byId("zipPasswordsInput");
  field.value = field.value ? `${field.value}\n${password}` : password;
  return true;
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
      updateJobStatus(data);
      if (!data.running) {
        clearInterval(state.pollTimer);
        byId("runBtn").disabled = false;
      }
    } catch (_error) {
      clearInterval(state.pollTimer);
      byId("runBtn").disabled = false;
    }
  }, 850);
}

function progressFromJob(job) {
  if (job && job.progress) {
    return job.progress;
  }
  if (!job || !job.phase) {
    return null;
  }
  return {
    phase: job.phase,
    label: phaseLabel(job.phase),
    input_index: null,
    input_total: null,
    input_name: "",
    artifact: null,
    percent: null,
    determinate: false,
    timeline: [],
  };
}

function progressItemText(progress) {
  if (!progress.input_index || !progress.input_total) {
    return "";
  }
  return t("progressItem")
    .replace("{index}", String(progress.input_index))
    .replace("{total}", String(progress.input_total));
}

function progressArtifactLabel(artifact) {
  const labels = {
    filtered: t("progressArtifactFiltered"),
    summarization: t("progressArtifactSummarization"),
  };
  return labels[artifact] || (artifact ? t("progressArtifactOutput") : "");
}

function progressStatusText(progress) {
  const details = [progress.input_name, progressArtifactLabel(progress.artifact)].filter(Boolean);
  if (progress.determinate && Number.isFinite(progress.percent)) {
    details.push(t("progressPercentLabel").replace("{percent}", String(progress.percent)));
  } else {
    details.push(t("progressIndeterminateLabel"));
  }
  return details.join(" · ");
}

function renderProgress(job) {
  const progress = progressFromJob(job);
  const panel = byId("progressPanel");
  if (!progress) {
    panel.classList.add("hidden");
    return;
  }
  const progressBar = byId("progressBar");
  const progressBarFill = byId("progressBarFill");
  const determinate = Boolean(progress.determinate && Number.isFinite(progress.percent));
  byId("progressPhaseText").textContent = progress.label || phaseLabel(progress.phase);
  byId("progressItemText").textContent = progressItemText(progress);
  byId("progressDetailText").textContent = progressStatusText(progress);
  progressBar.className = `progress-bar ${determinate ? "determinate" : "indeterminate"} ${progress.phase || ""}`;
  progressBar.setAttribute("aria-label", t("progressTitle"));
  if (determinate) {
    progressBar.setAttribute("aria-valuenow", String(progress.percent));
    progressBar.setAttribute("aria-valuetext", t("progressPercentLabel").replace("{percent}", String(progress.percent)));
    progressBarFill.style.transform = `scaleX(${Math.max(0, Math.min(100, Number(progress.percent))) / 100})`;
  } else {
    progressBar.removeAttribute("aria-valuenow");
    progressBar.setAttribute("aria-valuetext", t("progressIndeterminateLabel"));
    progressBarFill.style.transform = "";
  }
  renderProgressTimeline(progress.timeline || []);
  panel.classList.remove("hidden");
}

function renderProgressTimeline(timeline) {
  const list = byId("progressTimeline");
  list.innerHTML = "";
  timeline.slice(-6).forEach((entry) => {
    const item = document.createElement("li");
    const label = entry.label || phaseLabel(entry.phase);
    const meta = [progressItemText(entry), entry.input_name, progressArtifactLabel(entry.artifact)].filter(Boolean).join(" · ");
    item.className = entry.phase === "done" || entry.phase === "error" ? entry.phase : "";
    item.innerHTML = `<span><strong>${escapeHtml(label)}</strong>${meta ? `<br>${escapeHtml(meta)}` : ""}</span>`;
    list.appendChild(item);
  });
}

function updateJobStatus(job) {
  renderProgress(job);
  if (job.error) {
    setStatus(t("error"), job.error.message, "error");
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
    setStatus(t("readyTitle"), phaseLabel(job.phase), "running");
    return;
  }
  const report = job.report || {};
  state.outputPaths = report.output_paths || [];
  const failed = report.failed_inputs || (report.errors || []).length || 0;
  if (failed) {
    const message = state.outputPaths.length ? t("queuePartialDone") : t("queueAllFailed");
    setStatus(t("error"), message, "error");
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
  showResultCards(report);
  showDetails(report);
  if (state.outputPaths.length) {
    byId("openFolderBtn").classList.remove("hidden");
  }
}

function resetResultCards() {
  byId("progressPanel").classList.add("hidden");
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
    queue: state.language === "en-US" ? "Processing queue" : "Processando fila",
    inspecting: state.language === "en-US" ? "Reading file" : "Lendo arquivo",
    validating: state.language === "en-US" ? "Validating filter" : "Validando filtro",
    exporting: state.language === "en-US" ? "Creating output" : "Gerando saída",
    finishing: state.language === "en-US" ? "Finishing" : "Finalizando",
    done: state.language === "en-US" ? "Done" : "Concluído",
    error: state.language === "en-US" ? "Error" : "Erro",
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
  byId("visualTab").classList.toggle("active", mode === "visual");
  byId("advancedTab").classList.toggle("active", mode === "advanced");
  byId("visualFilterPanel").classList.toggle("hidden", mode !== "visual");
  byId("advancedFilterPanel").classList.toggle("hidden", mode !== "advanced");
}

function setOutputFormat(format, explicit = true) {
  state.outputFormatExplicit = explicit || state.outputFormatExplicit;
  byId("formatSelect").value = format;
  document.querySelectorAll("[data-format-card]").forEach((card) => {
    const active = card.dataset.formatCard === format;
    card.classList.toggle("active", active);
    card.setAttribute("aria-pressed", active ? "true" : "false");
  });
  if (state.outputFormatExplicit) {
    syncOutputSuffixWithFormat();
  }
  refreshOutputNameDefaults(outputItems());
  renderOutputNames();
}

function setSummaryOutputFormat(format) {
  byId("summaryFormatSelect").value = format;
  document.querySelectorAll("[data-summary-format-card]").forEach((card) => {
    const active = card.dataset.summaryFormatCard === format;
    card.classList.toggle("active", active);
    card.setAttribute("aria-pressed", active ? "true" : "false");
  });
  refreshOutputNameDefaults(outputItems());
  renderOutputNames();
}

function handleRouteModeChange() {
  updateSummarizationMode();
  refreshOutputNameDefaults(outputItems());
  renderOutputNames();
}

async function openInputPicker() {
  if (state.inputPickerOpen) {
    return;
  }
  state.inputPickerOpen = true;
  try {
    const data = handleResponse(await state.api.choose_input_files());
    const paths = data.paths && data.paths.length ? data.paths : data.path ? [data.path] : [];
    if (paths.length) {
      setInputPaths(paths);
      await inspectInput();
    }
  } finally {
    state.inputPickerOpen = false;
  }
}

function isInputPickerKey(event) {
  return event.key === "Enter" || event.key === " " || event.key === "Spacebar";
}

function syncOutputSuffixWithFormat() {
  const input = byId("outputPathInput");
  const path = input.value.trim();
  const format = byId("formatSelect").value;
  if (!path || hasOutputNames()) {
    return;
  }
  const expectedSuffix = outputExtension();
  if (/\.(csv|xlsx|parquet)$/i.test(path) && !path.toLowerCase().endsWith(expectedSuffix)) {
    setOutputPath(path.replace(/\.(csv|xlsx|parquet)$/i, expectedSuffix));
  }
}

function bindEvents() {
  if (state.eventsBound) {
    return;
  }
  state.eventsBound = true;

  byId("browseOutputBtn").addEventListener("click", async () => {
    const data = handleResponse(await state.api.choose_output_directory());
    if (data.path) setOutputPath(data.path);
  });

  byId("browseReportBtn").addEventListener("click", async () => {
    const data = handleResponse(await state.api.choose_report_file());
    if (data.path) byId("reportPathInput").value = data.path;
  });

  byId("browseRejectsBtn").addEventListener("click", async () => {
    const data = handleResponse(await state.api.choose_rejects_file());
    if (data.path) byId("rejectsPathInput").value = data.path;
  });

  byId("formatSelect").addEventListener("change", () => setOutputFormat(byId("formatSelect").value));
  document.querySelectorAll("[data-format-card]").forEach((card) => {
    card.addEventListener("click", () => setOutputFormat(card.dataset.formatCard));
  });

  byId("summaryFormatSelect").addEventListener("change", () => setSummaryOutputFormat(byId("summaryFormatSelect").value));
  document.querySelectorAll("[data-summary-format-card]").forEach((card) => {
    card.addEventListener("click", () => setSummaryOutputFormat(card.dataset.summaryFormatCard));
  });

  document.querySelectorAll('input[name="routeMode"]').forEach((input) => {
    input.addEventListener("change", handleRouteModeChange);
  });

  byId("addFilterBtn").addEventListener("click", () => addFilterRow());
  document.addEventListener("click", (event) => {
    if (!event.target.closest(".operator-picker")) {
      document.querySelectorAll(".filter-row").forEach(closeOperatorPicker);
    }
  });
  byId("addDerivedColumnBtn").addEventListener("click", () => addDerivedColumn());
  byId("selectColumnsInput").addEventListener("input", refreshSummarizationColumnPickers);
  byId("renamesInput").addEventListener("input", refreshSummarizationColumnPickers);
  byId("saveConfigBtn").addEventListener("click", async () => {
    const data = handleResponse(await state.api.save_config(payload()));
    if (data.path) {
      setStatus(t("readyTitle"), `${t("configSaved")} ${data.path}`, "done");
    }
  });
  byId("outputNameSuffixInput").addEventListener("input", (event) => {
    state.outputNameSuffix = event.target.value;
    state.outputNameSuffixTouched = true;
    refreshOutputNameDefaults(outputItems());
    renderOutputNames();
  });
  byId("summarizationOutputSuffixInput").addEventListener("input", (event) => {
    state.summarizationOutputSuffix = event.target.value;
    state.summarizationOutputSuffixTouched = true;
    if (routeMode() === "summarizationOnly") {
      refreshOutputNameDefaults(outputItems());
    }
    renderOutputNames();
  });
  byId("resetOutputNamesBtn").addEventListener("click", resetOutputNamesToDefaults);
  byId("visualTab").addEventListener("click", () => setFilterMode("visual"));
  byId("advancedTab").addEventListener("click", () => setFilterMode("advanced"));
  byId("checkExpressionBtn").addEventListener("click", validateFilter);
  byId("runBtn").addEventListener("click", runFilter);
  byId("resetBtn").addEventListener("click", () => window.location.reload());
  bindSummarizationColumnPicker("summarizationGroupByInput");
  bindSummarizationColumnPicker("summarizationTotalsInput");

  byId("openFolderBtn").addEventListener("click", async () => {
    const firstPath = state.outputPaths[0] || byId("outputPathInput").value;
    if (firstPath) handleResponse(await state.api.open_output_folder(firstPath));
  });

  byId("languageSelect").addEventListener("change", async (event) => {
    state.language = event.target.value;
    await state.api.set_language(state.language);
    applyLanguage();
    renderOutputNames();
    setStatus(t("readyTitle"), t("readyText"));
  });

  const dropZone = byId("dropZone");
  dropZone.addEventListener("click", async () => {
    await openInputPicker();
  });
  dropZone.addEventListener("keydown", async (event) => {
    if (!isInputPickerKey(event) || event.repeat) {
      return;
    }
    event.preventDefault();
    await openInputPicker();
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
      document.querySelectorAll(".step-link").forEach((item) => item.classList.remove("active"));
      link.classList.add("active");
    });
  });
  setOutputFormat(byId("formatSelect").value || "csv", false);
  setSummaryOutputFormat(byId("summaryFormatSelect").value || "xlsx");
  updateSummarizationMode();
  updateDerivedEmptyState();
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
