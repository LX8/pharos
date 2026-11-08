# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validation tests for the Epstein (2002) civil-violence model.

Asserts the published *legitimacy lever and tipping point*: a grieved population
stays quiescent while legitimacy is high, then rebellion ignites once legitimacy
slips below a threshold, and grows as it falls further. (Punctuated bursts need a
larger-scale run and are not asserted — see the module docstring.) Seeded for
determinism; small (grid 20, vision 1, 30 steps) so it runs fast in `make verify`."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "sims"))
import sim_civil_violence as m  # noqa: E402

CFG = dict(size=20, vision=1, steps=30, burn_in=10)


def mean_active(legitimacy, seed=1):
    s = m.simulate(legitimacy, seed=seed, **CFG)
    return sum(s) / len(s)


class TestLegitimacyLever(unittest.TestCase):
    def test_high_legitimacy_is_quiescent(self):
        self.assertLess(mean_active(0.95), 1.0, "a legitimate regime should stay quiet")

    def test_low_legitimacy_brings_rebellion(self):
        self.assertGreater(mean_active(0.70), 50.0, "low legitimacy should ignite rebellion")

    def test_monotone_in_legitimacy(self):
        hi, mid, lo = mean_active(0.95), mean_active(0.88), mean_active(0.70)
        self.assertGreater(lo, mid)
        self.assertGreater(mid, hi)   # the tipping point: more rebellion as legitimacy falls

    def test_full_legitimacy_zero_grievance(self):
        # G = H*(1-L); at L=1 every grievance is 0, so no one ever rebels
        self.assertEqual(mean_active(1.0), 0.0)


class TestModelInvariants(unittest.TestCase):
    def test_no_agent_is_active_while_jailed(self):
        model = m.Model(size=20, vision=1, legitimacy=0.75, seed=2)
        for _ in range(15):
            model.step()
        self.assertFalse(any(a["active"] and a["jail"] > 0 for a in model.agents))

    def test_population_densities(self):
        model = m.Model(size=20, agent_density=0.70, cop_density=0.04, seed=2)
        self.assertAlmostEqual(len(model.agents) / 400, 0.70, delta=0.02)
        self.assertAlmostEqual(len(model.cops) / 400, 0.04, delta=0.02)


if __name__ == "__main__":
    unittest.main()
