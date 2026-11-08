# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validation tests for the bounded-confidence (Deffuant–Weisbuch) opinion-dynamics model.

Pins the ROBUST published results: the ε = 1/2 consensus threshold (Fortunato 2004) and the
monotone decrease of the cluster count with ε (Lorenz 2007). The ~1/(2ε) cluster count is checked
only as a loose band — it is a stochastic rule of thumb, not asserted exactly. Deterministic; the
model is seeded.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "sims"))
import sim_opinion_dynamics as m  # noqa: E402


class TestCountClusters(unittest.TestCase):
    def test_pure_counting(self):
        # two tight groups separated by a gap > ε/2 → 2 clusters; ε = 0.2 so gap thresh 0.1
        self.assertEqual(m.count_clusters([0.10, 0.11, 0.80, 0.81], 0.2), 2)
        self.assertEqual(m.count_clusters([0.5, 0.5, 0.5], 0.2), 1)
        self.assertEqual(m.count_clusters([], 0.2), 0)


class TestPublishedResults(unittest.TestCase):
    def test_consensus_above_one_half(self):
        # Fortunato 2004: for ε > 1/2 the whole population converges to ONE opinion.
        # Assert genuine CONVERGENCE — a tight final spread — not merely count_clusters==1, which a
        # spread-out *random* distribution also satisfies (ε/2 = 0.3 dwarfs the inter-point gaps), so
        # count alone would pass on a no-op model. The spread check actually constrains the dynamics.
        for eps in (0.55, 0.6):
            final = m.run(epsilon=eps, seed=0)
            self.assertLess(max(final) - min(final), 0.05, f"ε={eps} did not converge to consensus")
            self.assertEqual(m.count_clusters(final, eps), 1)

    def test_fragments_at_narrow_confidence(self):
        # narrow confidence → many mutually-deaf clusters (ε=0.05 ⇒ ~1/(2ε)=10)
        self.assertGreaterEqual(m.clusters_for(0.05), 5)

    def test_cluster_count_monotone_in_confidence(self):
        # the published qualitative law: more openness (larger ε) ⇒ never more clusters
        ks = [m.clusters_for(e) for e in (0.05, 0.1, 0.15, 0.2, 0.3, 0.45, 0.6)]
        self.assertTrue(all(a >= b for a, b in zip(ks, ks[1:])), ks)
        # and a STRICT drop end-to-end, so the test can't pass on a no-op model (which would
        # give a roughly constant count): narrow confidence fragments, wide confidence unifies.
        self.assertGreater(ks[0], ks[-1])

    def test_rule_of_thumb_band(self):
        # ~1/(2ε) as a LOOSE sanity band only (not an exact claim): ε=0.1 ⇒ ≈5
        self.assertTrue(3 <= m.clusters_for(0.1) <= 7)

    def test_deterministic(self):
        self.assertEqual(m.run(seed=0), m.run(seed=0))
        self.assertEqual(m.clusters_for(0.2), m.clusters_for(0.2))


if __name__ == "__main__":
    unittest.main()
