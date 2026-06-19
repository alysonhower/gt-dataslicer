from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP_JS = ROOT / "src" / "gt_dataslicer" / "ui" / "web" / "app.js"
INDEX_HTML = ROOT / "src" / "gt_dataslicer" / "ui" / "web" / "index.html"
STYLES_CSS = ROOT / "src" / "gt_dataslicer" / "ui" / "web" / "styles.css"


def test_browser_app_does_not_prefer_stale_raw_filter_in_visual_mode() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert 'state.filterMode === "advanced" || rawFilter' not in script
    assert 'state.filterMode === "advanced"' in script


def test_browser_app_summarizes_inactive_filter_mode_edits() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert "stepFilterVisualWithInactiveAdvanced" in script
    assert "stepFilterNoRulesWithInactiveAdvanced" in script
    assert "stepFilterAdvancedWithInactiveVisual" in script
    assert "stepFilterNoAdvancedWithInactiveVisual" in script
    assert "function inactiveVisualRulesExist()" in script
    assert "function inactiveAdvancedFilterExists()" in script
    assert 'state.filterMode === "visual"' in script
    assert 'state.filterMode === "advanced"' in script
    assert "advanced inactive" in script
    assert "visual inactive" in script


def test_browser_app_recovers_run_button_after_start_error() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert "function setRunControlsRunning(running, options = {})" in script
    assert "setRunControlsRunning(true)" in script
    assert "catch (_error)" in script
    assert "setRunControlsRunning(false)" in script


def test_browser_app_exposes_cancel_control_for_running_jobs() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")

    assert "cancelRunBtn" in markup
    assert "data-i18n=\"cancelRun\"" in markup
    assert "cancel_job: bridgeUnavailableResponse" in script
    assert "function cancelCurrentJob()" in script
    assert "state.api.cancel_job(state.activeJobId)" in script
    assert "function setRunControlsCanceling()" in script
    assert "setRunControlsRunning(true, { canCancel: false })" in script
    start_run_section = script[script.index("async function startRun(runPayload)") : script.index("async function runFilter()")]
    assert "state.activeJobId = data.job_id" in start_run_section
    assert "setRunControlsRunning(true)" in start_run_section
    assert "job.phase === \"cancelled\"" in script
    assert "cancel_requested" in script
    assert "closeBlocked" in script
    assert "function notifyCloseBlocked()" in script
    assert "window.dataslicerNotifyCloseBlocked = notifyCloseBlocked" in script
    assert "A run is still in progress. Cancel it or wait for it to finish before closing." in script


def test_browser_app_has_translation_hooks_for_static_text() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")

    assert "data-i18n=\"chooseFile\"" in markup
    assert "data-i18n=\"browseInput\"" in markup
    assert "data-i18n-placeholder=\"chooseSavePlaceholder\"" in markup
    assert "data-i18n-aria-label=\"format\"" in markup
    assert "data-i18n-aria-label=\"chooseReport\"" in markup
    assert "data-i18n-aria-label=\"chooseRejects\"" in markup
    assert "data-i18n-aria-label=\"chooseLookup\"" in markup
    assert "data-i18n-aria-label=\"removeRule\"" in markup
    assert "data-i18n-aria-label=\"removeLookup\"" in markup
    assert "data-i18n-aria-label=\"removeDerivedColumn\"" in markup
    assert "data-i18n-aria-label=\"removeTransformation\"" in markup
    assert "styles.css?v=" in markup
    assert "app.js?v=" in markup
    assert "function applyLanguage()" in script
    assert "document.documentElement.lang = state.language" in script
    assert "document.querySelectorAll(\"[data-i18n]\")" in script
    assert "document.querySelectorAll(\"[data-i18n-aria-label]\")" in script
    assert "document.querySelectorAll(\"[data-i18n-label]\")" in script


def test_browser_app_surfaces_input_resolution_warnings() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert "inputWarningsPanel" in markup
    assert "inputWarningsList" in markup
    assert "function showInputWarnings(warnings = [])" in script
    assert "showInputWarnings(data.warnings || [])" in script
    assert "showInputWarnings([])" in script
    assert ".input-warnings" in styles


def test_browser_app_shows_contextual_input_read_options() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")

    assert 'id="readOptionsDetails"' in markup
    assert 'data-input-option-group="csv"' in markup
    assert 'data-input-option-group="excel"' in markup
    assert 'data-input-option-group="zip"' in markup
    assert 'data-input-option-group="queue"' in markup
    assert "function currentInputKinds()" in script
    assert "function updateInputOptionVisibility()" in script
    assert 'byId("readOptionsDetails").classList.toggle("hidden", !hasInput)' in script
    assert 'group.querySelectorAll("button, input, textarea, select").forEach((control) => {' in script
    assert "control.disabled = !visible" in script
    assert 'format === "zip"' in script
    assert 'kinds.add("csv")' in script
    assert 'kinds.add("excel")' in script
    assert 'zip_passwords: hasZipOptions ? [...state.zipPasswords] : []' in script
    assert 'all_excel_sheets: hasExcelOptions && byId("allExcelSheetsInput").checked' in script
    assert 'reuse_schema: hasQueueOptions && byId("reuseSchemaInput").checked' in script
    assert 'delete_zip_after_extract: hasZipOptions && byId("deleteZipInput").checked' in script
    assert "csv_options: hasCsvOptions" in script


def test_browser_app_exposes_explicit_workflow_step_state() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert 'data-step-link="file"' in markup
    assert 'data-step-summary="run"' in markup
    assert 'aria-current="step"' in markup
    assert "function updateWorkflowSteps()" in script
    assert "function currentRunStep(fileStep, filterStep, outputStep)" in script
    assert "function markSetupChanged()" in script
    assert "setRunStep(\"done\", t(\"stepRunDone\"))" in script
    assert "stepRunBlocked" in script
    assert "link.dataset.stepState = stateName" in script
    assert '.step-link[data-step-state="error"]' in styles
    assert ".step-summary" in styles


def test_browser_app_surfaces_queue_schema_mismatches() -> None:
    script = APP_JS.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert "schemaMismatch" in script
    assert "schemaMismatchShort" in script
    assert "item.schema_matches_first === false" in script
    assert "queue-schema-warning" in script
    assert "data.schema_compatible === false" in script
    assert ".queue-schema-warning" in styles


def test_browser_app_infers_value_type_without_showing_type_field() -> None:
    script = APP_JS.read_text(encoding="utf-8")
    markup = INDEX_HTML.read_text(encoding="utf-8")

    assert "filter-type" not in markup
    assert "columnTypes: {}" in script
    assert "function semanticColumnType(column)" in script
    assert "const FILTER_OPERATORS_BY_TYPE" in script
    assert "function refreshFilterOperatorOptions(row)" in script
    assert "function updateFilterValueInputTypes(row)" in script
    assert 'numeric: ["equals", "not_equals", "gt", "gte", "lt", "lte", "in", "not_in", "between", "is_null", "is_not_null"]' in script
    assert 'boolean: ["equals", "not_equals", "is_null", "is_not_null"]' in script
    assert "function inferredTypeForCondition(operator, value, column)" in script
    assert 'semanticType === "date"' in script
    assert 'semanticType === "boolean"' in script
    assert '[\"gt\", \"gte\", \"lt\", \"lte\"].includes(operator)' in script
    assert 'operator === "between"' in script
    assert 'return "auto";' in script
    assert r"\d{4}-\d{2}-\d{2}(?:[T ][0-2]\d:[0-5]\d" in script
    assert 'return "string";' in script
    assert "/^-?(?:\\d+(?:\\.\\d*)?|\\.\\d+)$/.test(text)" not in script
    assert "value_type: inferredTypeForCondition(" in script
    assert "setColumns(data.columns, data.types || {})" in script
    assert 'row.querySelector(".filter-operator").value' in script
    assert 'row.querySelector(".filter-value").value' in script
    assert 'row.querySelector(".filter-column").value' in script


def test_browser_app_syncs_output_suffix_when_format_changes() -> None:
    script = APP_JS.read_text(encoding="utf-8")
    markup = INDEX_HTML.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert "function syncOutputSuffixWithFormat()" in script
    assert "function outputNeedsFolder()" in script
    assert "return count > 1;" in script
    assert "choose_output_file(byId(\"formatSelect\").value, outputNeedsFolder())" in script
    assert "function splitXlsxCanCreateMultipleFiles()" in script
    assert '["files", "both"].includes(state.outputSplitMode)' in script
    assert "function splitXlsxOutputPattern()" in script
    assert "function updateOutputArtifactNotice()" in script
    assert "splitXlsxNotice" in markup
    assert "splitXlsxNoticeTitle" in markup
    assert "splitXlsxNoticeText" in script
    assert ".output-artifact-notice" in styles
    assert "outputMaxRowsPerSheet" in script
    assert "outputSheetsPerFile" in script
    assert "state.outputSplitMode" in script
    assert "split_mode: state.outputSplitMode" in script
    assert "/\\.(csv|xlsx|parquet)$/i.test(path)" in script
    assert 'parquet: ".parquet"' in script
    assert "syncOutputSuffixWithFormat();" in script
    assert 'data-format-card="csv"' in markup
    assert 'data-format-card="xlsx"' in markup
    assert 'data-format-card="parquet"' in markup
    assert 'role="radio"' in markup
    assert 'aria-checked="true"' in markup
    assert "aria-pressed" not in markup
    assert "aria-pressed" not in script
    assert "function handleOutputFormatKeydown(event, card)" in script
    assert 'event.key === "ArrowRight"' in script
    assert "card.tabIndex = active ? 0 : -1" in script
    assert "formatCsvHelp" in markup
    assert "formatExcelHelp" in markup
    assert "formatParquetHelp" in markup
    assert "spreadsheetSafeCsvInput" not in markup
    assert "spreadsheetSafeCsvLine" not in markup
    assert "Protect CSV when opening in spreadsheets" not in script
    assert "spreadsheet_safe_csv" not in script
    assert "Good for sharing and opening in spreadsheets." in script
    assert "Ready to open in Excel, with splitting when needed." in script
    assert "Best for large datasets and analytics tools." in script
    assert "excelNotice" not in markup
    assert "parquetNotice" not in markup
    assert "excelNotice" not in script
    assert "parquetNotice" not in script


def test_browser_app_groups_advanced_output_options_by_task() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert "advanced-options-grid" in markup
    assert "advancedSummaryTitle" in markup
    assert "advancedColumnsTitle" in markup
    assert "advancedOrganizationTitle" in markup
    assert "advancedDiagnosticsTitle" in markup
    assert 'data-i18n="advancedSummaryGroup"' in markup
    assert 'data-i18n="advancedColumnsGroup"' in markup
    assert 'data-i18n="advancedOrganizationGroup"' in markup
    assert 'data-i18n="advancedDiagnosticsGroup"' in markup
    assert "advancedSummaryGroup: \"Summary\"" in script
    assert "advancedColumnsGroup: \"Columns\"" in script
    assert "advancedOrganizationGroup: \"Organization\"" in script
    assert "advancedDiagnosticsGroup: \"Diagnostics\"" in script
    assert ".advanced-options-grid" in styles
    assert ".advanced-group + .advanced-group" in styles


def test_browser_app_exposes_summary_options() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")

    assert "summarizeInput" in markup
    assert "summaryOnlyInput" in markup
    assert "summaryFields" in markup
    assert "summaryGroupByInput" in markup
    assert "summaryTotalsInput" in markup
    assert "Generate summary" in script
    assert "Generate only summary" in script
    assert "function updateSummaryMode()" in script
    assert 'byId("summarizeInput").addEventListener("change", updateSummaryMode)' in script
    assert "const summarize = byId(\"summarizeInput\").checked" in script
    assert "summary_only: summaryOnly" in script
    assert "summary_group_by: summarize ? linesFromTextarea(\"summaryGroupByInput\") : []" in script
    assert "summary_totals: summarize ? linesFromTextarea(\"summaryTotalsInput\") : []" in script
    assert "configBool(config.summary_only)" in script
    assert "setTextareaLines(\"summaryGroupByInput\", config.summary_group_by)" in script


def test_browser_app_filter_hint_uses_complete_visual_rules() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert "function visualConditionIsComplete(row)" in script
    assert "function conditionIsComplete(condition)" in script
    assert ".some(visualConditionIsComplete)" in script
    assert "return Boolean(condition.value && condition.value2);" in script
    assert 'value.addEventListener("input", () => {' in script
    assert "clearFilterRowValidation(row)" in script


def test_browser_app_marks_incomplete_visual_rules_inline() -> None:
    script = APP_JS.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert "function validateVisualRowsBeforeSubmit()" in script
    assert "function markFilterRowInvalid(row, field, message)" in script
    assert "field.setAttribute(\"aria-invalid\", \"true\")" in script
    assert "filter-inline-error" in script
    assert "field.focus()" in script
    assert "field.scrollIntoView" in script
    assert "if (!validateVisualRowsBeforeSubmit())" in script
    assert ".filter-row-invalid" in styles
    assert ".filter-inline-error" in styles


def test_browser_app_keeps_workflow_panels_in_main_grid_column() -> None:
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert ".steps {" in styles
    assert "grid-row: 1 / span 4;" in styles
    assert ".panel {\n  grid-column: 2;" in styles
    assert "@media (max-width: 900px)" in styles
    assert ".panel {\n    grid-column: auto;" in styles


def test_browser_app_has_extreme_narrow_zoom_layout_fallback() -> None:
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert "@media (max-width: 320px)" in styles
    assert "width: calc(100vw - 16px)" in styles
    assert ".steps {\n    grid-template-columns: 1fr;" in styles


def test_browser_app_filter_rows_have_operator_specific_layouts() -> None:
    script = APP_JS.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert 'row.classList.toggle("no-value", noValue);' in script
    assert 'row.classList.toggle("is-between", between && !noValue);' in script
    assert ".filter-row.is-between" in styles
    assert ".filter-row.no-value" in styles
    assert ".filter-row .remove-filter" in styles


def test_browser_app_filter_mode_tabs_have_accessible_keyboard_model() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")

    assert 'role="tablist"' in markup
    assert 'data-i18n-aria-label="filterMode"' in markup
    assert 'role="tab"' in markup
    assert 'aria-selected="true"' in markup
    assert 'aria-controls="visualFilterPanel"' in markup
    assert 'role="tabpanel"' in markup
    assert "function handleFilterTabKeydown(event, tab)" in script
    assert 'tab.setAttribute("aria-selected", active ? "true" : "false")' in script
    assert "tab.tabIndex = active ? 0 : -1" in script
    assert 'event.key === "ArrowRight"' in script


def test_browser_app_drop_zone_is_keyboard_operable() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")

    assert 'id="dropZone"' in markup
    assert 'role="button"' in markup
    assert 'data-i18n-aria-label="browseInput"' in markup
    assert 'dropZone.addEventListener("keydown"' in script
    assert 'event.key === "Enter" || event.key === " "' in script
    assert 'byId("browseInputBtn").click();' in script


def test_browser_app_filter_columns_are_searchable() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert 'type="search"' in markup
    assert 'aria-autocomplete="list"' in markup
    assert "filter-column-suggestions" in markup
    assert "columnSearchPlaceholder" in script
    assert "function fuzzyScore(candidate, query)" in script
    assert "function rankedColumns(query)" in script
    assert "function moveColumnSuggestion(input, direction)" in script
    assert "function chooseFirstColumnSuggestion(input)" in script
    assert "function columnSearchParts(value)" in script
    assert 'option.classList.remove("active")' in script
    assert 'suggestions.classList.contains("hidden")' in script
    assert 'event.key === "ArrowDown"' in script
    assert 'event.key === "Tab"' in script
    assert "event.shiftKey ? -1 : 1" in script
    assert "option.tabIndex = -1" in script
    assert ".slice(0, 50)" in script
    assert 'column.addEventListener("input"' in script
    assert 'column.addEventListener("keydown"' in script
    assert ".column-search" in styles
    assert ".filter-column-suggestions" in styles
    assert ".column-suggestion.active" in styles


def test_browser_app_uses_noob_friendly_membership_labels() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")

    assert "é um destes valores" in markup
    assert "não é nenhum destes valores" in markup
    assert "is one of these values" in script
    assert "is none of these values" in script
    assert "está na lista" not in markup
    assert "está na lista" not in script
    assert "is in list" not in script


def test_browser_app_exposes_visual_lookup_file_workflow() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert "lookupTemplate" in markup
    assert "lookupList" in markup
    assert "addLookupBtn" in markup
    assert "data-i18n=\"lookupFilesTitle\"" in markup
    assert "data-i18n=\"addLookup\"" in markup
    assert "data-i18n=\"lookupName\"" in markup
    assert "data-i18n=\"lookupPath\"" in markup
    assert "data-i18n=\"lookupColumn\"" in markup
    assert "choose_lookup_file: bridgeUnavailableResponse" in script
    assert "function addLookup(initial = {})" in script
    assert "function visualLookups()" in script
    assert "function validateLookupRowsBeforeSubmit()" in script
    assert "markLookupInvalid(card, name, t(\"lookupNameRequired\"))" in script
    assert "lookups: visualLookups()" in script
    assert "lookupDefinitionsFromConfig(config.lookup || config.lookups).forEach(addLookup)" in script
    assert "state.api.choose_lookup_file()" in script
    assert "byId(\"addLookupBtn\").addEventListener(\"click\", () => addLookup())" in script
    assert "if (!validateLookupRowsBeforeSubmit())" in script
    assert ".lookup-card" in styles
    assert ".lookup-inline-error" in styles


def test_browser_app_replaces_terminal_details_with_result_cards() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")

    assert "resultCards" in markup
    assert "friendlyErrorBox" in markup
    assert "technicalDetails" in markup
    assert "details-box" not in markup
    assert "function showResultCards(report)" in script
    assert "queuePartialDone" in script
    assert "queueAllFailed" in script
    assert "report.errors || []" in script
    assert ".output-error" in styles
    assert ".result-cards" in styles
    assert "background: #161418" not in styles


def test_browser_app_exposes_bounded_row_preview() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert "previewRowsBtn" in markup
    assert "previewPanel" in markup
    assert "previewTableWrap" in markup
    assert "preview_rows: bridgeUnavailableResponse" in script
    assert "async function previewRows()" in script
    assert "state.api.preview_rows({ ...payload(), limit: 20 })" in script
    assert "function renderPreview(data)" in script
    assert "function previewMetaText(data, rowCount)" in script
    assert "previewLoadedQueue" in script
    assert "previewEmptyQueue" in script
    assert "Number(data.input_count || 1)" in script
    assert "document.createElement(\"table\")" in script
    assert "cell.textContent = value == null ? \"\" : String(value)" in script
    assert ".preview-table-wrap" in styles


def test_browser_app_prompts_for_zip_password_during_inspection() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert "async function maybePromptForZipPasswordAndRetryInspect(error)" in script
    assert "await maybePromptForZipPasswordAndRetryInspect(error)" in script
    assert "async function promptForZipPassword(error)" in script
    assert "Object.assign(thrown, error)" in script
    assert "zipPasswordSessionOnly" in markup
    assert "zipPasswordsInput" not in markup
    assert "textarea" not in markup[markup.index("zip-password-session") : markup.index("allExcelSheetsInput")]
    assert "addZipPasswordBtn" in markup
    assert "clearZipPasswordsBtn" in markup
    assert "zipPasswordStatus" in markup
    assert "zipPasswords: []" in script
    assert "function addZipPassword(password)" in script
    assert "function updateZipPasswordStatus()" in script
    assert 'state.zipPasswords.push(value);' in script
    assert "Used only for this run. Never saved." in script
    assert "password(s) kept only for this session." in script
    assert "function clearZipPasswords()" in script
    assert "state.zipPasswords = [];" in script
    assert "function setInputPaths(paths)" in script
    assert "clearZipPasswords();" in script[script.index("function setInputPaths(paths)") : script.index("function setOutputPath(path)")]
    assert "clearZipPasswords();" in script
    assert ".zip-password-session" in styles


def test_browser_app_confirms_zip_deletion_before_run() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert "function confirmZipDeletionBeforeRun(runPayload)" in script
    assert "confirmZipDelete" in script
    assert "window.confirm" in script
    assert "runPayload.confirm_delete_zip_after_extract = true" in script
    assert "const runPayload = payload();" in script
    assert "state.api.start_filter_run(runPayload)" in script


def test_browser_app_confirms_overwrite_before_retrying_run() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert "confirmOverwrite" in script
    assert "async function startRun(runPayload)" in script
    assert "async function maybeConfirmOverwriteAndRetry(error, runPayload)" in script
    assert 'error.type !== "overwrite_confirmation_required"' in script
    assert "runPayload.confirm_overwrite = true" in script
    assert "await startRun(runPayload)" in script
    assert "maybeConfirmOverwriteAndRetry(error, runPayload)" in script


def test_browser_app_has_visual_derived_columns_controls() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert "derivedColumnTemplate" in markup
    assert "derivedTransformTemplate" in markup
    assert "Criar novas colunas" in markup
    assert "derived-output-name" in markup
    assert "data-i18n=\"derivedOutputName\"" in markup
    assert "data-i18n-placeholder=\"derivedOutputNamePlaceholder\"" in markup
    assert "derived-sample-input" in markup
    assert "derived-sample-before" in markup
    assert "derived-sample-after" in markup
    assert "data-i18n=\"derivedSampleBefore\"" in markup
    assert "data-i18n=\"derivedSampleAfter\"" in markup
    assert "derivedSampleBefore: \"Before\"" in script
    assert "derivedSampleAfter: \"After\"" in script
    assert "function visualDerivedColumns()" in script
    assert "function validateDerivedRowsBeforeSubmit()" in script
    assert "function markDerivedInvalid(card, field, message)" in script
    assert "function clearDerivedValidation(card)" in script
    assert "function derivedTextParamRequired(operation)" in script
    assert "function derivedCountParamRequired(operation)" in script
    assert "markDerivedInvalid(card, source, t(\"derivedSourceRequired\"))" in script
    assert "markDerivedInvalid(card, positionTarget, t(\"derivedPositionTargetRequired\"))" in script
    assert "markDerivedInvalid(card, value, t(\"derivedTransformValueRequired\"))" in script
    assert "markDerivedInvalid(card, value, t(\"derivedTransformCountRequired\"))" in script
    assert "derivedTransformCaseConflict" in script
    assert "field.setAttribute(\"aria-invalid\", \"true\")" in script
    assert "details.open = true" in script
    assert "field.focus()" in script
    assert "field.scrollIntoView" in script
    assert "if (!validateDerivedRowsBeforeSubmit())" in script
    assert "function derivedNameParts(initial = {})" in script
    assert 'const outputName = card.querySelector(".derived-output-name").value.trim();' in script
    assert "name: { value: outputName, prefix, suffix, separator }" in script
    assert 'card.querySelector(".derived-output-name").value = nameParts.output;' in script
    assert "formatDerivedName(source, outputName, prefix, suffix, separator)" in script
    assert "derived_columns: visualDerivedColumns()" in script
    assert "function addDerivedColumn" in script
    assert "function moveDerivedTransform(card, row, direction)" in script
    assert "function handleDerivedMoveKeydown(event, card, row, direction)" in script
    assert 'moveUp.addEventListener("keydown", (event) => handleDerivedMoveKeydown(event, card, row, -1))' in script
    assert 'moveDown.addEventListener("keydown", (event) => handleDerivedMoveKeydown(event, card, row, 1))' in script
    assert '["Enter", " ", "Spacebar"].includes(event.key)' in script
    assert "function updateTransformMoveButtons(card)" in script
    assert "function applyDerivedSampleTransforms(value, transforms)" in script
    assert "function updateDerivedSample(card)" in script
    assert "formatCpfSample(text)" in script
    assert "applyDerivedSampleTransforms(sample, transforms)" in script
    assert "move-derived-transform-up" in markup
    assert "move-derived-transform-down" in markup
    assert "data-i18n-aria-label=\"moveTransformationUp\"" in markup
    assert "data-i18n-aria-label=\"moveTransformationDown\"" in markup
    assert "Move transformation up" in script
    assert "Move transformation down" in script
    assert "function transformPayload" in script
    assert "data-i18n-label=\"transformGroupClean\"" in markup
    assert "data-i18n-label=\"transformGroupChange\"" in markup
    assert "data-i18n-label=\"transformGroupExtract\"" in markup
    assert "data-i18n-label=\"transformGroupFormat\"" in markup
    assert "transformGroupClean: \"Clean text\"" in script
    assert "transformGroupFormat: \"Format identifiers\"" in script
    assert "derived-transform-param" in markup
    assert "derived-transform-value-label" in markup
    assert "valueLabel.textContent = t(\"transformCount\")" in script
    assert "extraLabel.textContent = t(\"transformFill\")" in script
    assert "valueWrapper.classList.toggle(\"hidden\", noValue)" in script
    assert "loadConfigBtn" in markup
    assert "data-i18n=\"loadConfig\"" in markup
    assert "choose_config_file: bridgeUnavailableResponse" in script
    assert "load_config: bridgeUnavailableResponse" in script
    assert "function applyLoadedConfig(config = {})" in script
    assert "function configBool(value)" in script
    assert '["false", "0", "no", "n", "nao", "não"].includes(normalized)' in script
    assert 'byId("dedupeInput").checked = configBool(config.dedupe)' in script
    assert 'byId("caseInsensitiveInput").checked = configBool(config.case_insensitive_columns)' in script
    assert 'setTextareaLines("sortInput", config.sort || config.sorts)' in script
    assert "config.dedupe_keys || config.dedupe_key" in script
    assert "config.output_names || config.output_name" in script
    assert "state.api.load_config({ config_path: chosen.path })" in script
    assert "applyLoadedConfig(data.config || {})" in script
    assert "saveConfigBtn" in markup
    assert "state.api.save_config(payload())" in script
    assert ".derived-column-card" in styles
    assert ".derived-column-card-invalid" in styles
    assert ".derived-inline-error" in styles
    assert ".derived-sample" in styles
    assert ".derived-sample-result" in styles
    assert ".format-card-grid" in styles
