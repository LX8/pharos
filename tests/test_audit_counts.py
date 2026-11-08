# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline tests for the doc-count audit — and drift guards that the pinned counts
and the doc claims stay in sync with the repo."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import audit_counts as c  # noqa: E402

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


class TestComputeActual(unittest.TestCase):
    def setUp(self):
        self.actual = c.compute_actual(REPO)

    def test_shape(self):
        for k in ("ledger_entries", "sim_count", "test_count", "robust", "contested", "refuted", "open"):
            self.assertIn(k, self.actual)
        self.assertGreaterEqual(self.actual["ledger_entries"], 15)
        self.assertGreaterEqual(self.actual["sim_count"], 6)
        self.assertGreater(self.actual["test_count"], 80)

    def test_grades_sum_to_entries(self):
        s = sum(self.actual[g] for g in ("robust", "contested", "refuted", "open"))
        self.assertEqual(s, self.actual["ledger_entries"])


class TestDriftGuards(unittest.TestCase):
    def test_pinned_counts_match_repo(self):
        with open(os.path.join(REPO, "data", "expected_counts.json"), encoding="utf-8") as f:
            expected = json.load(f)
        self.assertEqual(expected, c.compute_actual(REPO),
                         "data/expected_counts.json drifted — run `python3 src/audit_counts.py --update`")

    def test_doc_claims_match_repo(self):
        self.assertEqual(c.check_docs(REPO, c.compute_actual(REPO)), [])

    def test_every_doc_pattern_still_matches(self):
        # check_docs silently skips a pattern that no longer matches (so prose can be
        # reworded) — which means a count guard can go dark unnoticed. Pin that every
        # shipped doc-claim is still actually being compared; a reworded doc that breaks
        # its pattern fails here, forcing a conscious update of the pattern or the doc.
        self.assertEqual(c.unmatched_doc_patterns(REPO), [],
                         "a DOC_CHECKS pattern stopped matching its doc — that count is now silently unguarded")
        self.assertEqual(c.unmatched_figure_patterns(REPO), [],
                         "a FIGURE_CHECKS pattern stopped matching — that figure is now silently unpinned from the data")

    def test_site_figures_match_derived(self):
        # the site claims "every public number is machine-checked" — make that true for its
        # computed figures (88% within noise, 45 concur-decline, 2,600 forecasts) by pinning
        # them to the committed derived data.
        self.assertEqual(c.check_figures(REPO, c.compute_derived_figures(REPO)), [],
                         "a site figure drifted from the derived data — re-run the indicators or fix the site")

    def test_figure_check_bites(self):
        # the gate must actually catch a wrong figure, not just pass on the current ones
        bad = dict(c.compute_derived_figures(REPO))
        bad["within_noise_pct"] = 999
        self.assertTrue(any(key == "within_noise_pct" for *_, key in c.check_figures(REPO, bad)))


if __name__ == "__main__":
    unittest.main()
