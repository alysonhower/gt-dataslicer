from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP_JS = ROOT / "src" / "gt_dataslicer" / "ui" / "web" / "app.js"
INDEX_HTML = ROOT / "src" / "gt_dataslicer" / "ui" / "web" / "index.html"
STYLES_CSS = ROOT / "src" / "gt_dataslicer" / "ui" / "web" / "styles.css"


def test_browser_app_does_not_prefer_stale_raw_filter_in_visual_mode() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert 'state.filterMode === "advanced" || rawFilter' not in script
    assert 'state.filterMode === "advanced"' in script


def test_browser_app_recovers_run_button_after_start_error() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert "byId(\"runBtn\").disabled = true" in script
    assert "catch (_error)" in script
    assert "byId(\"runBtn\").disabled = false" in script


def test_browser_app_has_translation_hooks_for_static_text() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")

    assert "data-i18n=\"chooseFile\"" in markup
    assert "data-i18n=\"browseInput\"" in markup
    assert "data-i18n-placeholder=\"chooseSavePlaceholder\"" in markup
    assert "styles.css?v=" in markup
    assert "app.js?v=" in markup
    assert "function applyLanguage()" in script
    assert "document.querySelectorAll(\"[data-i18n]\")" in script


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


def test_browser_app_infers_value_type_without_showing_type_field() -> None:
    script = APP_JS.read_text(encoding="utf-8")
    markup = INDEX_HTML.read_text(encoding="utf-8")

    assert "filter-type" not in markup
    assert "function inferredTypeForCondition(operator, value)" in script
    assert '[\"gt\", \"gte\", \"lt\", \"lte\"].includes(operator)' in script
    assert 'operator === "between"' in script
    assert 'return "auto";' in script
    assert r"\d{4}-\d{2}-\d{2}(?:[T ][0-2]\d:[0-5]\d" in script
    assert 'return "string";' in script
    assert "/^-?(?:\\d+(?:\\.\\d*)?|\\.\\d+)$/.test(text)" not in script
    assert "value_type: inferredTypeForCondition(" in script
    assert 'row.querySelector(".filter-operator").value' in script
    assert 'row.querySelector(".filter-value").value' in script


def test_browser_app_syncs_output_suffix_when_format_changes() -> None:
    script = APP_JS.read_text(encoding="utf-8")
    markup = INDEX_HTML.read_text(encoding="utf-8")

    assert "function syncOutputSuffixWithFormat()" in script
    assert "/\\.(csv|xlsx|parquet)$/i.test(path)" in script
    assert 'parquet: ".parquet"' in script
    assert "syncOutputSuffixWithFormat();" in script
    assert 'data-format-card="csv"' in markup
    assert 'data-format-card="xlsx"' in markup
    assert 'data-format-card="parquet"' in markup
    assert "formatCsvHelp" not in markup
    assert "formatExcelHelp" not in markup
    assert "formatParquetHelp" not in markup
    assert "formatCsvHelp" not in script
    assert "formatExcelHelp" not in script
    assert "formatParquetHelp" not in script
    assert "excelNotice" not in markup
    assert "parquetNotice" not in markup
    assert "excelNotice" not in script
    assert "parquetNotice" not in script


def test_browser_app_filter_hint_uses_complete_visual_rules() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert "function visualConditionIsComplete(row)" in script
    assert "function conditionIsComplete(condition)" in script
    assert ".some(visualConditionIsComplete)" in script
    assert "return Boolean(condition.value && condition.value2);" in script
    assert 'value.addEventListener("input", updateFilterHint)' in script


def test_browser_app_keeps_workflow_panels_in_main_grid_column() -> None:
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert ".steps {" in styles
    assert "grid-row: 1 / span 4;" in styles
    assert ".panel {\n  grid-column: 2;" in styles
    assert "@media (max-width: 900px)" in styles
    assert ".panel {\n    grid-column: auto;" in styles


def test_browser_app_filter_rows_have_operator_specific_layouts() -> None:
    script = APP_JS.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert 'row.classList.toggle("no-value", noValue);' in script
    assert 'row.classList.toggle("is-between", between && !noValue);' in script
    assert ".filter-row.is-between" in styles
    assert ".filter-row.no-value" in styles
    assert ".filter-row .remove-filter" in styles


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


def test_browser_app_has_summary_controls_and_payload_fields() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")

    assert 'id="summarizeInput"' in markup
    assert 'id="summaryOnlyInput"' in markup
    assert 'id="summaryFields"' in markup
    assert 'id="summaryGroupByInput"' in markup
    assert 'id="summaryTotalsInput"' in markup
    assert "summaryGroupBy" in markup
    assert "summaryTotals" in markup
    assert "summarize" in script
    assert "summary_only" in script
    assert "summaryOnlyInput" in script
    assert "function updateSummaryMode()" in script
    assert "addEventListener(\"change\", updateSummaryMode)" in script


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


def test_browser_app_prompts_for_zip_password_during_inspection() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert "async function maybePromptForZipPasswordAndRetryInspect(error)" in script
    assert "await maybePromptForZipPasswordAndRetryInspect(error)" in script
    assert "async function promptForZipPassword(error)" in script
    assert "Object.assign(thrown, error)" in script


def test_browser_app_has_visual_derived_columns_controls() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert "derivedColumnTemplate" in markup
    assert "derivedTransformTemplate" in markup
    assert "Criar novas colunas" in markup
    assert "function visualDerivedColumns()" in script
    assert "derived_columns: visualDerivedColumns()" in script
    assert "function addDerivedColumn" in script
    assert "function transformPayload" in script
    assert "saveConfigBtn" in markup
    assert "state.api.save_config(payload())" in script
    assert ".derived-column-card" in styles
    assert ".format-card-grid" in styles
