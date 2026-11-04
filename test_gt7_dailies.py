import sys
import unittest
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gt7_dailies import create_payload, validate_races


class TestPayload(unittest.TestCase):
    def setUp(self):
        self.data = {"status": "success", "count": 3, "data": [
            {"race_type": c, "track_name": f"Test Track {c}", "laps": 6,
             "car_class": "Gr.3", "status": "live", "begin_date": "2026-11-02 00:00:00",
             "raw_payload": {"race": {"consume_fuel": 2, "consume_tire": 5},
                              "regulation": {"tire": "Racing", "compounds": ["Medium"]}},
             "meta_car": {"name": "Test GT3"}}
            for c in "ABC"]}

    def test_valid_current_week(self):
        races, monday = validate_races(self.data, today=date(2026, 11, 3))
        self.assertEqual(monday, date(2026, 11, 2))
        payload = create_payload(races, monday)
        self.assertEqual(len(payload["embeds"]), 3)
        self.assertIn("x5", payload["embeds"][0]["description"])
        self.assertIn("Test GT3", payload["embeds"][0]["description"])

    def test_stale_data_blocked(self):
        with self.assertRaisesRegex(ValueError, "begynder"):
            validate_races(self.data, today=date(2026, 11, 9))

    def test_partial_data_blocked(self):
        self.data["data"].pop()
        with self.assertRaisesRegex(ValueError, "alle tre"):
            validate_races(self.data, today=date(2026, 11, 3))


if __name__ == "__main__":
    unittest.main()
