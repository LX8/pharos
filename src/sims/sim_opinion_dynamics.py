#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded-confidence opinion dynamics — when a population converges, and when it fragments.

The Deffuant–Weisbuch model (Deffuant, Neau, Amblard & Weisbuch 2000): N agents hold a
continuous opinion in [0, 1]; a randomly met pair adjusts toward each other **only if** they
already agree within a confidence threshold ε, and otherwise ignore each other. This is the
micro-foundation under the polarization thread — it makes precise *when* talking produces
consensus and when it produces stable, mutually-deaf clusters (the ledger's SAA-026 / SAA-027).

TIER 1 — VALIDATED-MECHANISM. The robust, published results it reproduces:
  • **Consensus threshold ε = 1/2** — for ε > 1/2 the whole population converges to ONE opinion,
    essentially independent of who-meets-whom (Fortunato 2004, "Universality of the threshold…",
    arXiv:cond-mat/0406054). Below it, the population splits into clusters separated by more than ε,
    which can no longer influence one another.
  • The final **number of clusters decreases monotonically as ε increases** (Lorenz 2007 survey).
The well-known **~1/(2ε)** rule of thumb for the cluster count is *approximate and stochastic*, so
this is checked only as a loose band — **not asserted as an exact count** (the same honest-scope
discipline as the other sims). It shows the *logic* of consensus-vs-fragmentation under stated
assumptions; it does not claim any real public sorts opinions this way.

References: Deffuant, Neau, Amblard & Weisbuch (2000), "Mixing beliefs among interacting agents,"
Advances in Complex Systems 3:87–98; Fortunato (2004), Int. J. Mod. Phys. C, arXiv:cond-mat/0406054;
Lorenz (2007), "Continuous opinion dynamics under bounded confidence: a survey," IJMPC 18:1819.

Pure stdlib, seeded, deterministic — no numpy, no GPU. `make sims` runs the demo; `make verify`
validates against the published results.
"""
import random
import sys


# ---- pure, testable core ---------------------------------------------------

def run(n=200, epsilon=0.2, mu=0.5, sweeps=400, seed=0):
    """Run the Deffuant model to convergence and return the sorted final opinions.

    Each "sweep" is N random pairwise meetings, so total interactions = n * sweeps. ``mu`` in
    (0, 0.5] is the convergence rate (0.5 = meet in the middle). Deterministic for a given seed.
    """
    rng = random.Random(seed)
    op = [rng.random() for _ in range(n)]
    for _ in range(sweeps * n):
        i = rng.randrange(n)
        j = rng.randrange(n)
        if i == j:
            continue
        d = op[i] - op[j]
        if abs(d) < epsilon:           # they are within confidence — adjust toward each other
            op[i] -= mu * d
            op[j] += mu * d
    return sorted(op)


def count_clusters(sorted_op, epsilon):
    """Number of final opinion clusters. Deffuant clusters are separated by > ε and internally
    tight after convergence, so a gap exceeding ε/2 marks a new cluster. O(n)."""
    if not sorted_op:
        return 0
    clusters = 1
    for a, b in zip(sorted_op, sorted_op[1:]):
        if b - a > epsilon / 2:
            clusters += 1
    return clusters


def clusters_for(epsilon, n=200, mu=0.5, sweeps=400, seed=0):
    """Convenience: cluster count for one confidence threshold."""
    return count_clusters(run(n, epsilon, mu, sweeps, seed), epsilon)


def main():
    print("Bounded-confidence opinion dynamics (Deffuant–Weisbuch): when does talking converge?")
    print("  confidence ε   final clusters   reading")
    for eps in (0.05, 0.1, 0.15, 0.2, 0.3, 0.45, 0.6):
        k = clusters_for(eps)
        reading = "consensus" if k == 1 else f"{k} camps"
        print(f"     ε = {eps:<5}        {k:>3}            {reading}")
    print("  → above ε = 1/2 the population converges to one opinion; narrow confidence fragments it.")
    print("  Honest scope: the ε=1/2 consensus threshold + monotone fragmentation are the validated")
    print("  results; the exact cluster count is a stochastic ~1/(2ε) rule of thumb, not asserted.")


if __name__ == "__main__":
    sys.exit(main())
