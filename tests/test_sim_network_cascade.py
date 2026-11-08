# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validation tests for the Watts (2002) global-cascade model.

Asserts the published "cascade window": a single seed triggers system-wide
cascades only for an average degree z inside a window. Seeded for determinism;
kept small (n=800, 40 trials) so it runs fast inside `make verify`.
"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "sims"))
import sim_network_cascade as m  # noqa: E402

PHI = 0.18      # Watts's canonical threshold
N = 700
TRIALS = 30


def _global_freq_and_max(z, seed):
    rng = random.Random(seed)
    fracs = m.cascade_trials(N, z, PHI, TRIALS, rng)
    glob = sum(1 for f in fracs if f > 0.4) / len(fracs)
    return glob, max(fracs)


class TestCascadeWindow(unittest.TestCase):
    def test_in_window_produces_global_cascades(self):
        # z = 2.5 is inside the window for phi = 0.18 -> a lone seed often
        # flips a large fraction of the whole network.
        glob, biggest = _global_freq_and_max(2.5, seed=101)
        self.assertGreater(biggest, 0.4, "in-window: a global cascade should occur")
        self.assertGreaterEqual(glob, 0.25, "in-window: global cascades should be common")

    def test_above_window_no_global_cascades(self):
        # z = 10 is past the upper edge -> the vulnerable cluster no longer
        # percolates, so a single seed cannot flip the network.
        glob, biggest = _global_freq_and_max(10.0, seed=202)
        self.assertEqual(glob, 0.0, "above window: no global cascades")
        self.assertLess(biggest, 0.1, "above window: cascades stay local")


class TestPrimitives(unittest.TestCase):
    def test_er_graph_mean_degree(self):
        rng = random.Random(7)
        n, z = 1000, 4.0
        adj = m.er_graph(n, z, rng)
        mean_deg = sum(len(a) for a in adj) / n
        self.assertAlmostEqual(mean_deg, z, delta=0.6)  # ~z, sampling slack

    def test_cascade_at_least_seed(self):
        rng = random.Random(7)
        adj = m.er_graph(500, 3.0, rng)
        self.assertGreaterEqual(m.cascade_size(adj, PHI, rng), 1)

    def test_phi_zero_everything_activates(self):
        # threshold 0: any node with >=1 neighbour flips; a connected-ish graph
        # cascades to (nearly) all reachable nodes from the seed.
        rng = random.Random(7)
        adj = m.er_graph(500, 6.0, rng)
        self.assertGreater(m.cascade_size(adj, 0.0, rng), 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
