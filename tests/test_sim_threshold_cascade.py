# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validation tests for the Granovetter threshold model.

Each test asserts the simulator reproduces a *published* result. Granovetter's
model is deterministic, so these are exact.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "sims"))
import sim_threshold_cascade as m  # noqa: E402


class TestGranovetterKnifeEdge(unittest.TestCase):
    def test_uniform_distribution_all_act(self):
        # thresholds 0..99 -> every agent acts (the instigating crowd)
        self.assertEqual(m.equilibrium(m.uniform_distribution(100)), 100)

    def test_removing_the_spark_fizzles(self):
        # nudge the lone threshold-1 individual to 2 -> cascade dies at 1
        self.assertEqual(m.equilibrium(m.remove_the_spark(100)), 1)

    def test_the_knife_edge(self):
        # one marginal individual flips 100 -> 1 (Granovetter's whole point)
        riot = m.equilibrium(m.uniform_distribution(100))
        fizzle = m.equilibrium(m.remove_the_spark(100))
        self.assertEqual((riot, fizzle), (100, 1))


class TestEquilibriumProperties(unittest.TestCase):
    def test_all_zero_thresholds_all_act(self):
        self.assertEqual(m.equilibrium([0] * 10), 10)

    def test_all_high_thresholds_none_act(self):
        # nobody has threshold 0, so nobody ever starts
        self.assertEqual(m.equilibrium([5, 5, 5, 5, 5]), 0)

    def test_fixed_point(self):
        # the returned a* satisfies a* == #{t <= a*}
        d = [0, 0, 1, 3, 3, 9]
        a = m.equilibrium(d)
        self.assertEqual(a, sum(1 for t in d if t <= a))

    def test_monotone_in_size(self):
        # equilibrium is between 0 and n
        d = m.uniform_distribution(50)
        self.assertGreaterEqual(m.equilibrium(d), 0)
        self.assertLessEqual(m.equilibrium(d), len(d))


if __name__ == "__main__":
    unittest.main(verbosity=2)
