import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from update_pulse import render


class TestPulse(unittest.TestCase):
    def setUp(self):
        start = date(2026, 8, 11)
        self.days = [(start + timedelta(days=i), 0) for i in range(90)]

    def test_zero_activity_does_not_fake_spikes(self):
        result = render(self.days, self.days[-1][0])
        self.assertIn("0 PUBLIC CONTRIBUTIONS", result)
        self.assertNotIn('r="2.3"', result)
        self.assertEqual(result.count('stroke="#315b48"'), 90)

    def test_nonzero_activity_renders_a_signal(self):
        days = self.days.copy()
        days[5] = (days[5][0], 4)
        days[22] = (days[22][0], 9)
        result = render(days, days[-1][0])
        self.assertIn("13 PUBLIC CONTRIBUTIONS", result)
        self.assertEqual(result.count('r="2.3"'), 2)
        self.assertIn('aria-labelledby="title desc"', result)

    def test_rejects_incomplete_input(self):
        with self.assertRaises(ValueError):
            render(self.days[:5], date(2026, 11, 8))


if __name__ == "__main__":
    unittest.main()
