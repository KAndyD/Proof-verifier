"""Проверки парсера и корректности двух разрешённых правил вывода."""

import unittest

from logic import FormulaError, one_substitution, parse, substitute
from verifier import AXIOMS, Verifier


class ParserTests(unittest.TestCase):
    def test_redundant_parentheses_and_italic_letters(self):
        self.assertEqual(parse("(((𝑝))) ∨ ((q))"), parse("p∨q"))

    def test_implication_is_an_abbreviation_and_right_associative(self):
        self.assertEqual(parse("p ⊃ q"), parse("¬p ∨ q"))
        self.assertEqual(parse("p → q → r"), parse("¬p ∨ (¬q ∨ r)"))
        self.assertNotEqual(parse("(p ⊃ q) ⊃ r"), parse("p ⊃ (q ⊃ r)"))

    def test_rejects_incorrect_formulas(self):
        examples = ("", "p∨", "∨p", "p q", "mn", "p∨(q r)",
                    "p∨q)", "(p∨q", "p⊃⊃q", "p=q", "p1", "p∧q")
        for source in examples:
            with self.subTest(source=source), self.assertRaises(FormulaError):
                parse(source)

    def test_depth_limit(self):
        with self.assertRaises(FormulaError):
            parse("(" * 110 + "p" + ")" * 110)
        with self.assertRaises(FormulaError):
            parse("⊃".join(["p"] * 110))
        with self.assertRaises(FormulaError):
            parse("∨".join(["p"] * 310))


class InferenceTests(unittest.TestCase):
    def test_all_eight_written_axiom_forms_are_parsed(self):
        self.assertEqual(len(AXIOMS), 8)
        self.assertEqual(len(set(AXIOMS)), 8)

    def test_beta_replaces_all_occurrences_at_once(self):
        self.assertEqual(substitute(parse("p∨p"), "p", parse("¬q")),
                         parse("¬q∨¬q"))
        self.assertEqual(one_substitution(parse("p∨p"), parse("q∨q")),
                         ("p", parse("q")))
        self.assertIsNone(one_substitution(parse("p∨p"), parse("q∨r")))

    def test_two_different_replacements_are_not_one_beta_step(self):
        self.assertIsNone(one_substitution(parse("p∨q"), parse("r∨s")))

    def test_axiom_beta_modus_ponens_demo(self):
        verifier = Verifier()
        for text in ("¬p∨p", "(¬p∨p)⊃((¬p∨p)∨q)", "(¬p∨p)∨q"):
            ok, _ = verifier.add(text)
            self.assertTrue(ok)
        self.assertIn("modus ponens", verifier.steps[-1].explanation)
        self.assertEqual(len(verifier.steps), 3)

    def test_rejected_step_does_not_become_available(self):
        verifier = Verifier()
        ok, _ = verifier.add("p")
        self.assertFalse(ok)
        ok, _ = verifier.add("p∨q")
        self.assertFalse(ok)
        self.assertEqual(verifier.steps, [])

    def test_beta_does_not_allow_two_distinct_variables_per_step(self):
        verifier = Verifier()
        # Одного шага из аксиомы 7а достаточно для смены p на q,
        # но не для конструирования произвольной формулы.
        ok, _ = verifier.add("¬q∨q")
        self.assertTrue(ok)
        self.assertIn("β", verifier.steps[-1].explanation)
        ok, _ = verifier.add("¬q∨r")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
