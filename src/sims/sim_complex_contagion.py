#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Centola & Macy (2007) complex contagion — why clustering matters (and where it stops).

A *simple* contagion (one contact suffices, like a virus) spreads faster as a network
gains random long-range "shortcuts" — the small-world effect. A *complex* contagion —
a behaviour adopted only after **multiple reinforcing contacts** — behaves oppositely:
it needs the local redundancy that clustering provides, and random rewiring *destroys*
the wide bridges it travels on. So on a clustered ring lattice a complex contagion
sweeps the population, but after enough rewiring it **stalls**, even as a simple
contagion only speeds up.

TIER 1 — VALIDATED-MECHANISM. Reproduces the published clustering/rewiring contrast.
It shows the *mechanism*; it does NOT predict real movements — and note the boundary
this very corpus grades CONTESTED (`ledger/SAA-010`): the *real-world* generality of
the clustering prong is disputed (the reach-vs-reinforcement trade-off, arXiv:2411.07907).
This sim demonstrates the classic model faithfully; SAA-010 records its contested edge.

Reference: Centola, D. & Macy, M. (2007). Complex Contagions and the Weakness of Long
Ties. American Journal of Sociology 113(3):702-734.
"""
import random
import sys


# ---- Watts-Strogatz ring lattice (clustering -> rewired) -------------------

def ring_lattice(n, k, p, rng):
    """Ring of n nodes, each tied to k/2 neighbours per side, each such tie rewired
    with probability p (Watts-Strogatz). p=0 is fully clustered; p->1 is random."""
    adj = [set() for _ in range(n)]
    half = k // 2
    for i in range(n):
        for j in range(1, half + 1):
            b = (i + j) % n
            adj[i].add(b)
            adj[b].add(i)
    if p > 0:
        for i in range(n):
            for j in range(1, half + 1):
                b = (i + j) % n
                if b in adj[i] and rng.random() < p:
                    adj[i].discard(b)
                    adj[b].discard(i)
                    c = rng.randrange(n)
                    while c == i or c in adj[i]:
                        c = rng.randrange(n)
                    adj[i].add(c)
                    adj[c].add(i)
    return [sorted(s) for s in adj]


# ---- spread dynamics: adopt at >= threshold ACTIVE neighbours --------------

def spread(adj, threshold, seeds):
    """Synchronous spread; a node adopts when its count of active neighbours reaches
    `threshold` (threshold=1 is simple contagion; >=2 is complex). O(rounds * edges).
    Returns (final active fraction, rounds to converge)."""
    n = len(adj)
    active = bytearray(n)
    for s in seeds:
        active[s] = 1
    rounds = 0
    while True:
        newly = [u for u in range(n)
                 if not active[u] and sum(active[w] for w in adj[u]) >= threshold]
        if not newly:
            return sum(active) / n, rounds
        for u in newly:
            active[u] = 1
        rounds += 1


def seed_block(size):
    """A contiguous seed cluster — a complex contagion (threshold>=2) cannot ignite
    from scattered singletons; it needs neighbours that already share active ties."""
    return list(range(size))


def main():
    rng = random.Random(20260602)
    n, k, seeds = 1000, 4, seed_block(6)
    print("Centola & Macy (2007) complex contagion — clustering vs random rewiring")
    print("  (n=1000, k=4, threshold T; T=1 simple, T=2 complex)\n")
    for label, p in (("clustered (p=0.0)", 0.0), ("rewired  (p=0.5)", 0.5)):
        adj = ring_lattice(n, k, p, rng)
        cf, cr = spread(adj, 2, seeds)
        sf, sr = spread(adj, 1, seeds)
        print(f"  {label}:  complex(T=2) reach={cf:5.0%}  |  simple(T=1) reach={sf:5.0%} in {sr} rounds")
    print("\n  Complex contagion sweeps the clustered net but stalls once rewired;")
    print("  simple contagion spreads either way — and faster through long ties.")


if __name__ == "__main__":
    sys.exit(main())
