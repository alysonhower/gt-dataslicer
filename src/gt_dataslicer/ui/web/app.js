const state = {
  api: null,
  inputPath: "",
  inputPaths: [],
  outputPath: "",
  outputPaths: [],
  outputNames: [],
  resolvedInputs: [],
  columns: [],
  language: "pt-BR",
  filterMode: "visual",
  pollTimer: null,
  columnSuggestionListId: 0,
  eventsBound: false,
  derivedColumnId: 0,
};

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
    chooseOutput: "Escolha onde salvar o resultado.",
    noColumns: "Escolha um arquivo para carregar as colunas.",
    droppedFileNeedsPicker: "Use o botão Procurar arquivo para garantir acesso ao caminho completo do arquivo.",
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
    formatExcelTitle: "Excel",
    formatParquetTitle: "Parquet",
    saveAs: "Salvar em",
    chooseSavePlaceholder: "Escolha onde salvar",
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
    derivedSummaryEmpty: "Escolha uma coluna de origem e uma transformação.",
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
    opIsNull: "é nulo",
    opIsNotNull: "não é nulo",
    opIsEmpty: "é vazio",
    opIsNotEmpty: "não é vazio",
    opIsBlank: "é branco",
    opIsNotBlank: "não é branco",
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
    chooseOutput: "Choose where to save the result.",
    noColumns: "Choose a file to load columns.",
    droppedFileNeedsPicker: "Use Browse file so the app can access the full file path.",
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
    formatExcelTitle: "Excel",
    formatParquetTitle: "Parquet",
    saveAs: "Save as",
    chooseSavePlaceholder: "Choose where to save",
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
    derivedSummaryEmpty: "Choose a source column and a transformation.",
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
    opIsNull: "is null",
    opIsNotNull: "is not null",
    opIsEmpty: "is empty",
    opIsNotEmpty: "is not empty",
    opIsBlank: "is blank",
    opIsNotBlank: "is not blank",
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
  state.resolvedInputs = [];
  byId("inputPathText").textContent = state.inputPath || t("noFile");
  renderQueue();
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
  document.querySelectorAll(".derived-transform-row").forEach(updateTransformRow);
  document.querySelectorAll(".derived-column-card").forEach(updateDerivedCard);
  updateFilterHint();
  updateSummaryMode();
  updateDerivedEmptyState();
}

function updateFilterHint() {
  const hasActiveRules = Array.from(document.querySelectorAll(".filter-row")).some(visualConditionIsComplete);
  byId("noFilterHint").classList.toggle("hidden", hasActiveRules);
}

function updateSummaryMode() {
  const summarize = byId("summarizeInput").checked;
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
}

function setColumns(columns) {
  state.columns = columns || [];
  byId("columnCountText").textContent = state.columns.length ? String(state.columns.length) : "-";
  document.querySelectorAll(".filter-column").forEach((input) => updateColumnOptions(input));
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
    row.append(title, metaText, outputLabel);
    list.appendChild(row);
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
  column.addEventListener("change", updateFilterHint);
  operator.addEventListener("change", () => {
    updateFilterRow(row);
    updateFilterHint();
  });
  value.addEventListener("input", updateFilterHint);
  value2.addEventListener("input", updateFilterHint);
  row.querySelector(".remove-filter").addEventListener("click", () => {
    row.remove();
    updateFilterHint();
  });
  byId("filterRows").appendChild(row);
  applyLanguage();
  updateFilterRow(row);
  updateFilterHint();
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
  return Array.from({ length: count }, (_item, index) => (state.outputNames[index] || "").trim());
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
  return {
    input_path: state.inputPath,
    input_paths: state.inputPaths,
    output_path: byId("outputPathInput").value.trim(),
    output_format: format,
    output_names: outputNameItems(),
    summarize,
    summary_only: summaryOnly,
    summary_group_by: linesFromTextarea("summaryGroupByInput"),
    summary_totals: linesFromTextarea("summaryTotalsInput"),
    filters:
      state.filterMode === "advanced"
        ? { mode: "raw", raw: rawFilter }
        : { mode: "visual", combine: byId("combineSelect").value, conditions: visualConditions() },
    select: linesFromTextarea("selectColumnsInput"),
    derived_columns: visualDerivedColumns(),
    renames: linesFromTextarea("renamesInput"),
    dedupe: byId("dedupeInput").checked,
    dedupe_keys: linesFromTextarea("dedupeKeyInput"),
    sort: linesFromTextarea("sortInput"),
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

function updateJobStatus(job) {
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

function setOutputFormat(format) {
  byId("formatSelect").value = format;
  document.querySelectorAll("[data-format-card]").forEach((card) => {
    const active = card.dataset.formatCard === format;
    card.classList.toggle("active", active);
    card.setAttribute("aria-pressed", active ? "true" : "false");
  });
  syncOutputSuffixWithFormat();
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

  byId("browseInputBtn").addEventListener("click", async () => {
    const data = handleResponse(await state.api.choose_input_files());
    const paths = data.paths && data.paths.length ? data.paths : data.path ? [data.path] : [];
    if (paths.length) {
      setInputPaths(paths);
      await inspectInput();
    }
  });

  byId("browseOutputBtn").addEventListener("click", async () => {
    const data = handleResponse(await state.api.choose_output_file(byId("formatSelect").value));
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

  byId("addFilterBtn").addEventListener("click", () => addFilterRow());
  byId("addDerivedColumnBtn").addEventListener("click", () => addDerivedColumn());
  byId("saveConfigBtn").addEventListener("click", async () => {
    const data = handleResponse(await state.api.save_config(payload()));
    if (data.path) {
      setStatus(t("readyTitle"), `${t("configSaved")} ${data.path}`, "done");
    }
  });
  byId("visualTab").addEventListener("click", () => setFilterMode("visual"));
  byId("advancedTab").addEventListener("click", () => setFilterMode("advanced"));
  byId("checkExpressionBtn").addEventListener("click", validateFilter);
  byId("runBtn").addEventListener("click", runFilter);
  byId("resetBtn").addEventListener("click", () => window.location.reload());
  byId("summarizeInput").addEventListener("change", updateSummaryMode);
  byId("summaryOnlyInput").addEventListener("change", () => {
    if (byId("summaryOnlyInput").checked) {
      byId("summarizeInput").checked = true;
    }
    updateSummaryMode();
  });

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
  setOutputFormat(byId("formatSelect").value || "csv");
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
