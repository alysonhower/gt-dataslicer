from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_manual_test_data_is_ignored_and_documented() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "manual-test-data/" in gitignore
    assert "manual-test-data" in readme
    assert "manual-test-data/" in agents
