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
    assert "data-i18n-placeholder=\"chooseSavePlaceholder\"" in markup
    assert "styles.css?v=" in markup
    assert "app.js?v=" in markup
    assert "function applyLanguage()" in script
    assert "document.querySelectorAll(\"[data-i18n]\")" in script


def test_browser_app_defaults_numeric_operators_to_number() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert "function defaultTypeForOperator(operator)" in script
    assert '[\"gt\", \"gte\", \"lt\", \"lte\"].includes(operator)' in script
    assert 'return "number";' in script
    assert 'operator === "between"' in script
    assert 'return "auto";' in script


def test_browser_app_syncs_output_suffix_when_format_changes() -> None:
    script = APP_JS.read_text(encoding="utf-8")

    assert "function syncOutputSuffixWithFormat()" in script
    assert "/\\.(csv|xlsx)$/i.test(path)" in script
    assert 'format === "xlsx" ? ".xlsx" : ".csv"' in script
    assert "syncOutputSuffixWithFormat();" in script


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
