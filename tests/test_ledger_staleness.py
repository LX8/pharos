# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline, deterministic tests for the ledger staleness gate.

The gate reads the real clock only in ``main()``; the core is pure and is tested
here against fixed dates. The real-ledger scan uses a *fixed* ``today`` so the
suite never depends on when it is run — while still guarding that every shipped
entry carries the freshness fields the gate needs.
"""
import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import ledger_staleness as m  # noqa: E402

LEDGER = os.path.join(os.path.dirname(__file__), "..", "ledger")

SAMPLE = """---
id: SAA-099
title: A test claim, with: a colon in it
grade: CONTESTED
verified: 2026-01-01
last_reviewed: 2026-03-01
review_interval_days: 100
sources:
  - "Someone (2026). Thing. — https://example.org/x"
falsification_trigger: "Downgrade if X."
---

## Claim
Body text, not frontmatter.
"""


class TestParseFrontmatter(unittest.TestCase):
    def test_scalars_extracted(self):
        meta = m.parse_frontmatter(SAMPLE)
        self.assertEqual(meta["id"], "SAA-099")
        self.assertEqual(meta["grade"], "CONTESTED")
        self.assertEqual(meta["last_reviewed"], "2026-03-01")
        self.assertEqual(meta["review_interval_days"], "100")

    def test_list_blocks_skipped(self):
        meta = m.parse_frontmatter(SAMPLE)
        self.assertNotIn("sources", meta)  # parent-of-block has no scalar value

    def test_colon_in_value_kept(self):
        meta = m.parse_frontmatter(SAMPLE)
        self.assertEqual(meta["title"], "A test claim, with: a colon in it")

    def test_no_frontmatter_returns_empty(self):
        self.assertEqual(m.parse_frontmatter("no fence here\njust text"), {})


class TestInterval(unittest.TestCase):
    def test_explicit_override_wins(self):
        self.assertEqual(m.review_interval({"grade": "ROBUST", "review_interval_days": "30"}), 30)

    def test_grade_defaults(self):
        self.assertEqual(m.review_interval({"grade": "ROBUST"}), 540)
        self.assertEqual(m.review_interval({"grade": "CONTESTED"}), 270)
        self.assertEqual(m.review_interval({"grade": "OPEN"}), 180)

    def test_unknown_grade_falls_back(self):
        self.assertEqual(m.review_interval({"grade": "WHATEVER"}), m.FALLBACK_INTERVAL_DAYS)


class TestIsStale(unittest.TestCase):
    def test_interval_boundary(self):
        reviewed = date(2026, 1, 1)
        self.assertEqual((date(2026, 4, 11) - reviewed).days, 100)   # boundary fact
        self.assertFalse(m.is_stale(reviewed, 100, date(2026, 4, 11)))  # exactly at interval: fresh
        self.assertTrue(m.is_stale(reviewed, 100, date(2026, 4, 12)))   # one day past: stale

    def test_missing_review_date_is_stale(self):
        self.assertTrue(m.is_stale(None, 540, date(2026, 6, 15)))


class TestEntryStatus(unittest.TestCase):
    def test_fields_and_days_left(self):
        st = m.entry_status(m.parse_frontmatter(SAMPLE), date(2026, 4, 1))
        self.assertEqual(st["id"], "SAA-099")
        self.assertEqual(st["interval_days"], 100)
        self.assertEqual(st["age_days"], 31)        # 2026-03-01 -> 2026-04-01
        self.assertEqual(st["days_left"], 69)
        self.assertFalse(st["stale"])

    def test_last_reviewed_falls_back_to_verified(self):
        meta = {"grade": "ROBUST", "verified": "2026-02-01"}
        self.assertEqual(m.last_reviewed(meta), date(2026, 2, 1))


class TestRealLedger(unittest.TestCase):
    """Guards the *shipped* ledger: every entry must be vouchable and fresh today."""

    def test_every_entry_has_freshness_fields(self):
        rows = m.scan(LEDGER, date(2026, 6, 2))
        self.assertGreaterEqual(len(rows), 15)
        for r in rows:
            self.assertIn(r["grade"], m.GRADES, f"{r['file']}: bad/absent grade")
            self.assertIsNotNone(r["reviewed"], f"{r['file']}: no last_reviewed/verified date")

    def test_none_stale_at_seed_date(self):
        # At the dates the entries were reviewed, none can be stale.
        for r in m.scan(LEDGER, date(2026, 6, 3)):
            self.assertFalse(r["stale"], f"{r['file']} should be fresh at seed date")

    def test_all_stale_in_the_far_future(self):
        # The gate must bite eventually — that is the whole point.
        for r in m.scan(LEDGER, date(2031, 1, 1)):
            self.assertTrue(r["stale"], f"{r['file']} should be stale by 2031")


if __name__ == "__main__":
    unittest.main()
