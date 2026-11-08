# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validation tests for the reverse-dominance / egalitarian-revolution model.

Asserts (a) the Lanchester square-law levelling threshold (k² > r, exact — the
independently-validated published result) and (b) that the level-or-submit best-response
dynamic is, *by construction*, a deterministic classifier whose separatrix equals that
threshold (test_revolution_is_threshold_classifier pins this honestly — it is NOT a claim
to reproduce Gavrilets' emergent basin). Deterministic; no RNG.
"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "sims"))
import sim_reverse_dominance as m  # noqa: E402


class TestLanchesterThreshold(unittest.TestCase):
    def test_exact_values(self):
        # smallest k with k^2 > r (a tie k^2 == r is mutual destruction, not a win)
        self.assertEqual(m.min_winning_coalition(1), 2)
        self.assertEqual(m.min_winning_coalition(4), 3)
        self.assertEqual(m.min_winning_coalition(16), 5)
        self.assertEqual(m.min_winning_coalition(64), 9)
        self.assertEqual(m.min_winning_coalition(256), 17)

    def test_threshold_invariant(self):
        # k_min is the *smallest* coalition that strictly wins
        for r in (0.5, 1, 2, 3, 7, 25, 100, 999):
            k = m.min_winning_coalition(r)
            self.assertGreater(k * k, r)                 # k wins
            self.assertLessEqual((k - 1) * (k - 1), r)   # k-1 does not

    def test_weaker_dominator_needs_one(self):
        # a "dominator" weaker than a single subordinate is levelled by one
        self.assertEqual(m.min_winning_coalition(0.5), 1)

    def test_numbers_crush_strength(self):
        # because power ~ k^2, the critical mass grows only like sqrt(r):
        # a handful levels a vastly stronger tyrant
        for r in (16, 64, 256, 1024):
            k = m.min_winning_coalition(r)
            self.assertLessEqual(k, math.isqrt(int(r)) + 1)
            self.assertLess(k, r)  # far fewer than the strength ratio

    def test_coalition_wins_rule(self):
        self.assertTrue(m.coalition_wins(4, 9))    # 16 > 9
        self.assertFalse(m.coalition_wins(3, 9))   # 9 == 9, a tie, not a win


class TestEgalitarianRevolution(unittest.TestCase):
    def test_bistable_tipping_at_critical_mass(self):
        n, r = 30, 64
        kmin = m.min_winning_coalition(r)  # 9
        self.assertEqual(m.egalitarian_revolution(n, r, kmin)["outcome"], "EGALITARIAN")
        self.assertEqual(m.egalitarian_revolution(n, r, kmin - 1)["outcome"], "DESPOTIC")

    def test_converges_to_extremes(self):
        n, r = 40, 100
        kmin = m.min_winning_coalition(r)
        above = m.egalitarian_revolution(n, r, kmin + 2)
        below = m.egalitarian_revolution(n, r, kmin - 2)
        self.assertEqual(above["outcome"], "EGALITARIAN")
        self.assertGreaterEqual(above["w"], kmin)        # settled near full participation
        self.assertEqual(below["outcome"], "DESPOTIC")
        self.assertLess(below["w"], kmin)                # collapsed

    def test_revolution_is_threshold_classifier(self):
        # Honest pin of what the dynamic actually is: a deterministic classifier whose
        # separatrix equals the Lanchester critical mass by construction (NOT an emergent
        # basin). The converged outcome must equal the one-line threshold comparison for
        # every reachable input — if a future edit makes the dynamics genuinely emergent,
        # this test should be revisited rather than silently kept.
        for n in (5, 12, 30, 59):
            for r in (0.5, 1, 4, 16, 64, 256):
                kmin = m.min_winning_coalition(r)
                if kmin > n:
                    continue
                for w0 in range(0, n + 1):
                    expected = "EGALITARIAN" if w0 >= kmin else "DESPOTIC"
                    self.assertEqual(m.egalitarian_revolution(n, r, w0)["outcome"], expected)

    def test_unbeatable_dominator_stays_despotic(self):
        # if even all N subordinates cannot meet the square-law threshold, no revolt wins
        n = 5
        r = 100  # needs k_min = 11 > 5
        self.assertGreater(m.min_winning_coalition(r), n)
        self.assertEqual(m.egalitarian_revolution(n, r, n)["outcome"], "DESPOTIC")


if __name__ == "__main__":
    unittest.main(verbosity=2)
