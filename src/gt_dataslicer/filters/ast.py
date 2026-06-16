"""Typed AST nodes for the filter DSL."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Literal as TypingLiteral


Scalar = str | Decimal | bool | None | date | datetime


@dataclass(frozen=True, slots=True)
class Expr:
    pass


@dataclass(frozen=True, slots=True)
class Column(Expr):
    name: str


@dataclass(frozen=True, slots=True)
class Literal(Expr):
    value: Scalar
    kind: str


@dataclass(frozen=True, slots=True)
class BooleanOp(Expr):
    op: TypingLiteral["and", "or"]
    children: tuple[Expr, ...]


@dataclass(frozen=True, slots=True)
class Not(Expr):
    expr: Expr


@dataclass(frozen=True, slots=True)
class Comparison(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass(frozen=True, slots=True)
class InPredicate(Expr):
    left: Expr
    values: tuple[Literal, ...]
    negated: bool = False


@dataclass(frozen=True, slots=True)
class LookupPredicate(Expr):
    left: Expr
    lookup_name: str
    negated: bool = False


@dataclass(frozen=True, slots=True)
class BetweenPredicate(Expr):
    left: Expr
    lower: Expr
    upper: Expr


@dataclass(frozen=True, slots=True)
class NullCheck(Expr):
    left: Expr
    kind: TypingLiteral["null", "empty", "blank"]
    negated: bool = False


@dataclass(frozen=True, slots=True)
class StringPredicate(Expr):
    left: Expr
    op: TypingLiteral["contains", "starts_with", "ends_with", "regex"]
    right: Expr

