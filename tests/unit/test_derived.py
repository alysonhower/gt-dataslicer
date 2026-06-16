from pathlib import Path

import duckdb
import pytest

from gt_dataslicer.derived import build_projection, load_derived_columns_file, parse_derived_columns
from gt_dataslicer.exceptions import ConfigError, FilterValidationError


def _derived_value(source_value: object, transform: dict[str, object]) -> object:
    specs = parse_derived_columns(
        [
            {
                "source": "VALUE",
                "name": "OUT",
                "transforms": [transform],
            }
        ]
    )
    projection = build_projection(
        schema_columns={"VALUE": "VALUE"},
        selected_columns=["VALUE"],
        output_columns=["VALUE"],
        derived_columns=specs,
        case_insensitive_columns=False,
    )
    query = f"SELECT {projection.select_items[-1]} FROM (SELECT ? AS VALUE) AS source"
    return duckdb.connect().execute(query, [source_value]).fetchone()[0]


@pytest.mark.parametrize(
    ("source", "transform", "expected"),
    [
        ("abc", {"operation": "replace_text", "old": "a", "new": "X"}, "Xbc"),
        ("abc", {"operation": "uppercase"}, "ABC"),
        ("ABC", {"operation": "lowercase"}, "abc"),
        ("joao   silva", {"operation": "title_case"}, "Joao Silva"),
        ("  abc  ", {"operation": "trim"}, "abc"),
        ("a   b  c", {"operation": "remove_extra_spaces"}, "a b c"),
        ("abc", {"operation": "add_prefix", "text": "BR_"}, "BR_abc"),
        ("abc", {"operation": "add_suffix", "text": "_BR"}, "abc_BR"),
        ("a1b2", {"operation": "keep_digits"}, "12"),
        ("á!b 1", {"operation": "keep_letters"}, "áb"),
        ("ação", {"operation": "remove_accents"}, "acao"),
        ("a! b#1", {"operation": "remove_punctuation"}, "a b1"),
        ("a b\tc", {"operation": "remove_spaces"}, "abc"),
        ("7", {"operation": "pad_left", "count": 3, "fill": "0"}, "007"),
        ("7", {"operation": "pad_right", "count": 3, "fill": "0"}, "700"),
        ("abcdef", {"operation": "take_first", "count": 3}, "abc"),
        ("abcdef", {"operation": "take_last", "count": 3}, "def"),
        ("abcdef", {"operation": "remove_first", "count": 2}, "cdef"),
        ("abcdef", {"operation": "remove_last", "count": 2}, "abcd"),
        ("abc-def", {"operation": "extract_before", "text": "-"}, "abc"),
        ("abc-def", {"operation": "extract_after", "text": "-"}, "def"),
        ("   ", {"operation": "default_if_blank", "text": "N/A"}, "N/A"),
        ("12345678901", {"operation": "format_cpf"}, "123.456.789-01"),
        ("12345678000199", {"operation": "format_cnpj"}, "12.345.678/0001-99"),
        ("11987654321", {"operation": "format_phone"}, "(11) 98765-4321"),
    ],
)
def test_derived_transformations_compile_to_duckdb_sql(source: str, transform: dict[str, object], expected: str) -> None:
    assert _derived_value(source, transform) == expected


def test_derived_columns_can_be_inserted_before_or_after_output_columns() -> None:
    specs = parse_derived_columns(
        [
            {
                "source": "CPF",
                "name": {"prefix": "LIMPO", "separator": "_"},
                "position": {"mode": "before", "target": "Nome"},
                "transforms": [{"operation": "keep_digits"}],
            },
            {
                "source": "CPF",
                "name": {"suffix": "FORMATADO", "separator": "_"},
                "position": {"mode": "after", "target": "LIMPO_CPF"},
                "transforms": [{"operation": "format_cpf"}],
            },
        ]
    )
    projection = build_projection(
        schema_columns={"CPF": "CPF", "NOME": "NOME"},
        selected_columns=["NOME", "CPF"],
        output_columns=["Nome", "CPF"],
        derived_columns=specs,
        case_insensitive_columns=False,
    )

    assert projection.output_columns == ["LIMPO_CPF", "CPF_FORMATADO", "Nome", "CPF"]


def test_derived_columns_reject_confusing_case_chains() -> None:
    with pytest.raises(ConfigError, match="cannot combine case transformations"):
        parse_derived_columns(
            [
                {
                    "source": "NOME",
                    "transforms": [{"operation": "uppercase"}, {"operation": "lowercase"}],
                }
            ]
        )


def test_derived_columns_reject_duplicate_output_names() -> None:
    specs = parse_derived_columns([{"source": "CPF", "name": "CPF", "transforms": ["trim"]}])

    with pytest.raises(FilterValidationError, match="already exists"):
        build_projection(
            schema_columns={"CPF": "CPF"},
            selected_columns=["CPF"],
            output_columns=["CPF"],
            derived_columns=specs,
            case_insensitive_columns=False,
        )


def test_load_derived_columns_file_accepts_root_list_and_object(tmp_path: Path) -> None:
    yaml_path = tmp_path / "derived.yaml"
    yaml_path.write_text(
        "derived_columns:\n"
        "  - source: CPF\n"
        "    name: LIMPO_CPF\n"
        "    transforms:\n"
        "      - operation: keep_digits\n",
        encoding="utf-8",
    )

    specs = load_derived_columns_file(yaml_path)

    assert len(specs) == 1
    assert specs[0].source == "CPF"
    assert specs[0].output_name == "LIMPO_CPF"
