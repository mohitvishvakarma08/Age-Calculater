import unittest
from datetime import date

from app import app, calculate, predict_age_group


class AgeCalculatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config.update(TESTING=True)
        cls.client = app.test_client()

    def test_calculate_returns_exact_age_and_totals(self):
        response = self.client.post(
            "/api/calculate",
            json={"name": "ankit", "birth": "2001-11-08", "end": "2026-09-27"},
        )

        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertEqual(result["name"], "ankit")
        self.assertEqual(result["birth_date"], "08/11/2001")
        self.assertEqual(result["end_date"], "27/09/2026")
        self.assertEqual(result["age"], {"years": 24, "months": 10, "days": 19})
        self.assertEqual(result["age_group"], "Adult")
        self.assertEqual(result["totals"]["days"], 9089)

    def test_calculate_handles_leap_day_birthdays(self):
        result = calculate(date(2000, 2, 29), date(2021, 2, 28))

        self.assertEqual(result["age"], {"years": 21, "months": 0, "days": 0})
        self.assertEqual(result["birthday_date"], "February 28, 2022")
        self.assertEqual(result["age_group"], "Adult")

    def test_age_group_model_classifies_boundaries(self):
        self.assertEqual(predict_age_group(12), "Child")
        self.assertEqual(predict_age_group(13), "Teenager")
        self.assertEqual(predict_age_group(19), "Teenager")
        self.assertEqual(predict_age_group(20), "Adult")
        self.assertEqual(predict_age_group(59), "Adult")
        self.assertEqual(predict_age_group(60), "Senior")

    def test_calculate_rejects_missing_json(self):
        response = self.client.post("/api/calculate", data="not-json", content_type="text/plain")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Please provide a JSON object.")

    def test_calculate_rejects_invalid_date(self):
        response = self.client.post(
            "/api/calculate",
            json={"birth": "2001-02-29", "end": "2026-09-27"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("valid birth date", response.get_json()["error"])

    def test_calculate_rejects_end_before_birth(self):
        response = self.client.post(
            "/api/calculate",
            json={"birth": "2026-09-27", "end": "2020-01-01"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("cannot be before", response.get_json()["error"])

    def test_text_export_is_a_table_and_uses_report_filename(self):
        payload = {
            "type": "txt",
            "name": "ankit",
            "birth_date": "08/11/2001",
            "end_date": "27/09/2026",
            "age": {"years": 24, "months": 10, "days": 19},
            "age_group": "Adult",
            "born_on": "Thursday",
            "next_birthday": "42 days",
            "birthday_date": "November 08, 2026",
            "totals": {"months": 298, "weeks": 1298, "days": 9089, "hours": 218136, "minutes": 13088160},
        }

        response = self.client.post("/api/export", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Ankit's age.txt", response.headers["Content-Disposition"])
        content = response.get_data(as_text=True)
        self.assertIn("| Details", content)
        self.assertIn("| Total Minutes", content)
        self.assertIn("| AI age group", content)
        self.assertNotIn("| Report", content)

    def test_export_rejects_incomplete_payload(self):
        response = self.client.post("/api/export", json={"type": "pdf", "name": "ankit"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("age data is incomplete", response.get_json()["error"])

    def test_export_rejects_unsupported_format(self):
        response = self.client.post(
            "/api/export",
            json={"type": "csv", "age": {}, "totals": {}},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Unsupported file format.")

    def test_export_rejects_non_numeric_values(self):
        response = self.client.post(
            "/api/export",
            json={
                "type": "txt",
                "age": {"years": "24", "months": 10, "days": 19},
                "age_group": "Adult",
                "totals": {"months": 298, "weeks": 1298, "days": 9089, "hours": 218136, "minutes": 13088160},
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("age values must be integers", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
