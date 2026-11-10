"""Checks for the unified SVG data slots, layout, and GIF rendering."""
from datetime import date, timedelta
from pathlib import Path
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

import build_profile as profile

NS = "{http://www.w3.org/2000/svg}"
ROOT = Path(__file__).resolve().parents[1]


class UnifiedProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_source = profile.SOURCE
        self.old_dest = profile.DEST
        self.old_frames = profile.FRAME_COUNT
        profile.SOURCE = Path(self.tmp.name) / "profile.svg"
        profile.DEST = Path(self.tmp.name) / "profile.gif"
        shutil.copy(ROOT / "assets" / "profile-composite.svg", profile.SOURCE)
        self.days = [(date(2026, 8, 13) + timedelta(days=i), 0) for i in range(profile.DAYS)]

    def tearDown(self):
        profile.SOURCE = self.old_source
        profile.DEST = self.old_dest
        profile.FRAME_COUNT = self.old_frames
        self.tmp.cleanup()

    def test_all_three_sections_share_one_canvas(self):
        text = profile.SOURCE.read_text(encoding="utf-8")
        self.assertEqual(text.count("<svg "), 1)
        self.assertIn("BRITTNEY</text>", text)
        self.assertIn("contribution-bars", text)
        self.assertIn("PROJECT TOPOLOGY", text)
        self.assertIn("Embers Kernel", text)
        self.assertIn("Emberglass OS", text)
        self.assertIn("Mindful Moments", text)
        self.assertIn('aria-label="OPEN SOURCE RESEARCH"', text)
        self.assertIn("data-rain=", text)

    def test_chart_update_uses_real_counts_and_does_not_overlap(self):
        self.days[9] = (self.days[9][0], 4)
        self.days[43] = (self.days[43][0], 9)
        profile.update_activity(self.days)
        root = ET.parse(profile.SOURCE).getroot()
        count = root.find(".//*[@id='contribution-count']")
        data = root.find(".//*[@id='contribution-bars']")
        self.assertEqual(count.text, "13")
        self.assertEqual(len(list(data)), 92)  # 90 stems + 2 lit tip circles
        self.assertLess(max(float(el.get("x1", "0")) for el in data if el.tag == f"{NS}line"), 1140)

    def test_gif_renders_with_moving_rain(self):
        profile.FRAME_COUNT = 3
        profile.render_gif()
        from PIL import Image
        with Image.open(profile.DEST) as img:
            self.assertEqual(img.n_frames, 3)

    def test_rejects_incomplete_window(self):
        with self.assertRaises(ValueError):
            profile.update_activity(self.days[:7])


if __name__ == "__main__":
    unittest.main()
