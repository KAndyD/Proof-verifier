"""Консольная проверка последовательного доказательства."""

import argparse

from logic import FormulaError, parse, tree_lines
from verifier import AXIOM_NAMES, AXIOM_TEXT, Verifier


DEMO = (
    "¬p ∨ p",
    "(¬p ∨ p) ⊃ ((¬p ∨ p) ∨ q)",
    "(¬p ∨ p) ∨ q",
)


def show_axioms() -> None:
    print("Аксиомы варианта 3:")
    for name, formula in zip(AXIOM_NAMES, AXIOM_TEXT):
        print(f"  {name}. {formula}")
    print("7а и 7б — две записи из строки 7 задания; знак '=' во вводе не используется.")


def show_help() -> None:
    print("Введите формулу для проверки или команду:")
    print("  :axioms  аксиомы       :list  принятые шаги")
    print("  :tree ФОРМУЛА  дерево  :help  справка       :quit  выход")
    print("Связки: ¬, ∨; импликация ⊃ (или →, ->) — сокращение ¬A ∨ B.")
    print("С клавиатуры можно также писать ! вместо ¬ и | вместо ∨.")
    print("Приоритет: ¬, затем ∨, затем ⊃; ⊃ связывается справа.")


def submit(verifier: Verifier, source: str) -> None:
    try:
        ok, message = verifier.add(source)
    except FormulaError as exc:
        print(f"Ошибка в формуле: {exc}")
        return
    print(("✓ " if ok else "· ") + message)


def interactive() -> None:
    verifier = Verifier()
    print("ЛР №1 · Верификатор доказательств · вариант 3")
    show_help()
    while True:
        try:
            line = input("формула> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nСеанс завершён.")
            break
        if line == ":quit":
            print("Сеанс завершён.")
            break
        if line == ":help":
            show_help()
        elif line == ":axioms":
            show_axioms()
        elif line == ":list":
            if not verifier.steps:
                print("Пока нет принятых шагов.")
            for number, step in enumerate(verifier.steps, 1):
                print(f"  {number}. {step.original} — {step.explanation}")
        elif line.startswith(":tree"):
            expression = line[5:].strip()
            try:
                print("\n".join(tree_lines(parse(expression))))
            except FormulaError as exc:
                print(f"Ошибка в формуле: {exc}")
        elif line.startswith(":"):
            print("Неизвестная команда. Список команд: :help")
        elif line:
            submit(verifier, line)


def main() -> None:
    parser = argparse.ArgumentParser(description="ЛР №1, вариант 3: верификатор доказательств")
    parser.add_argument("--demo", action="store_true", help="показать доказательство на 3 шагах")
    args = parser.parse_args()
    if args.demo:
        verifier = Verifier()
        print("Пример: аксиома 7а → подстановка β → modus ponens\n")
        for number, formula in enumerate(DEMO, 1):
            print(f"{number}. {formula}")
            submit(verifier, formula)
    else:
        interactive()


if __name__ == "__main__":
    main()
