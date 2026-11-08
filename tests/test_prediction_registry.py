# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline tests for the forward prediction registry — the falsifiable commitment that
the honest "no-change" forecast posture will be tested against the real future."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "forecast"))
import prediction_registry as pr  # noqa: E402
import pharos_forecast as pf  # noqa: E402


def _synth_panel():
    # two countries, 1990..2024, one declining one flat
    return {"AAA": {y: 0.9 - 0.4 * (y - 1990) / 34 for y in range(1990, 2025)},
            "BBB": {y: 0.70 for y in range(1990, 2025)}}


class TestBuildRegistry(unittest.TestCase):
    def test_forecasts_every_country_with_origin_value(self):
        panel = _synth_panel()
        forecasts, fit = pr.build_registry(panel)
        self.assertEqual(set(forecasts), {"AAA", "BBB"})
        self.assertEqual(fit["n_countries"], 2)
        for iso, fc in forecasts.items():
            self.assertEqual(fc["origin_year"], pr.ORIGIN_YEAR)
            self.assertEqual(set(fc["horizons"]), {1, 3})

    def test_no_change_is_the_scored_model(self):
        # the registry's scored forecast is the no-change baseline (mu=0), not a hero call
        forecasts, _ = pr.build_registry(_synth_panel())
        for fc in forecasts.values():
            for h in (1, 3):
                self.assertEqual(fc["horizons"][h]["mu"], 0.0)

    def test_sigma_is_positive_and_leak_free(self):
        # sigma is derived only from past changes realized by the origin year
        forecasts, fit = pr.build_registry(_synth_panel())
        self.assertGreater(fit["sigma_1yr"], 0.0)
        self.assertGreater(fit["sigma_3yr"], fit["sigma_1yr"])  # 3yr spread > 1yr


class TestScoreRegistry(unittest.TestCase):
    def test_no_realized_data_reports_unscored(self):
        forecasts, fit = pr.build_registry(_synth_panel())
        registry = {"forecasts": forecasts}
        # panel has no 2025/2027 -> nothing scoreable
        results = pr.score_registry(registry, _synth_panel())
        for h in pr.HORIZONS:
            self.assertEqual(results[h]["scored"], 0)

    def test_scores_when_outcome_realizes(self):
        # synthesize a realized 2025 for AAA (a decline) and confirm it scores
        panel = _synth_panel()
        panel["AAA"][2025] = panel["AAA"][2024] - 0.10  # a 0.10 decline
        forecasts, _ = pr.build_registry(_synth_panel())  # build from unrealized panel
        registry = {"forecasts": forecasts}
        results = pr.score_registry(registry, panel)
        self.assertEqual(results[1]["scored"], 1)
        self.assertIsNotNone(results[1]["crps"])
        # the climatology reference is scored beside it, and the decline is counted
        r = results[1]
        self.assertIsNotNone(r["crps_climatology"])
        self.assertIn("crps_skill_vs_climatology", r)
        self.assertEqual(r["decline_events"], 1)
        self.assertEqual(r["origin_revision_max_abs"], 0.0)

        # The loader keeps years after the pin only when asked. Until 2026-10-31 it capped live
        # data at 2024 too, so the registry could never be scored; this test passed a hand-made
        # panel and did not see it.
        import csv
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            snap = os.path.join(d, "snap.csv")
            with open(snap, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["code", "year", "value"])
                w.writerow(["AAA", 2024, 0.5])
                w.writerow(["AAA", 2025, 0.4])
            saved = (pf.SNAPSHOT, pf._OFFLINE)
            pf.SNAPSHOT, pf._OFFLINE = snap, True
            try:
                self.assertNotIn(2025, pf._load_panel()["AAA"])
                self.assertIn(2025, pf._load_panel(max_year=None)["AAA"])
            finally:
                pf.SNAPSHOT, pf._OFFLINE = saved
            # a pinned realization round-trips for offline re-scoring
            self.assertEqual(pr._load_pinned(snap)["AAA"][2025], 0.4)

        # main(): --score in any order; an offline re-score of the same pin is byte-identical; a
        # fetch without the origin year writes nothing; the frozen registry is not re-issued by accident.
        import json
        with tempfile.TemporaryDirectory() as d:
            saved = (pr.REGISTRY_PATH, pr.SCORES_PATH, pr.SNAPSHOTS)
            pr.REGISTRY_PATH, pr.SCORES_PATH, pr.SNAPSHOTS = (os.path.join(d, "reg.json"),
                                                              os.path.join(d, "scores.json"), d)
            try:
                with open(pr.REGISTRY_PATH, "w", encoding="utf-8") as f:
                    json.dump({"issued": "2026-07-24", "forecasts": forecasts}, f)
                pin = os.path.join(d, "pin.csv")
                with open(pin, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(["code", "year", "value"])
                    for iso, s in panel.items():
                        for y, v in s.items():
                            w.writerow([iso, y, v])
                self.assertEqual(pr.main(["--panel", pin, "--score"]), 0)
                with open(pr.SCORES_PATH, "rb") as f:
                    first = f.read()
                self.assertEqual(pr.main(["--score", "--panel", pin]), 0)
                with open(pr.SCORES_PATH, "rb") as f:
                    self.assertEqual(f.read(), first)
                res1 = json.loads(first)["scorings"][0]["results"]["1"]
                self.assertFalse(res1["prospective"])  # 2025 was public (March 2026) before the July issue
                empty = os.path.join(d, "empty.csv")
                with open(empty, "w", encoding="utf-8") as f:
                    f.write("code,year,value\n")
                self.assertEqual(pr.main(["--score", "--panel", empty]), 1)
                with open(pr.SCORES_PATH, "rb") as f:
                    self.assertEqual(f.read(), first)
                self.assertEqual(pr.main([]), 2)  # refuses to re-issue without --reissue
            finally:
                pr.REGISTRY_PATH, pr.SCORES_PATH, pr.SNAPSHOTS = saved


class TestCommittedRegistry(unittest.TestCase):
    """Guard the shipped registry's falsifiable contract."""

    def setUp(self):
        path = os.path.join(os.path.dirname(__file__), "..", "data", "derived", "prediction_registry.json")
        if not os.path.exists(path):
            self.skipTest("registry not generated yet (run `python3 src/forecast/prediction_registry.py`)")
        import json
        with open(path, encoding="utf-8") as f:
            self.r = json.load(f)

    def test_is_dated_and_frozen(self):
        self.assertIn("issued", self.r)              # a date -> it's a frozen commitment
        self.assertEqual(self.r["origin_year"], 2024)

    def test_carries_input_provenance(self):
        # the input sha256 pins what it was fit from — can't be silently re-fit
        prov = self.r["input_provenance"]
        self.assertTrue(prov["input_sha256"].startswith("sha256:"))

        # The committed scores reproduce from the committed pins (no hand edits, no silent regression).
        import json
        repo = os.path.join(os.path.dirname(__file__), "..")
        scores_path = os.path.join(repo, "data", "derived", "prediction_registry_scores.json")
        if os.path.exists(scores_path):
            with open(scores_path, encoding="utf-8") as f:
                scores = json.load(f)
            for rec in scores["scorings"]:
                pin = os.path.join(repo, rec["realized_input"]["path"])
                self.assertEqual(pr.fetch_utils.sha256_file(pin), rec["realized_input"]["input_sha256"])
                res = pr.score_registry(self.r, pr._load_pinned(pin), clim_mu=pr.leakfree_climatology(self.r))
                for h, r in rec["results"].items():
                    self.assertEqual(res[int(h)].get("crps"), r.get("crps"))
                    self.assertEqual(res[int(h)].get("crps_climatology"), r.get("crps_climatology"))

    def test_no_hero_call(self):
        # R6 reflexivity fix: the scored model is no-change, not a point call on a country
        for fc in self.r["forecasts"].values():
            for h in fc["horizons"].values():
                self.assertEqual(h["mu"], 0.0)


if __name__ == "__main__":
    unittest.main()
