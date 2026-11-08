# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline, deterministic tests for the WGI governance core math.

The network fetch is NOT tested here (that would be flaky); the load-bearing
*calculation* — uncertainty-aware change detection, shared across all six
governance dimensions — is pure and fully tested.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "indicators"))
import wgi_governance as m  # noqa: E402


class TestDimensions(unittest.TestCase):
    def test_six_dimensions(self):
        self.assertEqual(set(m.DIMENSIONS), {"VA", "RL", "CC", "GE", "RQ", "PV"})


class TestPhi(unittest.TestCase):
    def test_center(self):
        self.assertAlmostEqual(m.phi(0.0), 0.5, places=12)

    def test_90th(self):
        self.assertAlmostEqual(m.phi(m.Z90), 0.95, places=4)

    def test_monotonic(self):
        self.assertLess(m.phi(-1.0), m.phi(0.0))
        self.assertLess(m.phi(0.0), m.phi(1.0))


class TestSeFromCi(unittest.TestCase):
    def test_known(self):
        self.assertAlmostEqual(m.se_from_ci(-m.Z90, m.Z90), 1.0, places=12)


class TestComputeChange(unittest.TestCase):
    def test_meaningful_decline(self):
        r = m.compute_change(70, 66, 74, 50, 46, 54)
        self.assertEqual(r["verdict"], "DECLINE")
        self.assertLess(r["z"], -m.Z90)
        self.assertAlmostEqual(r["change"], -20.0, places=6)

    def test_meaningful_improve(self):
        r = m.compute_change(40, 37, 43, 55, 52, 58)
        self.assertEqual(r["verdict"], "IMPROVE")
        self.assertGreater(r["z"], m.Z90)

    def test_within_noise(self):
        r = m.compute_change(70, 60, 80, 72, 62, 82)
        self.assertEqual(r["verdict"], "NO_SIG_CHANGE")

    def test_identical_is_zero(self):
        r = m.compute_change(50, 45, 55, 50, 45, 55)
        self.assertEqual(r["change"], 0.0)
        self.assertEqual(r["z"], 0.0)
        self.assertEqual(r["verdict"], "NO_SIG_CHANGE")

    def test_threshold_behavior(self):
        self.assertAlmostEqual(2.0 * (1.0 - m.phi(m.Z90)), 0.10, places=3)
        se_diff = m.math.sqrt(2.0)  # se per year = 1 -> CI half-width == Z90

        def verdict_for(change):
            return m.compute_change(50, 50 - m.Z90, 50 + m.Z90,
                                    50 + change, 50 + change - m.Z90,
                                    50 + change + m.Z90)["verdict"]

        # clearly past the 90% bar -> flagged; clearly short of it -> noise
        # (the exact knife-edge z==Z90 is floating-point ambiguous and not probed)
        self.assertEqual(verdict_for(+1.01 * m.Z90 * se_diff), "IMPROVE")
        self.assertEqual(verdict_for(-1.01 * m.Z90 * se_diff), "DECLINE")
        self.assertEqual(verdict_for(+0.99 * m.Z90 * se_diff), "NO_SIG_CHANGE")

    def test_ci_ordering_sanity(self):
        r = m.compute_change(60, 57, 63, 45, 42, 48)
        self.assertGreater(r["se_diff"], 0.0)
        self.assertLess(r["change"], 0.0)
        self.assertEqual(r["verdict"], "DECLINE")


class TestCrossYearCorrelation(unittest.TestCase):
    """The headline test treats the two WGI estimates as independent (rho=0). WGI's
    overlapping sources make the true rho positive; for a change test rho=0 is the
    conservative choice (flags fewest). rho is an option, defaulting to 0 so the
    committed headline is unchanged, with a sensitivity sweep reporting robustness."""

    def test_rho_defaults_to_zero_backcompat(self):
        # omitting rho reproduces the original independence assumption exactly
        args = (70, 66, 74, 50, 46, 54)
        self.assertEqual(m.compute_change(*args), m.compute_change(*args, rho=0.0))

    def test_positive_rho_shrinks_se_diff_and_inflates_abs_z(self):
        # for a difference of positively-correlated estimates, shared measurement
        # error partially cancels -> se_diff falls, |z| rises, so rho=0 is conservative
        args = (70, 66, 74, 50, 46, 54)
        r0 = m.compute_change(*args, rho=0.0)
        r_hi = m.compute_change(*args, rho=0.7)
        self.assertLess(r_hi["se_diff"], r0["se_diff"])
        self.assertGreater(abs(r_hi["z"]), abs(r0["z"]))

    def test_rho_near_one_for_equal_se_is_small(self):
        # degenerate check: equal SEs at rho->1 leave only measurement-noise difference
        r = m.compute_change(50, 45, 55, 40, 35, 45, rho=0.99)  # se1==se2==~3.04
        self.assertGreater(r["se_diff"], 0.0)            # never negative (guarded)
        self.assertLess(r["se_diff"], 1.0)               # but much smaller than rho=0


if __name__ == "__main__":
    unittest.main(verbosity=2)
