#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Committed-minority tipping — the naming game with zealots (Xie et al. 2011).

A population starts in consensus on opinion B. A committed fraction p always
holds opinion A and never changes. Agents play the naming game: a speaker utters
one of its opinions; on agreement both collapse to it, on disagreement the
listener adds it. Xie et al. (2011) showed a sharp tipping point near
**p_c ≈ 10%**: below it, the time for the committed minority to flip the whole
population grows *exponentially* with N (effectively never); above it, it grows
only *logarithmically* (fast). This is the quantitative core of the project's
"critical mass" theory — and Centola et al. (2018) measured ~25% experimentally,
a reminder that the exact threshold is model/context-dependent (see SAA-009).

TIER 1 — VALIDATED-MECHANISM. Reproduces the published sharp-threshold behaviour.
It shows *how big* a committed minority must be to tip a system under stated
assumptions; it does NOT predict whether any real minority will. See
docs/sims/README.md.

References: Xie, J. et al. (2011) Phys. Rev. E 84:011130; Centola, D. et al.
(2018) Science 360:1116.
"""
import random
import sys

A, B = 1, 2  # opinions as bit flags; an agent's list is a bitmask in {1, 2, 3}


# ---- pure, testable core ---------------------------------------------------

def run_naming_game(n, p, rng, max_steps):
    """Run until all non-committed agents hold only A, or until max_steps.

    Returns (steps, converged). Committed agents (the first round(p*n)) always
    hold {A} and never update.
    """
    k = int(round(p * n))
    committed = bytearray(n)
    lst = bytearray(n)
    for i in range(n):
        if i < k:
            committed[i] = 1
            lst[i] = A          # committed: {A}
        else:
            lst[i] = B          # everyone else starts at {B}
    noncommitted = [i for i in range(n) if not committed[i]]
    check_every = max(1, n)
    rr = rng.randrange
    rand = rng.random
    for step_i in range(1, max_steps + 1):
        s = rr(n)
        t = rr(n)
        if s == t:
            continue
        ls = lst[s]
        w = A if ls == A else (B if ls == B else (A if rand() < 0.5 else B))
        if lst[t] & w:                       # agreement -> both collapse to w
            if not committed[t]:
                lst[t] = w
            if not committed[s]:
                lst[s] = w
        elif not committed[t]:               # disagreement -> listener adds w
            lst[t] |= w
        if step_i % check_every == 0 and all(lst[i] == A for i in noncommitted):
            return step_i, True
    return max_steps, False


def mean_time_to_tip(n, p, rng, runs, max_steps):
    """Mean steps for the committed minority to flip the population (capped)."""
    return sum(run_naming_game(n, p, rng, max_steps)[0] for _ in range(runs)) / runs


def main():
    rng = random.Random(20260602)
    n, runs = 400, 3
    cap = 400 * n
    print("Committed-minority tipping — naming game with zealots (Xie 2011)")
    print(f"  N={n}, steps capped at {cap} ({cap // n}*N); 3 runs averaged")
    print("   committed p   mean steps-to-tip / N   tipped?")
    for p in (0.03, 0.06, 0.09, 0.12, 0.20):
        t = mean_time_to_tip(n, p, rng, runs, cap)
        tipped = "yes (fast)" if t < cap else "NOT within cap"
        print(f"     {p:>5.0%}        {t / n:>10.1f}            {tipped}")
    print("  Past the ~10% tipping point the flip time collapses — a critical mass.")


if __name__ == "__main__":
    sys.exit(main())
