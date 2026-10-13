"""Offline regression tests for the ClinicCraft public RSS lead finder."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("find_leads.py")
SPEC = importlib.util.spec_from_file_location("find_leads", SCRIPT)
find_leads = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(find_leads)


class LeadFinderTests(unittest.TestCase):
    def test_writes_daily_and_latest_reports_to_documented_paths(self):
        rss = b"""<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0"><channel><item>
          <title>Freelance PowerPoint presentation designer needed</title>
          <link>https://example.test/opportunity/1</link>
          <description>Looking for a paid presentation formatting freelancer.</description>
          <pubDate>Mon, 12 Oct 2026 10:00:00 +0000</pubDate>
        </item></channel></rss>"""

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "ClinicCraft"
            reports = root / "reports"
            reports.mkdir(parents=True)
            with (
                patch.object(find_leads, "ROOT", root),
                patch.object(find_leads, "OUT", reports),
                patch.object(find_leads, "TODAY", "2026-10-13"),
                patch.object(find_leads, "QUERIES", [("Fixture feed", "https://example.test/feed")]),
                patch.object(find_leads, "fetch", return_value=rss),
            ):
                find_leads.main()

            daily = reports / "2026-10-13.md"
            latest = root / "LATEST_CLIENT_LEADS.md"
            self.assertTrue(daily.is_file())
            self.assertTrue(latest.is_file())
            self.assertEqual(daily.read_text(encoding="utf-8"), latest.read_text(encoding="utf-8"))
            self.assertIn("Freelance PowerPoint presentation designer needed", daily.read_text(encoding="utf-8"))
            self.assertIn("1 unique links", daily.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
