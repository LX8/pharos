# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline tests for the bias-audit blind-pack generator (docs/BIAS_AUDIT_PREREGISTRATION.md §1).

Pins the properties the pre-registration depends on: full coverage, real blindness (no grade
token survives masking), determinism (two builds byte-identical, so the pack is auditable),
a faithful key, and a genuinely non-alphabetical shuffle.
"""
import json
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import bias_audit  # noqa: E402

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
LEDGER = os.path.join(REPO, "ledger")


class TestBlindPack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack, cls.key = bias_audit.build_pack(LEDGER)

    def test_covers_every_entry_exactly_once(self):
        with open(os.path.join(LEDGER, "index.json"), encoding="utf-8") as f:
            ids = {e["id"] for e in json.load(f)["entries"]}
        self.assertEqual(set(self.key.values()), ids)
        self.assertEqual(len(self.key), len(ids), "codes must map 1:1")

    def test_no_grade_token_survives_any_case(self):
        # the whole point: a single surviving token unblinds the coder. R7 review demonstrated
        # the uppercase-only v1 leaked ("Refuted pseudoscience" in a title, lowercase prose) —
        # so the three grade-loaded words must be gone in ANY case
        self.assertIsNone(re.search(r"(?i)\b(robust|contested|refuted)\b", self.pack))
        # OPEN is masked in its uppercase grade form (lowercase 'open' is ordinary English —
        # the documented §5 residual)
        self.assertNotRegex(self.pack, r"\bOPEN\b")
        self.assertNotRegex(self.pack, r"\bgrade[d]?\s+open\b")

    def test_masking_actually_fired(self):
        # SAA-028's Claim says "is ROBUST"/"is CONTESTED" in prose — the mask must have work to do
        self.assertIn(bias_audit.MASK, self.pack)

    def test_deterministic(self):
        pack2, key2 = bias_audit.build_pack(LEDGER)
        self.assertEqual(self.pack, pack2)
        self.assertEqual(self.key, key2)

    def test_shuffle_is_not_ledger_order(self):
        # if codes ran in SAA order the "shuffle" would be a label rename, not a blind
        ordered = [self.key[f"E{i:02d}"] for i in range(1, len(self.key) + 1)]
        self.assertNotEqual(ordered, sorted(ordered))

    def test_every_block_has_coding_line(self):
        self.assertEqual(self.pack.count("VALENCE (circle one)"), len(self.key))


class TestClopperPearson(unittest.TestCase):
    """The pre-registration publishes an exact 95% CI per proportion; pin it to known values."""

    def test_known_values(self):
        lo, hi = bias_audit.clopper_pearson(8, 10)
        self.assertAlmostEqual(lo, 0.4439, places=4)
        self.assertAlmostEqual(hi, 0.9748, places=4)

    def test_exact_edges(self):
        # closed-form edges: k=0 -> (0, 1-(a/2)^(1/n)); k=n -> ((a/2)^(1/n), 1)
        lo, hi = bias_audit.clopper_pearson(0, 10)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 1 - 0.025 ** 0.1, places=4)
        lo, hi = bias_audit.clopper_pearson(5, 5)
        self.assertAlmostEqual(lo, 0.025 ** 0.2, places=4)
        self.assertEqual(hi, 1.0)

    def test_empty_group_is_none(self):
        self.assertIsNone(bias_audit.clopper_pearson(0, 0))


class TestFisherExact(unittest.TestCase):
    """Pure-stdlib Fisher exact must match published values, or the whole H1 analysis is wrong."""

    def test_known_two_sided_values(self):
        self.assertAlmostEqual(bias_audit.fisher_exact(3, 1, 1, 3), 0.4857, places=4)  # tea-tasting
        self.assertAlmostEqual(bias_audit.fisher_exact(8, 2, 1, 5), 0.0350, places=4)
        self.assertAlmostEqual(bias_audit.fisher_exact(5, 5, 5, 5), 1.0, places=6)

    def test_symmetry_and_bounds(self):
        self.assertAlmostEqual(bias_audit.fisher_exact(2, 8, 8, 2), bias_audit.fisher_exact(8, 2, 2, 8))
        self.assertLessEqual(bias_audit.fisher_exact(10, 0, 0, 10), 1.0)


class TestScore(unittest.TestCase):
    KEY = {"E01": "SAA-A", "E02": "SAA-B", "E03": "SAA-C", "E04": "SAA-D", "E05": "SAA-E"}
    GRADES = {"SAA-A": "ROBUST", "SAA-B": "ROBUST", "SAA-C": "CONTESTED",
              "SAA-D": "ROBUST", "SAA-E": "OPEN"}

    def test_neutral_excluded_from_table(self):
        coded = {"E01": "D", "E02": "N", "E03": "R", "E04": "D", "E05": "R"}
        r = bias_audit.score(coded, self.KEY, self.GRADES)
        # E02 (N) excluded; D: E01(ROBUST),E04(ROBUST); R: E03(CONTESTED),E05(OPEN)
        self.assertEqual(r["table"], {"D_robust": 2, "D_not": 0, "R_robust": 0, "R_not": 2})
        self.assertEqual(r["n_neutral_or_skipped"], 1)
        self.assertEqual(r["delta_p"], 1.0)

    def test_no_skew_when_balanced(self):
        # equal ROBUST rate across valences -> delta 0, criterion cannot fire
        coded = {"E01": "D", "E02": "R", "E03": "D", "E04": "R", "E05": "N"}
        grades = {"SAA-A": "ROBUST", "SAA-B": "ROBUST", "SAA-C": "OPEN", "SAA-D": "OPEN", "SAA-E": "ROBUST"}
        r = bias_audit.score(coded, self.KEY, grades)
        self.assertEqual(r["delta_p"], 0.0)
        self.assertFalse(r["skew_detected"])

    def test_criterion_needs_both_conditions(self):
        # a large delta on tiny N has a big Fisher p -> must NOT fire (guards against small-N false alarms)
        coded = {"E01": "D", "E03": "R"}
        r = bias_audit.score(coded, self.KEY, self.GRADES)
        self.assertEqual(r["delta_p"], 1.0)              # D robust, R not
        self.assertGreater(r["fisher_p_two_sided"], 0.10)
        self.assertFalse(r["skew_detected"])             # delta passes but p does not

    def test_bad_valence_rejected(self):
        with self.assertRaises(ValueError):
            bias_audit.score({"E01": "X"}, self.KEY, self.GRADES)

    def test_real_key_and_grades_score(self):
        # smoke against the real ledger: every code -> real id -> real grade, no crash
        _, key = bias_audit.build_pack(LEDGER)
        grades = bias_audit.load_grades(LEDGER)
        coded = {c: "N" for c in key}
        r = bias_audit.score(coded, key, grades)
        self.assertEqual(r["n_coded"], 0)  # all neutral
        self.assertEqual(r["n_neutral_or_skipped"], len(key))


class TestCli(unittest.TestCase):
    def test_score_needs_key(self):
        self.assertEqual(bias_audit.main(["--score", "x.json"]), 2)

    def test_missing_ledger_is_a_clean_error(self):
        orig = bias_audit.LEDGER
        try:
            bias_audit.LEDGER = os.path.join(REPO, "no-such-ledger")
            self.assertEqual(bias_audit.main([]), 2)
        finally:
            bias_audit.LEDGER = orig


if __name__ == "__main__":
    unittest.main()
