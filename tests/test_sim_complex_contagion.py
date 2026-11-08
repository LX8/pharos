# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validation tests for the Centola & Macy (2007) complex-contagion model.

Asserts the published contrast: a complex contagion (needs >=2 reinforcing contacts)
sweeps a clustered ring lattice but stalls once the network is randomly rewired, while
a simple contagion spreads either way — and faster through the long ties. Seeded for
determinism; small (n=600) so it runs fast in `make verify`."""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "sims"))
import sim_complex_contagion as m  # noqa: E402

N, K = 600, 4
SEEDS = m.seed_block(6)


def run(p, threshold, seed):
    rng = random.Random(seed)
    adj = m.ring_lattice(N, K, p, rng)
    return m.spread(adj, threshold, SEEDS)


class TestComplexContagion(unittest.TestCase):
    def test_complex_sweeps_clustered_network(self):
        frac, _ = run(0.0, 2, seed=11)
        self.assertGreater(frac, 0.9, "complex contagion should sweep the clustered lattice")

    def test_complex_stalls_when_rewired(self):
        frac, _ = run(0.5, 2, seed=11)
        self.assertLess(frac, 0.2, "complex contagion should stall once long ties replace clustering")

    def test_simple_spreads_either_way(self):
        self.assertGreater(run(0.0, 1, seed=11)[0], 0.9)
        self.assertGreater(run(0.5, 1, seed=11)[0], 0.9)

    def test_long_ties_speed_up_simple_contagion(self):
        _, clustered_rounds = run(0.0, 1, seed=11)
        _, rewired_rounds = run(0.5, 1, seed=11)
        self.assertLess(rewired_rounds, clustered_rounds,
                        "long ties should make a simple contagion converge in fewer rounds")


class TestPrimitives(unittest.TestCase):
    def test_ring_lattice_mean_degree(self):
        rng = random.Random(3)
        adj = m.ring_lattice(N, K, 0.0, rng)
        self.assertAlmostEqual(sum(len(a) for a in adj) / N, K, delta=0.001)

    def test_single_seed_cannot_ignite_complex(self):
        # one scattered seed has no neighbour with 2 active ties -> never spreads
        rng = random.Random(3)
        adj = m.ring_lattice(N, K, 0.0, rng)
        frac, _ = m.spread(adj, 2, [0])
        self.assertLess(frac, 0.01)


if __name__ == "__main__":
    unittest.main()
