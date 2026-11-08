# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline tests for the plain-language brief (docs/IMPACT.md lever L4).

Pins the three properties that make a salience layer safe: the committed brief cannot go
stale (freshness gate), the generator is deterministic (no clock, no volatile stamps), and
the plain language never inflates certainty — the noise floor leads and the forecast's
negative result survives translation (IMPACT.md red line 4).
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import brief  # noqa: E402

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def _build():
    def load(name):
        with open(os.path.join(REPO, "data", "derived", name), encoding="utf-8") as f:
            return json.load(f)
    with open(os.path.join(REPO, "ledger", "index.json"), encoding="utf-8") as f:
        index = json.load(f)
    return brief.build_brief(load("wgi_governance_summary.json"), load("voice_divergence.json"),
                             load("forecast_backtest.json"), index)


class TestFreshness(unittest.TestCase):
    def test_committed_brief_matches_derived_data(self):
        # the drift gate: a stale docs/BRIEF.md fails the suite (and thus the dashboard)
        with open(os.path.join(REPO, "docs", "BRIEF.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), _build(), "docs/BRIEF.md is stale — run `make brief` and commit")


class TestDeterminism(unittest.TestCase):
    def test_two_builds_identical(self):
        self.assertEqual(_build(), _build())

    def test_no_volatile_stamps(self):
        # regeneration must not depend on fetch mode/time, or a re-pin would churn the brief spuriously
        text = _build()
        self.assertNotIn("fetched_utc", text)
        self.assertNotIn("offline-snapshot", text)


class TestHonestyPreserved(unittest.TestCase):
    """Plain language may simplify register, never confidence."""

    def test_noise_floor_is_the_headline(self):
        text = _build()
        one_sentence = text.split("## The ledger")[0]
        self.assertIn("noise", one_sentence, "the noise floor must lead the brief")

    def test_forecast_negative_result_survives_translation(self):
        self.assertIn("does not beat that baseline", _build())

    def test_tally_matches_index(self):
        with open(os.path.join(REPO, "ledger", "index.json"), encoding="utf-8") as f:
            entries = json.load(f)["entries"]
        self.assertIn(f"**{len(entries)} claims**", _build())

    def test_conflicts_surfaced_not_blended(self):
        # the divergence discipline must survive the plain-language register
        self.assertIn("conflict", _build().lower())


class TestCliRobustness(unittest.TestCase):
    def test_missing_input_is_a_clean_error(self):
        orig = brief.DERIVED
        try:
            brief.DERIVED = os.path.join(REPO, "no-such-dir")
            self.assertEqual(brief.main([]), 2)
        finally:
            brief.DERIVED = orig


if __name__ == "__main__":
    unittest.main()
