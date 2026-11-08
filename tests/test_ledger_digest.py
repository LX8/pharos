# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline tests for the ledger digest (the read surface + falsification watch).

Pins the pure core (grouping, the falsification watch, determinism, pipe-escaping) and the
freshness invariant: the committed ledger/INDEX.md must equal what the current entries generate,
so it can never silently drift from the source of truth.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import ledger_digest as d  # noqa: E402

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
LEDGER = os.path.join(REPO, "ledger")

ENTRIES = [
    ("SAA-002-x.md", {"id": "SAA-002", "grade": "ROBUST", "title": "Beta claim", "domain": "d",
                      "verified": "2026-06-02", "last_reviewed": "2026-06-02",
                      "review_interval_days": "540", "falsification_trigger": "Downgrade if B."}),
    ("SAA-001-x.md", {"id": "SAA-001", "grade": "ROBUST", "title": "Alpha | with pipe", "domain": "d",
                      "verified": "2026-06-02", "last_reviewed": "2026-06-02",
                      "review_interval_days": "540", "falsification_trigger": "Downgrade if A."}),
    ("SAA-003-x.md", {"id": "SAA-003", "grade": "CONTESTED", "title": "Gamma", "domain": "d",
                      "verified": "2026-06-02", "last_reviewed": "2026-06-02",
                      "review_interval_days": "270", "falsification_trigger": "Promote if C."}),
]


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.md = d.build_digest(ENTRIES)

    def test_headline_tally(self):
        self.assertIn("3 graded, falsifiable evidence entries", self.md)
        self.assertIn("2 ROBUST", self.md)
        self.assertIn("1 CONTESTED", self.md)

    def test_grade_sections_and_id_sort(self):
        # ROBUST section exists with its count; entries sort by id within a grade
        self.assertIn("### 🟢 ROBUST (2)", self.md)
        self.assertLess(self.md.index("SAA-001"), self.md.index("SAA-002"))

    def test_coverage_by_domain(self):
        # a by-domain coverage table with the per-domain grade breakdown (all 3 fixture
        # entries share domain "d": 2 ROBUST + 1 CONTESTED)
        self.assertIn("## Coverage by domain", self.md)
        self.assertIn("| d | 3 | 2 ROBUST · 1 CONTESTED |", self.md)

    def test_falsification_watch_lists_every_trigger(self):
        watch = self.md.split("Falsification watch")[1]
        for trig in ("Downgrade if A.", "Downgrade if B.", "Promote if C."):
            self.assertIn(trig, watch)

    def test_next_review_is_deterministic(self):
        # 2026-06-02 + 540 d — computed without a clock, so the file is reproducible
        self.assertIn("2027-11-24", self.md)
        self.assertEqual(d.build_digest(ENTRIES), self.md)

    def test_pipe_in_title_is_escaped(self):
        self.assertIn("Alpha \\| with pipe", self.md)


class TestCommittedIndexIsCurrent(unittest.TestCase):
    """The committed ledger/INDEX.md must match the live entries — run `make index` if this fails."""

    def test_index_matches_entries(self):
        path = os.path.join(LEDGER, "INDEX.md")
        self.assertTrue(os.path.exists(path), "ledger/INDEX.md missing — run `make index`")
        with open(path, encoding="utf-8") as f:
            committed = f.read()
        regenerated = d.build_digest(d._scan(LEDGER))
        self.assertEqual(committed.rstrip("\n"), regenerated.rstrip("\n"),
                         "ledger/INDEX.md is stale — run `make index` and commit")


if __name__ == "__main__":
    unittest.main()
