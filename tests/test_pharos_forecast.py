# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline, deterministic tests for the pharos-forecast proper-scoring core and
the pre-registered backtest harness. No network (the harness reads a snapshot)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "forecast"))
import pharos_forecast as pf  # noqa: E402


class TestScoringRules(unittest.TestCase):
    def test_crps_at_mean(self):
        # CRPS(N(0,1), 0) = 2*phi(0) - 1/sqrt(pi)
        self.assertAlmostEqual(pf.crps_gaussian(0.0, 1.0, 0.0), 0.23369497, places=6)

    def test_crps_zero_sigma_is_abs_error(self):
        self.assertAlmostEqual(pf.crps_gaussian(0.2, 0.0, 0.5), 0.3)

    def test_crps_rewards_closer_forecast(self):
        far = pf.crps_gaussian(0.0, 0.2, 0.5)
        near = pf.crps_gaussian(0.45, 0.2, 0.5)
        self.assertLess(near, far)

    def test_brier(self):
        self.assertEqual(pf.brier(1.0, 1), 0.0)
        self.assertEqual(pf.brier(0.0, 1), 1.0)
        self.assertEqual(pf.brier(0.5, 1), 0.25)

    def test_skill(self):
        self.assertAlmostEqual(pf.skill(0.5, 1.0), 0.5)    # half the loss → +0.5
        self.assertAlmostEqual(pf.skill(2.0, 1.0), -1.0)   # twice the loss → -1
        self.assertEqual(pf.skill(0.3, 0.0), 0.0)          # guard

    def test_stdev(self):
        self.assertAlmostEqual(pf.stdev([1, 2, 3, 4, 5]), 1.5811388, places=6)
        self.assertEqual(pf.stdev([7]), 0.0)


class TestModels(unittest.TestCase):
    def setUp(self):
        # linear decline 0.9 (1990) -> 0.5 (2024)
        self.series = {y: 0.9 - 0.4 * (y - 1990) / 34 for y in range(1990, 2025)}

    def test_no_change_is_zero(self):
        self.assertEqual(pf.f_no_change(self.series, 2010), 0.0)

    def test_trend_extrapolates_decline(self):
        self.assertLess(pf.f_trend(self.series, 2010), 0)             # declining
        self.assertAlmostEqual(pf.f_damped_trend(self.series, 2010),
                               pf.f_trend(self.series, 2010) * pf.DAMP)

    def test_reversion_pulls_toward_mean(self):
        f = pf.make_reversion(0.5)
        self.assertLess(f({2010: 0.9}, 2010), 0)   # above mean → predicts decline
        self.assertGreater(f({2010: 0.2}, 2010), 0)


class TestBacktest(unittest.TestCase):
    def synth(self):
        p = {"AAA": {y: 0.9 - 0.4 * (y - 1990) / 34 for y in range(1990, 2025)},
             "BBB": {y: 0.70 for y in range(1990, 2025)}}
        return p

    def test_structure_and_baseline_skill_zero(self):
        panel = self.synth()
        mean = sum(v for s in panel.values() for v in s.values()) / sum(len(s) for s in panel.values())
        res = pf.backtest(panel, {"no_change": pf.f_no_change, "trend": pf.f_trend,
                                  "reversion": pf.make_reversion(mean)})
        self.assertEqual(res["per_model"]["no_change"]["crps_skill"], 0.0)
        self.assertEqual(res["per_model"]["no_change"]["brier_skill"], 0.0)
        self.assertEqual(res["n_forecasts"], 30)              # 2 countries x 15 origins
        self.assertTrue(0.0 <= res["base_rate"] <= 1.0)
        for m in res["per_model"].values():
            self.assertIn("reliability", m)

    def test_climatology_baseline_auto_injected(self):
        # the climatology no-skill reference is added even if not passed in
        res = pf.backtest(self.synth(), {"no_change": pf.f_no_change})
        self.assertIn("climatology", res["per_model"])

    def test_empty_panel_returns_nothing_to_score_not_crash(self):
        # regression: backtest({}) used to raise ZeroDivisionError (crps_sum / n, n=0).
        # It must return an explicit empty result instead.
        res = pf.backtest({}, {"no_change": pf.f_no_change})
        self.assertEqual(res["n_forecasts"], 0)
        self.assertEqual(res["per_model"], {})

    def test_missing_no_change_baseline_raises_clearly(self):
        # regression: a models dict without 'no_change' used to KeyError deep inside
        # the skill computation. It must raise a clear contract error up front.
        with self.assertRaises(ValueError) as cm:
            pf.backtest(self.synth(), {"trend": pf.f_trend})
        self.assertIn("no_change", str(cm.exception))

    def test_score_origins_restricts_scored_cases(self):
        # out-of-sample mechanism: score_origins must score ONLY those origins.
        # synth panel = 2 countries x 15 origins (2000..2014) = 30 cases by default.
        panel = self.synth()
        res_all = pf.backtest(panel, {"no_change": pf.f_no_change})
        self.assertEqual(res_all["n_forecasts"], 30)
        res_held = pf.backtest(panel, {"no_change": pf.f_no_change},
                               score_origins=(2013, 2014))
        self.assertEqual(res_held["n_forecasts"], 2 * 2)   # 2 countries x 2 origins

    def test_score_origins_none_scores_all(self):
        # score_origins=None (default) reproduces the full backtest exactly
        panel = self.synth()
        full = pf.backtest(panel, {"no_change": pf.f_no_change})
        none_arg = pf.backtest(panel, {"no_change": pf.f_no_change}, score_origins=None)
        self.assertEqual(full, none_arg)


class TestCommittedBacktest(unittest.TestCase):
    """Guards the shipped result: the honest pre-registered finding must hold."""

    def setUp(self):
        import json
        path = os.path.join(os.path.dirname(__file__), "..", "data", "derived", "forecast_backtest.json")
        if not os.path.exists(path):
            self.skipTest("backtest not generated yet (run `make forecast`)")
        with open(path, encoding="utf-8") as f:
            self.d = json.load(f)

    def test_baseline_present_and_honest_verdict(self):
        self.assertIn("no_change", self.d["result"]["per_model"])
        # the pre-registered bar is skill>0; v0 honestly does not clear it
        self.assertLessEqual(self.d["best_model"]["crps_skill"], 0.0)
        self.assertIn("does NOT beat", self.d["verdict"])

    def test_input_provenance_present(self):
        # DATA_CONTRACT §guarantees #2: the derived JSON must carry the input
        # snapshot's source_url + fetched_utc + input_sha256, so a swapped upstream
        # snapshot is detectable from this file alone.
        prov = self.d["input_provenance"]
        self.assertTrue(prov["source_url"].startswith("https://"))
        self.assertIn("T", prov["fetched_utc"])               # an ISO timestamp
        self.assertTrue(prov["input_sha256"].startswith("sha256:"))
        # and it must match the actual committed snapshot file
        import hashlib
        h = hashlib.sha256()
        with open(pf.SNAPSHOT, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        self.assertEqual(prov["input_sha256"], "sha256:" + h.hexdigest())


class TestCommittedHoldout(unittest.TestCase):
    """Guards the out-of-sample hold-out result: the negative verdict must also hold
    on the held-out (most recent) origins, not just the full window."""

    def setUp(self):
        import json
        path = os.path.join(os.path.dirname(__file__), "..", "data", "derived", "oos_holdout.json")
        if not os.path.exists(path):
            self.skipTest("oos hold-out not generated yet (run `python3 src/forecast/oos_holdout.py`)")
        with open(path, encoding="utf-8") as f:
            self.d = json.load(f)

    def test_holdout_verdict_holds(self):
        # the whole point of the out-of-sample test: the negative result generalizes
        self.assertTrue(self.d["verdict"]["holds"],
                        f"OOS verdict does not hold: {self.d['verdict']}")

    def test_holdout_scores_recent_origins(self):
        self.assertEqual(self.d["holdout_origins"], [2012, 2013, 2014])
        self.assertGreater(self.d["n_forecasts"], 0)


if __name__ == "__main__":
    unittest.main()
