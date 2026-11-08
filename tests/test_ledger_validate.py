# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline, deterministic tests for the ledger structural validator.

Good/bad fixtures pin each rule; a real-ledger scan guards the *shipped* ledger
(and any future second-grader's entries) against silent protocol drift.
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import ledger_validate as m  # noqa: E402
from ledger_staleness import parse_frontmatter  # noqa: E402

LEDGER = os.path.join(os.path.dirname(__file__), "..", "ledger")

GOOD = """---
id: SAA-099
title: A test claim
grade: ROBUST
domain: testing
verified: 2026-01-01
last_reviewed: 2026-02-01
review_interval_days: 540
sources:
  - "Someone (2026). A Thing. — https://example.org/x"
falsification_trigger: "Downgrade if X is shown."
---

## Claim
Body text.
"""
GOOD_FN = "SAA-099-a-test-claim.md"


def problems(text, fn=GOOD_FN):
    return m.validate_entry(parse_frontmatter(text), text, fn)


class TestValidEntry(unittest.TestCase):
    def test_good_entry_has_no_problems(self):
        self.assertEqual(problems(GOOD), [])


class TestEntryRules(unittest.TestCase):
    def test_bad_grade(self):
        bad = GOOD.replace("grade: ROBUST", "grade: SOLID")
        self.assertTrue(any("grade" in p for p in problems(bad)))

    def test_missing_required_field(self):
        bad = GOOD.replace("last_reviewed: 2026-02-01\n", "")
        self.assertTrue(any("last_reviewed" in p for p in problems(bad)))

    def test_id_filename_mismatch(self):
        self.assertTrue(any("does not match filename" in p
                            for p in problems(GOOD, fn="SAA-100-other.md")))

    def test_reviewed_before_verified(self):
        bad = GOOD.replace("last_reviewed: 2026-02-01", "last_reviewed: 2025-12-01")
        self.assertTrue(any("precedes verified" in p for p in problems(bad)))

    def test_nonpositive_interval(self):
        bad = GOOD.replace("review_interval_days: 540", "review_interval_days: 0")
        self.assertTrue(any("positive" in p for p in problems(bad)))

    def test_missing_falsification_trigger(self):
        bad = GOOD.replace('falsification_trigger: "Downgrade if X is shown."\n', "")
        self.assertTrue(any("falsification_trigger" in p for p in problems(bad)))

    def test_missing_sources(self):
        bad = GOOD.replace('sources:\n  - "Someone (2026). A Thing. — https://example.org/x"\n', "")
        self.assertTrue(any("sources" in p for p in problems(bad)))

    def test_unterminated_frontmatter(self):
        self.assertTrue(any("frontmatter" in p for p in problems("---\nid: SAA-099\n")))


class TestIndexCrossCheck(unittest.TestCase):
    def setUp(self):
        self.meta = parse_frontmatter(GOOD)
        self.idx_ok = {"entries": [{"id": "SAA-099", "grade": "ROBUST",
                                    "domain": "testing", "file": GOOD_FN, "title": "A test claim"}]}

    def test_agreement_is_clean(self):
        self.assertEqual(m.validate_against_index([(GOOD_FN, self.meta)], self.idx_ok), [])

    def test_file_not_in_index(self):
        probs = m.validate_against_index([(GOOD_FN, self.meta)], {"entries": []})
        self.assertTrue(any("not listed" in p for p in probs))

    def test_index_orphan(self):
        probs = m.validate_against_index([], self.idx_ok)
        self.assertTrue(any("no such file" in p for p in probs))

    def test_grade_disagreement(self):
        idx_bad = {"entries": [{"id": "SAA-099", "grade": "CONTESTED",
                                "domain": "testing", "file": GOOD_FN}]}
        probs = m.validate_against_index([(GOOD_FN, self.meta)], idx_bad)
        self.assertTrue(any("grade" in p and "disagrees" in p for p in probs))


class TestRealLedger(unittest.TestCase):
    """The shipped ledger must conform — this is what makes the protocol enforceable."""

    def test_every_entry_conforms(self):
        scanned = m._scan(LEDGER)
        self.assertGreaterEqual(len(scanned), 15)
        problems_all = []
        for name, meta, text in scanned:
            problems_all += m.validate_entry(meta, text, name)
        self.assertEqual(problems_all, [], f"ledger protocol violations: {problems_all}")

    def test_ledger_agrees_with_index(self):
        scanned = m._scan(LEDGER)
        with open(os.path.join(LEDGER, "index.json"), encoding="utf-8") as fh:
            index = json.load(fh)
        probs = m.validate_against_index([(n, meta) for n, meta, _ in scanned], index)
        self.assertEqual(probs, [], f"ledger/index.json disagreements: {probs}")


if __name__ == "__main__":
    unittest.main()
