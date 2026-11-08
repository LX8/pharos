# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline tests for the flagship watch-report prototype (docs/IMPACT.md lever L2 [now] half)
and the H3 symmetric-reporting machine gate (docs/BIAS_AUDIT_PREREGISTRATION.md §3).
"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import audit_counts  # noqa: E402
import watch_report  # noqa: E402

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def _build():
    def load(name):
        with open(os.path.join(REPO, "data", "derived", name), encoding="utf-8") as f:
            return json.load(f)
    with open(os.path.join(REPO, "ledger", "index.json"), encoding="utf-8") as f:
        index = json.load(f)
    return watch_report.build_report(load("wgi_governance_summary.json"),
                                     load("voice_divergence.json"),
                                     load("forecast_backtest.json"), index)


class TestWatchReport(unittest.TestCase):
    def test_committed_report_is_fresh(self):
        with open(os.path.join(REPO, "docs", "WATCH_REPORT.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), _build(), "stale — run `make watch-report` and commit")

    def test_movements_table_never_drops_asymmetric_rows(self):
        # if the two top-N lists ever differ in length, no row may be silently truncated away —
        # zip() would drop the extra decline; zip_longest keeps it with a blank counterpart
        d = [{"country": "A", "change": -1.0, "z": -2.0}, {"country": "B", "change": -3.0, "z": -4.0}]
        i = [{"country": "C", "change": 1.0, "z": 2.0}]
        out = watch_report._zip_movers(d, i)
        self.assertEqual(len(out.splitlines()), 2)   # max(2, 1), not min
        self.assertIn("B", out)                       # the unmatched decline is kept
        self.assertIn("—", out)                       # its missing improvement shows blank

    def test_symmetric_case_output_unchanged(self):
        # the fix must be byte-identical for equal-length lists (guards the committed report)
        row = watch_report._zip_movers(
            [{"country": "Nicaragua", "change": -19.1706, "z": -5.446}],
            [{"country": "Gambia, The", "change": 17.9825, "z": 4.894}])
        self.assertEqual(row, "| Nicaragua | -19.2 | -5.4 | | Gambia, The | +18.0 | +4.9 |")

    def test_deterministic_and_stampless(self):
        text = _build()
        self.assertEqual(text, _build())
        self.assertNotIn("fetched_utc", text)

    def test_watch_list_matches_derived_headline(self):
        with open(os.path.join(REPO, "data", "derived", "voice_divergence.json"), encoding="utf-8") as f:
            headline = json.load(f)["headline_concur_decline_n_sig_3"]
        self.assertIn(f"The Watch List — {len(headline)} countries", _build())

    def test_prototype_banner_until_founder_names_it(self):
        # the name + cadence are the founder's; the artifact must say so until they decide
        self.assertIn("PROTOTYPE", _build())

    def test_symmetric_by_construction(self):
        # movements table carries improvements beside declines; concurrence carries both directions
        text = _build()
        self.assertIn("Largest improvements", text)
        self.assertIn("concurrence on *improvement*", text)

    def test_improve_counterpart_uses_the_same_bar(self):
        # R7 review, MAJOR: the Watch List is the n_sig==3 decline set, so its stated
        # improvement counterpart must be the n_sig==3 improve count — never the looser
        # CONCUR-IMPROVE total, which mixes 2-of-3 countries and inflates the "balance"
        with open(os.path.join(REPO, "data", "derived", "voice_divergence.json"), encoding="utf-8") as f:
            v = json.load(f)
        full3 = sum(1 for c in v["countries"]
                    if c["agreement"]["label"] == "CONCUR-IMPROVE" and c["agreement"]["n_sig"] == 3)
        text = _build()
        self.assertIn(f"**{full3} countries** show full three-instrument", text)
        # and the looser pair is reported AS the looser pair, both sides at the same bar
        self.assertIn(f"{v['counts']['CONCUR-DECLINE']} declining to "
                      f"{v['counts']['CONCUR-IMPROVE']} improving", text)

    def test_missing_input_is_a_clean_error(self):
        orig = watch_report.DERIVED
        try:
            watch_report.DERIVED = os.path.join(REPO, "no-such-dir")
            self.assertEqual(watch_report.main([]), 2)
        finally:
            watch_report.DERIVED = orig


class TestSymmetricReportingGate(unittest.TestCase):
    FIGS = {"meaningful_declines": 88, "meaningful_improvements": 54}

    def test_all_current_surfaces_pass(self):
        figures = audit_counts.compute_derived_figures(REPO)
        self.assertEqual(audit_counts.check_symmetric_reporting(REPO, figures), [])

    def test_violation_bites(self):
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "README.md"), "w", encoding="utf-8") as f:
                f.write("We measured 88 meaningful declines this decade.")
            problems = audit_counts.check_symmetric_reporting(td, self.FIGS)
            self.assertEqual(len(problems), 1)
            self.assertEqual(problems[0][0], "README.md")

    def test_percentage_does_not_false_trigger(self):
        # 88 (declines) and 88% (within-noise) collide numerically; only the count binds
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "README.md"), "w", encoding="utf-8") as f:
                f.write("88% of changes are within noise.")
            self.assertEqual(audit_counts.check_symmetric_reporting(td, self.FIGS), [])

    def test_balanced_surface_passes(self):
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "README.md"), "w", encoding="utf-8") as f:
                f.write("88 declines against 54 improvements.")
            self.assertEqual(audit_counts.check_symmetric_reporting(td, self.FIGS), [])


if __name__ == "__main__":
    unittest.main()
