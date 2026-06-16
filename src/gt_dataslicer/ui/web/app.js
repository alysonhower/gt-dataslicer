const state = {
  api: null,
  inputPath: "",
  outputPath: "",
  outputPaths: [],
  columns: [],
  language: "pt-BR",
  filterMode: "visual",
  pollTimer: null,
};

const text = {
  "pt-BR": {
    readyTitle: "Pronto",
    readyText: "Escolha um arquivo CSV para começar.",
    inspecting: "Lendo o arquivo...",
    validating: "Validando filtro...",
    valid: "Filtro válido.",
    running: "Gerando o arquivo...",
    done: "Arquivo gerado com sucesso.",
    error: "Algo precisa de atenção.",
    chooseCsv: "Escolha um CSV.",
    chooseOutput: "Escolha onde salvar o resultado.",
    noColumns: "Escolha um arquivo para carregar as colunas.",
    droppedFileNeedsPicker: "Use o botão Procurar CSV para garantir acesso ao caminho completo do arquivo.",
    noFile: "Nenhum arquivo escolhido",
    columnsLoaded: "colunas carregadas.",
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
    browseCsv: "Procurar CSV",
    dropStrong: "Arraste o CSV aqui",
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
    validateFilter: "Validar filtro",
    chooseOutputTitle: "Escolha a saída",
    chooseDestination: "Escolher destino",
    format: "Formato",
    saveAs: "Salvar em",
    chooseSavePlaceholder: "Escolha onde salvar",
    excelNotice: "Arquivos Excel têm limite de linhas por aba. Se o resultado for muito grande, o DataSlicer dividirá em abas ou arquivos conforme as opções.",
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
    opIn: "está na lista",
    opNotIn: "não está na lista",
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
    valueList: "valor1, valor2",
    typeText: "texto",
    typeNumber: "número",
    typeDate: "data",
    typeBool: "lógico",
    removeRule: "Remover regra",
  },
  "en-US": {
    readyTitle: "Ready",
    readyText: "Choose a CSV file to begin.",
    inspecting: "Reading file...",
    validating: "Validating filter...",
    valid: "Filter is valid.",
    running: "Creating output file...",
    done: "Output file created.",
    error: "Something needs attention.",
    chooseCsv: "Choose a CSV file.",
    chooseOutput: "Choose where to save the result.",
    noColumns: "Choose a file to load columns.",
    droppedFileNeedsPicker: "Use Browse CSV so the app can access the full file path.",
    noFile: "No file selected",
    columnsLoaded: "columns loaded.",
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
    browseCsv: "Browse CSV",
    dropStrong: "Drop the CSV here",
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
    validateFilter: "Validate filter",
    chooseOutputTitle: "Choose the output",
    chooseDestination: "Choose destination",
    format: "Format",
    saveAs: "Save as",
    chooseSavePlaceholder: "Choose where to save",
    excelNotice: "Excel files have row limits per sheet. If the result is very large, DataSlicer will split it across sheets or files according to the options.",
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
    opIn: "is in list",
    opNotIn: "is not in list",
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
    valueList: "value1, value2",
    typeText: "text",
    typeNumber: "number",
    typeDate: "date",
    typeBool: "boolean",
    removeRule: "Remove rule",
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
  const details = byId("detailsBox");
  if (!value) {
    details.classList.add("hidden");
    details.textContent = "";
    return;
  }
  details.textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  details.classList.remove("hidden");
}

function handleResponse(response) {
  if (response && response.ok) {
    return response.data;
  }
  const error = response && response.error ? response.error : { message: t("error") };
  setStatus(t("error"), error.message, "error");
  showDetails(error.details || error);
  throw new Error(error.message);
}

function linesFromTextarea(id) {
  return byId(id)
    .value.split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function setInputPath(path) {
  state.inputPath = path || "";
  byId("inputPathText").textContent = state.inputPath || t("noFile");
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
  updateFilterHint();
}

function updateFilterHint() {
  const hasActiveRules = Array.from(document.querySelectorAll(".filter-row")).some(visualConditionIsComplete);
  byId("noFilterHint").classList.toggle("hidden", hasActiveRules);
}

function setColumns(columns) {
  state.columns = columns || [];
  byId("columnCountText").textContent = state.columns.length ? String(state.columns.length) : "-";
  document.querySelectorAll(".filter-column").forEach((select) => populateColumnSelect(select));
}

function populateColumnSelect(select) {
  const current = select.value;
  select.innerHTML = "";
  if (!state.columns.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = t("noColumns");
    select.appendChild(option);
    return;
  }
  state.columns.forEach((column) => {
    const option = document.createElement("option");
    option.value = column;
    option.textContent = column;
    select.appendChild(option);
  });
  if (current && state.columns.includes(current)) {
    select.value = current;
  }
}

function updateFilterRow(row) {
  const operator = row.querySelector(".filter-operator").value;
  const value = row.querySelector(".filter-value");
  const value2 = row.querySelector(".filter-value2");
  const type = row.querySelector(".filter-type");
  const noValue = ["is_null", "is_not_null", "is_empty", "is_not_empty", "is_blank", "is_not_blank"].includes(operator);
  const between = operator === "between";
  if (row.dataset.typeTouched !== "true") {
    type.value = defaultTypeForOperator(operator);
  }
  row.classList.toggle("no-value", noValue);
  row.classList.toggle("is-between", between && !noValue);
  value.classList.toggle("hidden", noValue);
  type.classList.toggle("hidden", noValue);
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

function defaultTypeForOperator(operator) {
  if (["gt", "gte", "lt", "lte"].includes(operator)) {
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
  const valueType = row.querySelector(".filter-type");

  populateColumnSelect(column);
  if (initial.column) column.value = initial.column;
  if (initial.operator) operator.value = initial.operator;
  if (initial.value) value.value = initial.value;
  if (initial.value2) value2.value = initial.value2;
  if (initial.value_type) {
    valueType.value = initial.value_type;
    row.dataset.typeTouched = "true";
  }

  column.addEventListener("change", updateFilterHint);
  operator.addEventListener("change", () => {
    updateFilterRow(row);
    updateFilterHint();
  });
  value.addEventListener("input", updateFilterHint);
  value2.addEventListener("input", updateFilterHint);
  valueType.addEventListener("change", () => {
    row.dataset.typeTouched = "true";
  });
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
    value_type: row.querySelector(".filter-type").value,
  }));
}

function payload() {
  const format = byId("formatSelect").value;
  const rawFilter = byId("rawFilterInput").value.trim();
  const nullValue = byId("nullValueInput").value;
  return {
    input_path: state.inputPath,
    output_path: byId("outputPathInput").value.trim(),
    output_format: format,
    filters:
      state.filterMode === "advanced"
        ? { mode: "raw", raw: rawFilter }
        : { mode: "visual", combine: byId("combineSelect").value, conditions: visualConditions() },
    select: linesFromTextarea("selectColumnsInput"),
    renames: linesFromTextarea("renamesInput"),
    dedupe: byId("dedupeInput").checked,
    dedupe_keys: linesFromTextarea("dedupeKeyInput"),
    sort: linesFromTextarea("sortInput"),
    case_insensitive_columns: byId("caseInsensitiveInput").checked,
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
  const data = handleResponse(await state.api.inspect_csv(payload()));
  byId("inputSizeText").textContent = formatBytes(data.size_bytes);
  setColumns(data.columns);
  setStatus(t("readyTitle"), `${data.columns.length} ${t("columnsLoaded")}`, "done");
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
  byId("runBtn").disabled = true;
  byId("openFolderBtn").classList.add("hidden");
  try {
    const data = handleResponse(await state.api.start_filter_run(payload()));
    pollJob(data.job_id);
  } catch (_error) {
    byId("runBtn").disabled = false;
  }
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
    showDetails(job.error.details || job.error);
    return;
  }
  if (job.running) {
    setStatus(t("readyTitle"), phaseLabel(job.phase), "running");
    return;
  }
  const report = job.report || {};
  state.outputPaths = report.output_paths || [];
  setStatus(t("readyTitle"), `${t("done")} ${report.output_rows || 0} ${t("rowsWritten")}`, "done");
  showDetails(report);
  if (state.outputPaths.length) {
    byId("openFolderBtn").classList.remove("hidden");
  }
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

function syncOutputSuffixWithFormat() {
  const input = byId("outputPathInput");
  const path = input.value.trim();
  const format = byId("formatSelect").value;
  if (!path) {
    return;
  }
  const expectedSuffix = format === "xlsx" ? ".xlsx" : ".csv";
  if (/\.(csv|xlsx)$/i.test(path) && !path.toLowerCase().endsWith(expectedSuffix)) {
    setOutputPath(path.replace(/\.(csv|xlsx)$/i, expectedSuffix));
  }
}

function bindEvents() {
  byId("browseInputBtn").addEventListener("click", async () => {
    const data = handleResponse(await state.api.choose_input_csv());
    if (data.path) {
      setInputPath(data.path);
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

  byId("formatSelect").addEventListener("change", () => {
    byId("excelNotice").classList.toggle("hidden", byId("formatSelect").value !== "xlsx");
    syncOutputSuffixWithFormat();
  });

  byId("addFilterBtn").addEventListener("click", () => addFilterRow());
  byId("visualTab").addEventListener("click", () => setFilterMode("visual"));
  byId("advancedTab").addEventListener("click", () => setFilterMode("advanced"));
  byId("validateBtn").addEventListener("click", validateFilter);
  byId("runBtn").addEventListener("click", runFilter);
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
  dropZone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropZone.classList.add("dragging");
  });
  dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragging"));
  dropZone.addEventListener("drop", async (event) => {
    event.preventDefault();
    dropZone.classList.remove("dragging");
    const file = event.dataTransfer.files[0];
    const path = file && (file.path || file.pywebviewFullPath);
    if (path) {
      setInputPath(path);
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
}

async function initialize() {
  if (!window.pywebview || !window.pywebview.api) {
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
      setStatus("Pywebview", t("bridgeWaiting"), "running");
    }
  }, 600);
});
