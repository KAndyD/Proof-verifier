"""Формулы варианта 3: ¬, ∨ и запись импликации через ⊃."""

from __future__ import annotations

from dataclasses import dataclass
import unicodedata


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Not:
    child: Formula


@dataclass(frozen=True)
class Or:
    left: Formula
    right: Formula


Formula = Var | Not | Or


class FormulaError(ValueError):
    """Введённая строка не является правильно построенной формулой."""


def render(formula: Formula) -> str:
    """Единая запись формулы; импликации в дереве уже раскрыты."""
    if isinstance(formula, Var):
        return formula.name
    if isinstance(formula, Not):
        child = render(formula.child)
        return f"¬({child})" if isinstance(formula.child, Or) else f"¬{child}"
    return f"({render(formula.left)} ∨ {render(formula.right)})"


def tree_lines(formula: Formula, indent: str = "") -> list[str]:
    if isinstance(formula, Var):
        return [indent + formula.name]
    if isinstance(formula, Not):
        return [indent + "¬"] + tree_lines(formula.child, indent + "  ")
    return ([indent + "∨"] + tree_lines(formula.left, indent + "  ")
            + tree_lines(formula.right, indent + "  "))


class Parser:
    # Ограничение предотвращает переполнение стека на чрезмерно вложенном вводе.
    MAX_LENGTH = 2000
    MAX_DEPTH = 100
    MAX_NODES = 300

    def __init__(self, source: str):
        source = unicodedata.normalize("NFKC", source).replace("→", "⊃")
        source = source.replace("->", "⊃").replace("|", "∨")
        source = source.replace("!", "¬").replace("~", "¬")
        self.source = "".join(c for c in source if not c.isspace())
        self.pos = 0
        self.depth = 0
        self.nodes = 0

    def parse(self) -> Formula:
        if not self.source:
            raise FormulaError("пустая строка")
        if len(self.source) > self.MAX_LENGTH:
            raise FormulaError(f"длина формулы превышает {self.MAX_LENGTH} символов")
        result = self._implication()
        if self.pos != len(self.source):
            self._error("лишний символ или отсутствует операция")
        return result

    def _peek(self) -> str:
        return self.source[self.pos:self.pos + 1]

    def _take(self, char: str) -> bool:
        if self._peek() == char:
            self.pos += 1
            return True
        return False

    def _error(self, reason: str) -> None:
        raise FormulaError(f"позиция {self.pos + 1}: {reason}")

    def _node(self, formula: Formula) -> Formula:
        self.nodes += 1
        if self.nodes > self.MAX_NODES:
            self._error("слишком длинное дерево формулы")
        return formula

    def _implication(self) -> Formula:
        self.depth += 1
        try:
            if self.depth > self.MAX_DEPTH:
                self._error("слишком глубокая вложенность")
            left = self._disjunction()
            if self._take("⊃"):
                right = self._implication()  # импликация связывается справа
                return self._node(Or(self._node(Not(left)), right))
            return left
        finally:
            self.depth -= 1

    def _disjunction(self) -> Formula:
        left = self._unary()
        while self._take("∨"):
            left = self._node(Or(left, self._unary()))
        return left

    def _unary(self) -> Formula:
        self.depth += 1
        try:
            if self.depth > self.MAX_DEPTH:
                self._error("слишком глубокая вложенность")
            if self._take("¬"):
                return self._node(Not(self._unary()))
            if self._take("("):
                inside = self._implication()
                if not self._take(")"):
                    self._error("ожидалась закрывающая скобка")
                return inside
            char = self._peek()
            if "a" <= char <= "z":
                self.pos += 1
                return self._node(Var(char))
            self._error("ожидалась однобуквенная переменная или '('")
        finally:
            self.depth -= 1


def parse(source: str) -> Formula:
    return Parser(source).parse()


def variables(formula: Formula) -> set[str]:
    if isinstance(formula, Var):
        return {formula.name}
    if isinstance(formula, Not):
        return variables(formula.child)
    return variables(formula.left) | variables(formula.right)


def substitute(formula: Formula, variable: str, replacement: Formula) -> Formula:
    """Одна одновременная замена во всех вхождениях указанной переменной."""
    if isinstance(formula, Var):
        return replacement if formula.name == variable else formula
    if isinstance(formula, Not):
        return Not(substitute(formula.child, variable, replacement))
    return Or(substitute(formula.left, variable, replacement),
              substitute(formula.right, variable, replacement))


def subformulas(formula: Formula):
    yield formula
    if isinstance(formula, Not):
        yield from subformulas(formula.child)
    elif isinstance(formula, Or):
        yield from subformulas(formula.left)
        yield from subformulas(formula.right)


def one_substitution(source: Formula, target: Formula) -> tuple[str, Formula] | None:
    """Ищет одну заменяемую букву и единое выражение для всех её вхождений."""
    if source == target:
        return None
    candidates = list(dict.fromkeys(subformulas(target)))
    for variable in sorted(variables(source)):
        for replacement in candidates:
            if substitute(source, variable, replacement) == target:
                return variable, replacement
    return None
