from __future__ import annotations

import unittest

from src.scoring import calculate_acidity_balance, calculate_final_score, normalize_category


class ScoringTests(unittest.TestCase):
    def test_acidity_balance_rewards_middle(self) -> None:
        self.assertEqual(calculate_acidity_balance(5), 10)
        self.assertEqual(calculate_acidity_balance(2.5), 5)
        self.assertEqual(calculate_acidity_balance(0), 0)
        self.assertEqual(calculate_acidity_balance(10), 0)

    def test_fresh_mango_weights(self) -> None:
        score = calculate_final_score(
            {
                "category": "Fresh Mango",
                "sweetness": 10,
                "acidity": 5,
                "aroma": 8,
                "texture": 7,
                "mango_intensity": 9,
                "value_for_money": 4,
            }
        )

        self.assertEqual(score, 8.2)

    def test_prepared_mango_weights(self) -> None:
        score = calculate_final_score(
            {
                "category": "Gelato",
                "sweetness": 10,
                "acidity": 5,
                "aroma": 8,
                "texture": 7,
                "mango_intensity": 9,
                "value_for_money": 4,
            }
        )

        self.assertEqual(score, 8.2)

    def test_legacy_category_aliases(self) -> None:
        self.assertEqual(normalize_category("Fresh mango"), "Fresh Mango")
        self.assertEqual(normalize_category("Mango gelato"), "Gelato")
        self.assertEqual(normalize_category("Other mango magic"), "Other")


if __name__ == "__main__":
    unittest.main()
