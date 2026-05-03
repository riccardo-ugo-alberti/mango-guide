from __future__ import annotations

import unittest

from src.db import _clean_review_payload, _integer_schema_message


class DatabasePayloadTests(unittest.TestCase):
    def test_clean_payload_converts_whole_number_floats(self) -> None:
        payload = _clean_review_payload(
            {
                "name": "Ataulfo",
                "sweetness": 7.0,
                "acidity": 6.5,
                "final_score": 7.0,
                "image_url": None,
                "country": None,
                "created_at": "ignored",
                "unknown": "ignored",
            }
        )

        self.assertEqual(payload["sweetness"], 7)
        self.assertEqual(payload["acidity"], 6.5)
        self.assertEqual(payload["final_score"], 7)
        self.assertIsNone(payload["image_url"])
        self.assertIsNone(payload["country"])
        self.assertNotIn("created_at", payload)
        self.assertNotIn("unknown", payload)

    def test_integer_schema_message_names_half_point_columns(self) -> None:
        message = _integer_schema_message()

        self.assertIn("integer score columns", message)
        self.assertIn("numeric", message)
        self.assertIn("sweetness", message)
        self.assertIn("final_score", message)


if __name__ == "__main__":
    unittest.main()
