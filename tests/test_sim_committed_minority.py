# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validation tests for the committed-minority naming game (Xie et al. 2011).

Asserts the published sharp tipping point near ~10%: below it the committed
minority cannot flip the population within a large budget; above it the flip is
fast. Seeded for determinism; kept small (n=250) so it runs fast.
"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "sims"))
import sim_committed_minority as m  # noqa: E402

N = 250
CAP = 80 * N  # above-threshold tips in ~20*N; below needs exponentially more


class TestTippingPoint(unittest.TestCase):
    def test_below_threshold_does_not_tip(self):
        # p = 4% << ~10%: the minority cannot flip the population within budget
        steps, converged = m.run_naming_game(N, 0.04, random.Random(1), CAP)
        self.assertFalse(converged, "below threshold should NOT tip within budget")
        self.assertEqual(steps, CAP)

    def test_above_threshold_tips_fast(self):
        # p = 20% >> ~10%: a critical mass flips the whole population quickly
        steps, converged = m.run_naming_game(N, 0.20, random.Random(2), CAP)
        self.assertTrue(converged, "above threshold should tip")
        self.assertLess(steps, 60 * N, "above threshold should tip *fast*")

    def test_time_collapses_across_the_threshold(self):
        # the signature: flip time drops sharply from below to above ~10%
        slow = m.mean_time_to_tip(N, 0.06, random.Random(3), runs=1, max_steps=CAP)
        fast = m.mean_time_to_tip(N, 0.20, random.Random(3), runs=1, max_steps=CAP)
        self.assertLess(fast, slow / 2.0)


class TestProperties(unittest.TestCase):
    def test_no_committed_never_introduces_A(self):
        # with p = 0 there is no zealot to introduce A, so it never tips
        _, converged = m.run_naming_game(N, 0.0, random.Random(4), 50 * N)
        self.assertFalse(converged)

    def test_all_committed_is_trivially_A(self):
        # p = 1.0: everyone is committed to A -> consensus is immediate/vacuous
        _, converged = m.run_naming_game(50, 1.0, random.Random(5), 50 * 50)
        self.assertTrue(converged)

    def test_more_committed_never_slower_on_average(self):
        # monotone-ish: a larger committed fraction tips at least as fast
        t_small = m.mean_time_to_tip(N, 0.12, random.Random(6), runs=1, max_steps=CAP)
        t_large = m.mean_time_to_tip(N, 0.25, random.Random(6), runs=1, max_steps=CAP)
        self.assertLessEqual(t_large, t_small + 5 * N)  # slack for stochasticity


if __name__ == "__main__":
    unittest.main(verbosity=2)
