#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Watts (2002) global cascades on a random network — the "cascade window".

Each node flips to active when the *fraction* of its neighbours that are active
reaches its threshold phi. A single seed is placed at random; the cascade
propagates until stable. Watts's central result: system-wide ("global") cascades
occur only inside a window of average degree z — too sparse and the network is
disconnected; too dense and no node is easily swayed (the "vulnerable cluster"
stops percolating). A lone seed can then flip a whole population, or nothing.

TIER 1 — VALIDATED-MECHANISM. Reproduces the published cascade-window phenomenon.
It explains *how/when* a small trigger can cascade; it does NOT predict real
events. See docs/sims/README.md.

Reference: Watts, D. J. (2002). A simple model of global cascades on random
networks. PNAS 99(9):5766-5771.
"""
import math
import random
import sys
from collections import deque


# ---- graph (Erdos-Renyi, O(n+m) Batagelj-Brandes) --------------------------

def er_graph(n, z, rng):
    """Sparse G(n, p) adjacency lists with mean degree z (p = z/(n-1))."""
    adj = [[] for _ in range(n)]
    if n < 2 or z <= 0:
        return adj
    p = min(1.0, z / (n - 1))
    if p >= 1.0:
        return [[j for j in range(n) if j != i] for i in range(n)]
    log1mp = math.log(1.0 - p)
    v, w = 1, -1
    while v < n:
        w += 1 + int(math.log(1.0 - rng.random()) / log1mp)
        while w >= v and v < n:
            w -= v
            v += 1
        if v < n:
            adj[v].append(w)
            adj[w].append(v)
    return adj


# ---- cascade dynamics (pure, given a graph + rng) --------------------------

def cascade_size(adj, phi, rng):
    """Activate one random seed; spread by the fraction->=phi rule; return size."""
    n = len(adj)
    active = bytearray(n)
    seed = rng.randrange(n)
    active[seed] = 1
    queue = deque(adj[seed])
    while queue:
        u = queue.popleft()
        if active[u]:
            continue
        deg = len(adj[u])
        if deg == 0:
            continue
        if sum(active[w] for w in adj[u]) / deg >= phi:
            active[u] = 1
            queue.extend(w for w in adj[u] if not active[w])
    return sum(active)


def cascade_trials(n, z, phi, trials, rng):
    """Return the cascade size (as a fraction of n) for each of `trials` seeds."""
    out = []
    for _ in range(trials):
        adj = er_graph(n, z, rng)
        out.append(cascade_size(adj, phi, rng) / n)
    return out


def main():
    rng = random.Random(20260602)
    n, phi, trials = 1500, 0.18, 60
    print("Watts (2002) global cascades — the cascade window  (phi = 0.18)")
    for z in (1.5, 2.5, 4.0, 8.0):
        fr = cascade_trials(n, z, phi, trials, rng)
        glob = sum(1 for f in fr if f > 0.4) / trials
        biggest = max(fr)
        tag = "IN window" if glob > 0.02 else "outside"
        print(f"  z={z:>4}  global-cascade freq={glob:5.0%}  largest={biggest:5.0%}  [{tag}]")
    print("  Global cascades from a single seed appear only inside the window.")


if __name__ == "__main__":
    sys.exit(main())
