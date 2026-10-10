"""Проверка шагов доказательства для аксиоматической системы варианта 3."""

from dataclasses import dataclass

from logic import Formula, Not, Or, one_substitution, parse, render


# Схемы записаны ровно как в таблице варианта 3. Равенство в строке 7
# рассматривается как пояснение к двум записям, а не как связка языка.
AXIOM_TEXT = (
    "p ⊃ (p ∨ q)",
    "(p ∨ p) ⊃ p",
    "(p ∨ (q ∨ r)) ⊃ (q ∨ (p ∨ r))",
    "(q ⊃ s) ⊃ ((p ∨ q) ⊃ (p ∨ s))",
    "¬¬p ⊃ p",
    "(¬q ⊃ ¬p) ⊃ (p ⊃ q)",
    "¬p ∨ p",
    "¬p ⊃ (p ⊃ p)",
)
AXIOM_NAMES = ("1", "2", "3", "4", "5", "6", "7а", "7б")
AXIOMS = tuple(parse(text) for text in AXIOM_TEXT)


@dataclass(frozen=True)
class Step:
    formula: Formula
    original: str
    explanation: str


class Verifier:
    def __init__(self):
        self.steps: list[Step] = []
        self.known: dict[Formula, str] = {}
        self.written: dict[Formula, str] = {}
        for name, formula, source in zip(AXIOM_NAMES, AXIOMS, AXIOM_TEXT):
            self.known.setdefault(formula, f"аксиома №{name}")
            self.written.setdefault(formula, source)

    @staticmethod
    def _from(reference: str) -> str:
        if reference.startswith("аксиома"):
            return reference.replace("аксиома", "аксиомы", 1)
        return reference.replace("шаг", "шага", 1)

    def add(self, source: str) -> tuple[bool, str]:
        """Возвращает успех и причину. Не добавляет недоказанные формулы."""
        formula = parse(source)
        if formula in self.known:
            if formula in AXIOMS and formula not in (s.formula for s in self.steps):
                return self._accept(formula, source, f"Это {self.known[formula]}.")
            return False, f"Формула уже известна ({self.known[formula]})."

        # Сначала MP: известные A и A ⊃ B (дерево ¬A ∨ B).
        for statement, implication_ref in self.known.items():
            if (isinstance(statement, Or) and isinstance(statement.left, Not)
                    and statement.right == formula):
                premise = statement.left.child
                if premise in self.known:
                    message = (f"Формула {source.strip()} выводима из формул "
                               f"{self.written[statement]} ({self._from(implication_ref)}) "
                               f"и {self.written[premise]} "
                               f"({self._from(self.known[premise])}) "
                               f"по правилу modus ponens.")
                    return self._accept(formula, source, message)

        # β: одна буква заменяется одним и тем же деревом во всех вхождениях.
        for known, reference in self.known.items():
            found = one_substitution(known, formula)
            if found is not None:
                variable, replacement = found
                message = (f"Формула {source.strip()} выводима из формулы "
                           f"{self.written[known]} ({self._from(reference)}) "
                           f"по правилу β с подстановкой формулы "
                           f"{render(replacement)} вместо переменной {variable}.")
                return self._accept(formula, source, message)

        return False, "Формула корректна, но не выводится за один шаг по MP или β."

    def _accept(self, formula: Formula, source: str, reason: str):
        number = len(self.steps) + 1
        self.steps.append(Step(formula, source.strip(), reason))
        self.known[formula] = f"шаг №{number}"
        self.written[formula] = source.strip()
        return True, f"Шаг {number}: доказано. {reason}"
