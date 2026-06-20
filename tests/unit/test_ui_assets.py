import re
from pathlib import Path
from typing import Final


ROOT = Path(__file__).resolve().parents[2]
APP_JS = ROOT / "src" / "gt_dataslicer" / "ui" / "web" / "app.js"
INDEX_HTML = ROOT / "src" / "gt_dataslicer" / "ui" / "web" / "index.html"
STYLES_CSS = ROOT / "src" / "gt_dataslicer" / "ui" / "web" / "styles.css"
DOCUMENTED_CONTEXTUAL_HEX: Final = {
    "#eef9fa",
    "#fbfafc",
    "#f7f5fa",
    "#f7f7f8",
    "#fff4f5",
}


def _translation(script: str, language: str, key: str) -> str:
    block_start = script.index(f'  "{language}": {{')
    block_end = script.index("\n  },", block_start)
    block = script[block_start:block_end]
    match = re.search(rf'    {re.escape(key)}: "([^"]+)",', block)
    assert match is not None
    return match.group(1)


def _workflow_labels(markup: str, script: str, language: str, mode: str) -> list[str]:
    link_keys = dict(re.findall(r'<a href="#([^"]+)"[^>]+data-step-label-key="([^"]+)"', markup))
    sections = re.findall(r'<section id="([^"]+)" class="([^"]+)" data-workflow-step>', markup)
    labels = []
    for step_id, classes in sections:
        if mode == "cleanBase" and "summarization-only-section" in classes:
            continue
        if mode == "summarizationOnly" and "cleanup-only-section" in classes:
            continue
        key = link_keys[step_id]
        labels.append(f"{len(labels) + 1}. {_translation(script, language, key)}")
    return labels


def _hex_colors_outside_root(styles: str) -> set[str]:
    root_end = styles.index("}\n", styles.index(":root {"))
    return set(re.findall(r"#[0-9a-fA-F]{3,8}", styles[root_end:]))


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
    assert "data-i18n=\"dropStrong\"" in markup
    assert "data-i18n=\"dropHelp\"" in markup
    assert "data-i18n-placeholder=\"chooseFolderPlaceholder\"" in markup
    assert "styles.css?v=" in markup
    assert "app.js?v=" in markup
    assert "function applyLanguage()" in script
    assert "document.querySelectorAll(\"[data-i18n]\")" in script


def test_browser_app_uses_drop_zone_as_input_picker() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert "browseInputBtn" not in markup
    assert "byId(\"browseInputBtn\")" not in script
    assert 'id="dropZone" class="drop-zone" role="button" tabindex="0"' in markup
    assert 'aria-labelledby="dropZoneTitle"' in markup
    assert 'aria-describedby="dropZoneHelp"' in markup
    assert "function openInputPicker()" in script
    assert "state.api.choose_input_files()" in script
    assert script.count("state.api.choose_input_files()") == 1
    assert 'dropZone.addEventListener("click"' in script
    assert 'dropZone.addEventListener("keydown"' in script
    assert "function isInputPickerKey(event)" in script
    assert 'event.key === "Enter"' in script
    assert 'event.key === " "' in script
    assert "event.repeat" in script
    assert "event.preventDefault();" in script
    assert 'dropZone.addEventListener("dragover"' in script
    assert 'dropZone.addEventListener("dragleave"' in script
    assert 'dropZone.addEventListener("drop"' in script
    assert "droppedFileNeedsPicker" in script
    assert "Use Browse file" not in script
    assert "use the button" not in script
    assert "botão Procurar arquivo" not in script
    assert ".drop-zone:focus-visible" in styles
    assert "cursor: pointer;" in styles


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


def test_browser_app_uses_directory_first_output_destination() -> None:
    script = APP_JS.read_text(encoding="utf-8")
    markup = INDEX_HTML.read_text(encoding="utf-8")

    output_handler_start = script.index('byId("browseOutputBtn").addEventListener("click"')
    output_handler_end = script.index('byId("browseReportBtn").addEventListener("click"', output_handler_start)
    output_handler = script[output_handler_start:output_handler_end]

    assert "choose_output_directory()" in output_handler
    assert "choose_output_file" not in output_handler
    assert 'data-i18n="chooseOutputFolder"' in markup
    assert 'data-i18n="saveToFolder"' in markup
    assert 'data-i18n-placeholder="chooseFolderPlaceholder"' in markup
    assert "Salvar em" not in markup
    assert "Save as" not in script
    assert "Escolha onde salvar" not in script


def test_browser_app_generates_localized_default_output_names() -> None:
    script = APP_JS.read_text(encoding="utf-8")
    markup = INDEX_HTML.read_text(encoding="utf-8")

    assert 'data-i18n="outputNamesTitle"' in markup
    assert 'data-i18n="individualOutputNames"' not in markup
    assert "individualOutputNames" not in script
    assert "Individual names" not in script
    assert "Nomes individuais" not in script
    assert "individualOutputNamesHelp" not in script
    assert 'id="outputNameSuffixInput"' in markup
    assert 'id="resetOutputNamesBtn"' in markup
    assert 'defaultOutputSuffix: "_tratada"' in script
    assert 'defaultOutputSuffix: "_treated"' in script
    assert "function refreshOutputNameDefaults" in script
    assert "state.outputNameTouchedIndexes.add(index)" in script
    assert "state.outputNameSuffixTouched = true" in script
    assert 'avoid_existing_output_paths: true' in script


def test_browser_app_copy_contract_stays_bilingual_and_concise() -> None:
    script = APP_JS.read_text(encoding="utf-8")
    markup = INDEX_HTML.read_text(encoding="utf-8")
    combined = f"{markup}\n{script}"

    for forbidden_copy in (
        "Summarization step",
        "Individual names",
        "Browse file",
        "Use Browse file",
        "Nomes individuais",
        "botão Procurar arquivo",
        "Operator " "meaning:",
        "Significado do " "operador:",
        "Significado: " "igual a",
    ):
        assert forbidden_copy not in combined

    for expected_copy in (
        'outputNamesTitle: "Nomes"',
        'outputNamesTitle: "Names"',
        'chooseOutput: "Escolha a pasta de destino antes de continuar."',
        'chooseOutput: "Choose a destination folder before continuing."',
        'outputNameSuffix: "Sufixo dos nomes gerados"',
        'outputNameSuffix: "Generated name suffix"',
        'progressArtifactSummarization: "Sumarização"',
        'progressArtifactSummarization: "Summarization"',
        'derivedSummaryEmpty: "Escolha a coluna de origem e pelo menos uma ação."',
        'derivedSummaryEmpty: "Choose the source column and at least one action."',
    ):
        assert expected_copy in script


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
    assert "function rankedColumns(query, columns = state.columns)" in script
    assert "function moveColumnSuggestion(input, direction)" in script
    assert "function chooseFirstColumnSuggestion(input)" in script
    assert "function columnSearchParts(value)" in script
    assert 'option.classList.remove("active")' in script
    assert 'suggestions.classList.contains("hidden")' in script
    assert 'event.key === "ArrowDown"' in script
    assert 'event.key === "Tab"' not in script
    assert "event.shiftKey ? -1 : 1" not in script
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

    assert "é um destes valores" in script
    assert "não é nenhum destes valores" in script
    assert "is one of these values" in script
    assert "is none of these values" in script
    assert "está na lista" not in markup
    assert "está na lista" not in script
    assert "is in list" not in script


def test_browser_app_uses_symbolic_operator_picker_with_accessible_meanings() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")
    operator_options = script[script.index("const FILTER_OPERATOR_OPTIONS"):script.index("const text =")]
    operator_meaning_key = "operator" "Meaning"

    for token in ("=", "≠", ">", "≥", "<", "≤", "∈", "∉", "≤ x ≤", "…x…", "x…", "…x", ".*", "∅", "≠ ∅"):
        assert f'symbol: "{token}"' in operator_options

    for operator_id in (
        "equals",
        "not_equals",
        "gt",
        "gte",
        "lt",
        "lte",
        "in",
        "not_in",
        "between",
        "contains",
        "starts_with",
        "ends_with",
        "regex",
        "is_blank",
        "is_not_blank",
    ):
        assert f'id: "{operator_id}"' in operator_options
        assert f'<option value="{operator_id}"' not in markup

    for legacy_operator_id in ("is_null", "is_not_null", "is_empty", "is_not_empty"):
        assert f'id: "{legacy_operator_id}"' not in operator_options
        assert f'<option value="{legacy_operator_id}"' not in markup

    assert 'opIsNull: "' not in script
    assert 'opIsNotNull: "' not in script
    assert 'opIsEmpty: "' not in script
    assert 'opIsNotEmpty: "' not in script
    assert 'opIsBlank: "é branco ou vazio"' in script
    assert 'opIsNotBlank: "não é branco nem vazio"' in script
    assert 'opIsBlank: "is blank or empty"' in script
    assert 'opIsNotBlank: "is not blank or empty"' in script

    assert 'class="filter-operator" type="hidden" value="equals"' in markup
    assert 'class="operator-trigger"' in markup
    assert 'aria-haspopup="listbox"' in markup
    assert 'aria-describedby' not in script
    assert 'operatorAriaLabel: "Operador: {symbol}, {meaning}"' in script
    assert 'operatorAriaLabel: "Operator: {symbol}, {meaning}"' in script
    assert 'setAttribute("role", "listbox")' in script
    assert 'setAttribute("role", "option")' in script
    assert 'aria-selected' in script
    assert 'item.setAttribute("aria-label", operatorAriaLabel(option));' in script
    assert 'item.title = operatorLabel(option);' in script
    assert 'trigger.setAttribute("aria-label", operatorAriaLabel(option));' in script
    assert 'trigger.title = operatorLabel(option);' in script
    assert 'label.textContent = option.symbol;' in script
    assert 'label.textContent = operatorAriaLabel(option);' not in script
    assert 'setOperatorDescription' not in script
    assert 'operator-description' not in markup
    assert 'operator-description' not in script
    assert 'operator-description' not in styles
    assert 'description.textContent = operatorLabel(option);' not in script
    assert f'description.textContent = t("{operator_meaning_key}")' not in script
    assert f'{operator_meaning_key}:' not in script
    assert 'item.append(symbol);' in script
    assert 'item.append(symbol, meaning);' not in script
    assert 'meaning.className = "operator-option-meaning";' not in script
    assert ".operator-option-meaning" not in styles
    assert "function openOperatorPicker" in script
    assert "function chooseOperator" in script
    assert "operator.addEventListener(\"change\"" in script
    assert 'item.addEventListener("focus", () => setOperatorDescription' not in script
    assert 'item.addEventListener("mouseenter", () => setOperatorDescription' not in script
    assert 'data-i18n="opEquals"' not in markup
    assert ">igual a</option>" not in markup
    assert ">equals</option>" not in markup


def test_browser_app_has_summarization_mode_controls_and_picker_containers() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")

    assert 'id="summarizeInput"' not in markup
    assert 'id="summaryOnlyInput"' not in markup
    assert 'data-i18n="cleanBase"' in markup
    assert 'data-i18n="cleanThenSummarization"' in markup
    assert 'data-i18n="summarizationOnly"' in markup
    assert 'id="summarizationGroupByInput"' in markup
    assert 'id="summarizationTotalsInput"' in markup
    assert '<textarea id="summarizationGroupByInput"' not in markup
    assert '<textarea id="summarizationTotalsInput"' not in markup
    assert 'linesFromTextarea("summarizationGroupByInput")' not in script
    assert 'linesFromTextarea("summarizationTotalsInput")' not in script
    assert "summarization_group_by" in script
    assert "summary_group_by" not in script
    assert 'bindEnterFlow(' in script


def test_browser_app_summary_pickers_include_derived_outputs_without_filter_inputs() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert "function summaryColumnCandidates()" in script
    assert "function derivedOutputNames()" in script
    assert "function projectedOutputColumns()" in script
    assert "formatDerivedName(column.source, column.name.prefix, column.name.suffix, column.name.separator)" in script
    assert "function updateSummaryColumnOptions(input)" in script
    assert "updateColumnOptions(input, summaryColumnCandidates());" in script
    assert "function refreshSummarizationColumnPickers()" in script
    assert "removeUnavailableSummarizationChips(container, candidates);" in script
    assert "updateColumnOptions(input);" in script
    assert "updateColumnOptions(input, summaryColumnCandidates());" in script


def test_browser_app_refreshes_summary_pickers_when_derived_outputs_change() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert "card.remove();\n    updateDerivedEmptyState();\n    refreshSummarizationColumnPickers();" in script
    assert "function updateDerivedCard(card)" in script
    assert "card.querySelector(\".derived-summary\").textContent" in script
    assert "refreshSummarizationColumnPickers();\n}" in script
    assert 'byId("selectColumnsInput").addEventListener("input", refreshSummarizationColumnPickers);' in script
    assert 'byId("renamesInput").addEventListener("input", refreshSummarizationColumnPickers);' in script
    assert "function payload() {\n  refreshSummarizationColumnPickers();" in script


def test_browser_app_uses_dynamic_visible_workflow_step_numbers() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")

    assert "function updateVisibleStepNumbers()" in script
    assert "function numberedStepLabel(number, key)" in script
    assert "function stepEyebrowLabel(number)" in script
    assert "updateVisibleStepNumbers();" in script
    assert 'data-workflow-step' in markup
    assert 'data-step-eyebrow' in markup
    assert 'data-step-label-key="stepSummarization"' in markup
    assert 'stepEyebrow: "Etapa {number}"' in script
    assert 'stepEyebrow: "Step {number}"' in script
    assert 'stepSummarization: "Sumarização"' in script
    assert 'stepSummarization: "Summarization"' in script
    for stale_text in ("Summarization step", "Etapa de sumarização"):
        assert stale_text not in markup
        assert stale_text not in script
    for stale_key in ("stageOne", "stageTwo", "stageThree", "stageFour", "stageSummarization"):
        assert stale_key not in markup
        assert stale_key not in script


def test_browser_app_step_labels_match_route_modes_and_languages() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")

    assert _workflow_labels(markup, script, "pt-BR", "cleanBase") == [
        "1. Arquivo",
        "2. Filtro",
        "3. Novas colunas",
        "4. Saída",
        "5. Gerar",
    ]
    assert _workflow_labels(markup, script, "pt-BR", "cleanThenSummarization") == [
        "1. Arquivo",
        "2. Filtro",
        "3. Novas colunas",
        "4. Sumarização",
        "5. Saída",
        "6. Gerar",
    ]
    assert _workflow_labels(markup, script, "en-US", "summarizationOnly") == [
        "1. File",
        "2. Summarization",
        "3. Output",
        "4. Create",
    ]


def test_browser_app_places_derived_columns_as_own_cleanup_step() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")

    filter_index = markup.index('id="step-filter"')
    derived_index = markup.index('id="step-derived"')
    summarization_index = markup.index('id="step-summarization"')
    output_index = markup.index('id="step-output"')
    run_index = markup.index('id="step-run"')
    assert filter_index < derived_index < summarization_index < output_index < run_index
    assert 'href="#step-derived"' in markup
    assert 'data-step-label-key="stepDerived"' in markup

    derived_section = markup[derived_index:summarization_index]
    output_section = markup[output_index:run_index]
    assert 'class="panel cleanup-only-section derived-section"' in derived_section
    assert 'id="addDerivedColumnBtn"' in derived_section
    assert 'id="derivedColumnsList"' in derived_section
    assert 'id="noDerivedColumnsText"' in derived_section
    assert 'id="saveConfigBtn"' in derived_section
    assert "derived-section" not in output_section
    for derived_control in ("addDerivedColumnBtn", "derivedColumnsList", "noDerivedColumnsText", "saveConfigBtn"):
        assert derived_control not in output_section


def test_browser_app_binds_enter_flow_helper_for_column_pickers() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert "function bindEnterFlow(" in script
    assert "event.key === \"Enter\"" in script
    assert "bindEnterFlow(column" in script or "bindEnterFlow(input" in script


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


def test_browser_app_renders_accessible_structured_progress() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert 'id="progressPanel" class="progress-card ui-card hidden"' in markup
    assert 'id="progressBar" class="progress-bar" role="progressbar"' in markup
    assert 'aria-valuemin="0"' in markup
    assert 'aria-valuemax="100"' in markup
    assert 'id="progressTimeline"' in markup
    assert "function renderProgress(job)" in script
    assert "function progressFromJob(job)" in script
    assert "function progressStatusText(progress)" in script
    assert "renderProgress(job);" in script
    assert "progressBar.removeAttribute(\"aria-valuenow\")" in script
    assert "progressBar.setAttribute(\"aria-valuenow\", String(progress.percent))" in script
    assert ".slice(-6)" in script
    assert "progressIndeterminateLabel" in script
    assert "progressPercentLabel" in script
    assert ".progress-card" in styles
    assert ".progress-bar.indeterminate .progress-bar-fill" in styles
    assert "@keyframes progress-indeterminate" in styles


def test_browser_app_applies_shared_card_primitives_to_workflow_surfaces() -> None:
    markup = INDEX_HTML.read_text(encoding="utf-8")
    styles = STYLES_CSS.read_text(encoding="utf-8")
    script = APP_JS.read_text(encoding="utf-8")

    assert 'class="route-card ui-card ui-card--interactive active"' in markup
    assert markup.count('class="ui-card file-summary-card"') == 3
    assert 'class="status-strip ui-card"' in markup
    assert markup.count('class="result-card ui-card') == 5
    assert 'class="friendly-error ui-card hidden"' in markup
    assert 'class="derived-column-card ui-card"' in markup
    for selector in (
        ".route-card,",
        ".file-summary > div,",
        ".queue-item,",
        ".queue-output-name,",
        ".output-row,",
        ".derived-column-card,",
        ".status-strip,",
        ".result-card,",
    ):
        assert selector in styles
    assert ".output-row:focus-visible" in styles
    assert 'row.className = "queue-item"' in script
    assert 'label.className = "queue-output-name"' in script
    assert 'row.className = "output-row"' in script
    assert 'row.className = "output-row output-error"' in script


def test_browser_app_css_raw_hex_colors_stay_documented_outside_root() -> None:
    styles = STYLES_CSS.read_text(encoding="utf-8")

    assert _hex_colors_outside_root(styles) <= DOCUMENTED_CONTEXTUAL_HEX


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
    assert "const derivedColumns = cleanup ? visualDerivedColumns() : [];" in script
    assert "data.derived_columns = derivedColumns;" in script
    assert "function addDerivedColumn" in script
    assert "function transformPayload" in script
    assert "saveConfigBtn" in markup
    assert "state.api.save_config(payload())" in script
    assert ".derived-column-card" in styles
    assert ".format-card-grid" in styles


def test_browser_app_only_submits_derived_columns_for_cleanup_output() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert 'const cleanup = mode !== "summarizationOnly";' in script
    assert "derived_columns: cleanup ? visualDerivedColumns() : []" not in script
    assert "const derivedColumns = cleanup ? visualDerivedColumns() : [];" in script
    assert "if (derivedColumns.length) {\n    data.derived_columns = derivedColumns;\n  }" in script
    assert "options.derived_columns" not in script


def test_browser_app_disables_derived_controls_in_summarization_only_mode() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert 'document.querySelectorAll(".cleanup-only-section, .cleanup-option")' in script
    assert 'element.classList.toggle("hidden", !cleanup);' in script
    assert ".derived-section input, .derived-section select, .derived-section textarea, .derived-section button" in script
    assert "field.disabled = !cleanup;" in script
    assert "applyLanguage()" in script
    assert "updateSummarizationMode();" in script
    assert "updateDerivedEmptyState();" in script
