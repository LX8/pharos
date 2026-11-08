# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline, deterministic tests for the Voice & Accountability triangulation.

The network fetch is not tested (flaky by design); the load-bearing logic — the
per-instrument reductions and the divergence combiner, including the anti-gaming
guarantees (disagreement beats majority; one instrument can never produce HIGH;
a missing CI never masquerades as significance) — is pure and fully tested. A light
guard also checks the committed derived artifact for internal consistency.
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "indicators"))
import voice_divergence as m  # noqa: E402


def wrow(verdict, z=-3.0, base=50.0, latest=40.0, change=-10.0):
    return {"verdict": verdict, "sc_base": str(base), "sc_latest": str(latest),
            "change": str(change), "z": str(z)}


SIG_DECLINE = {"wgi": m.reduce_wgi(wrow("DECLINE")),
               "vdem": m.reduce_vdem(0.90, 0.80),
               "fh": m.reduce_fh(55, 48)}
SIG_IMPROVE = {"wgi": m.reduce_wgi(wrow("IMPROVE", z=3.0, change=10.0, base=40, latest=50)),
               "vdem": m.reduce_vdem(0.80, 0.90),
               "fh": m.reduce_fh(48, 55)}
NS = {"vdem": m.reduce_vdem(0.90, 0.91), "fh": m.reduce_fh(50, 51)}


class TestReductions(unittest.TestCase):
    def test_vdem_threshold(self):
        self.assertEqual(m.reduce_vdem(0.90, 0.951)["direction"], 1)    # +0.051 ≥ 0.05
        self.assertEqual(m.reduce_vdem(0.90, 0.949)["direction"], 0)    # +0.049 < 0.05
        self.assertEqual(m.reduce_vdem(0.96, 0.90)["direction"], -1)
        self.assertEqual(m.reduce_vdem(0.90, 0.80)["flag_basis"], "THRESHOLD")

    def test_fh_threshold_on_0_60(self):
        self.assertEqual(m.reduce_fh(55, 50)["direction"], -1)          # −5 ≥ 3
        self.assertEqual(m.reduce_fh(50, 48)["direction"], 0)           # −2 < 3 (the 0–60 rescale)
        self.assertEqual(m.reduce_fh(55, 50)["flag_basis"], "THRESHOLD-NO-CI")

    def test_wgi_maps_verdict(self):
        self.assertEqual(m.reduce_wgi(wrow("DECLINE"))["direction"], -1)
        self.assertEqual(m.reduce_wgi(wrow("IMPROVE"))["direction"], 1)
        self.assertEqual(m.reduce_wgi(wrow("NO_SIG_CHANGE"))["direction"], 0)
        w = m.reduce_wgi(wrow("DECLINE"))
        self.assertEqual(w["flag"], "SIG")
        self.assertEqual(w["flag_basis"], "CI")
        self.assertEqual(w["z"], -3.0)

    def test_absent(self):
        a = m.absent("prob_0_1")
        self.assertFalse(a["available"])
        self.assertEqual(a["flag"], "NA")


class TestCombiner(unittest.TestCase):
    def test_concur_decline_three_sig(self):
        a = m.combine_agreement(SIG_DECLINE["wgi"], SIG_DECLINE["vdem"], SIG_DECLINE["fh"])
        self.assertEqual(a["label"], "CONCUR-DECLINE")
        self.assertEqual(a["n_sig"], 3)
        self.assertEqual(a["evidence_strength"], "HIGH")
        self.assertEqual(a["flag_basis_mix"], {"CI": 1, "THRESHOLD": 1, "THRESHOLD-NO-CI": 1})

    def test_concur_improve(self):
        a = m.combine_agreement(SIG_IMPROVE["wgi"], SIG_IMPROVE["vdem"], SIG_IMPROVE["fh"])
        self.assertEqual(a["label"], "CONCUR-IMPROVE")
        self.assertEqual(a["evidence_strength"], "HIGH")

    def test_conflict_names_dissenter(self):
        # WGI −1, V-Dem −1, FH +1 — a gamed single input surfaces as CONFLICT.
        a = m.combine_agreement(SIG_DECLINE["wgi"], SIG_DECLINE["vdem"], m.reduce_fh(48, 55))
        self.assertEqual(a["label"], "CONFLICT")
        self.assertEqual(a["dissenting"], ["fh"])
        self.assertEqual(a["evidence_strength"], "CONFLICT")

    def test_conflict_beats_majority(self):
        # 2 decline + 1 improve must NOT become a 2-vs-1 CONCUR vote.
        a = m.combine_agreement(SIG_DECLINE["wgi"], SIG_DECLINE["vdem"], m.reduce_fh(48, 55))
        self.assertNotIn("CONCUR", a["label"])

    def test_mixed_weak(self):
        a = m.combine_agreement(m.reduce_wgi(wrow("NO_SIG_CHANGE")), SIG_DECLINE["vdem"], NS["fh"])
        self.assertEqual(a["label"], "MIXED-WEAK")
        self.assertEqual(a["evidence_strength"], "LOW")

    def test_all_flat(self):
        a = m.combine_agreement(m.reduce_wgi(wrow("NO_SIG_CHANGE")), NS["vdem"], NS["fh"])
        self.assertEqual(a["label"], "ALL-FLAT")

    def test_insufficient_one_instrument_cannot_be_high(self):
        # Only WGI available, and SIG — but a single instrument can never triangulate.
        a = m.combine_agreement(SIG_DECLINE["wgi"], m.absent("prob_0_1"), m.absent("score_0_60"))
        self.assertEqual(a["label"], "INSUFFICIENT")
        self.assertNotEqual(a["evidence_strength"], "HIGH")

    def test_concur_without_ci_is_medium(self):
        # V-Dem + FH both SIG-decline, WGI not significant → MEDIUM, never HIGH
        # (a missing CI never masquerades as statistical significance — the USA case).
        a = m.combine_agreement(m.reduce_wgi(wrow("NO_SIG_CHANGE")),
                                SIG_DECLINE["vdem"], SIG_DECLINE["fh"])
        self.assertEqual(a["label"], "CONCUR-DECLINE")
        self.assertEqual(a["evidence_strength"], "MEDIUM")


class TestTriangulateAndConstants(unittest.TestCase):
    def test_determinism(self):
        row = wrow("DECLINE")
        a = m.triangulate_country("HUN", "Hungary", row, (0.84, 0.41), (50, 36))
        b = m.triangulate_country("HUN", "Hungary", row, (0.84, 0.41), (50, 36))
        self.assertEqual(a, b)
        self.assertEqual(a["agreement"]["label"], "CONCUR-DECLINE")

    def test_thresholds_pinned_and_wgi_reused(self):
        self.assertEqual(m.VDEM_THRESHOLD, 0.05)
        self.assertEqual(m.FH_THRESHOLD, 3.0)
        # proves the shared engine is imported, not re-derived
        self.assertAlmostEqual(m.wgi.Z90, 1.6448536269514722)


class TestCommittedArtifact(unittest.TestCase):
    """Guards the shipped derived JSON for internal consistency (no network)."""

    def setUp(self):
        path = os.path.join(os.path.dirname(__file__), "..", "data", "derived", "voice_divergence.json")
        if not os.path.exists(path):
            self.skipTest("derived artifact not generated yet (run `make divergence`)")
        with open(path, encoding="utf-8") as fh:
            self.d = json.load(fh)

    def test_labels_valid_and_counts_sum(self):
        recs = self.d["countries"]
        for r in recs:
            self.assertIn(r["agreement"]["label"], m.LABELS)
        self.assertEqual(sum(self.d["counts"].values()), len(recs))

    def test_headline_lists_internally_consistent(self):
        recs = {r["country"]: r for r in self.d["countries"]}
        for iso in self.d["headline_concur_decline_n_sig_3"]:
            a = recs[iso]["agreement"]
            self.assertEqual(a["label"], "CONCUR-DECLINE")
            self.assertEqual(a["n_sig"], 3)
        for c in self.d["conflicts"]:
            self.assertEqual(recs[c["country"]]["agreement"]["label"], "CONFLICT")


if __name__ == "__main__":
    unittest.main()
