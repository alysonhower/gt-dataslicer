"""Type utilities for filter compilation."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
import re

from .ast import Literal


ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ][0-2]\d:[0-5]\d(?::[0-5]\d(?:\.\d+)?)?$")


def literal_to_type(literal: Literal) -> str:
    if literal.kind in {"date", "datetime", "decimal", "bool", "null"}:
        return literal.kind
    if isinstance(literal.value, Decimal):
        return "decimal"
    if isinstance(literal.value, bool):
        return "bool"
    if isinstance(literal.value, date) and not isinstance(literal.value, datetime):
        return "date"
    if isinstance(literal.value, datetime):
        return "datetime"
    return "string"


def string_date_type(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    if ISO_DATE_RE.match(value):
        return "date"
    if ISO_DATETIME_RE.match(value):
        return "datetime"
    return None

