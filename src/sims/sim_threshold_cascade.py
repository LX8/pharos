#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Granovetter (1978) threshold model of collective behaviour — the knife-edge.

Each agent i acts once the number of others already acting reaches its threshold
t_i. The equilibrium is the fixed point of F(a) = #{i : t_i <= a}, found by
iterating from a = 0. Granovetter's famous result: two crowds with *almost
identical* threshold distributions can reach opposite outcomes — a near-universal
riot vs. nothing — because of a single individual at the margin.

TIER 1 — VALIDATED-MECHANISM. Reproduces a published, exact result (deterministic,
no RNG). It explains *how* a threshold distribution decides a cascade; it does NOT
predict whether any real crowd will act. See docs/sims/README.md.

Reference: Granovetter, M. (1978). Threshold Models of Collective Behavior.
American Journal of Sociology 83(6):1420-1443.
"""
import sys


# ---- pure, testable core ---------------------------------------------------

def equilibrium(thresholds):
    """Number of agents acting at equilibrium.

    F(a) = #{i : t_i <= a}; the equilibrium is the smallest fixed point, reached
    by iterating F from a = 0 (monotone, so it always converges).
    """
    a = 0
    while True:
        new_a = sum(1 for t in thresholds if t <= a)
        if new_a == a:
            return a
        a = new_a


def uniform_distribution(n=100):
    """Granovetter's instigating crowd: thresholds 0, 1, 2, ..., n-1 -> all act."""
    return list(range(n))


def remove_the_spark(n=100):
    """The same crowd with the lone threshold-1 individual nudged to 2.

    A single marginal change: the cascade now dies after the one instigator.
    """
    d = list(range(n))
    d[1] = 2  # the person who would have gone at "1 other acting" now needs 2
    return d


def main():
    n = 100
    a_riot = equilibrium(uniform_distribution(n))
    a_fizzle = equilibrium(remove_the_spark(n))
    print("Granovetter threshold model — the knife-edge")
    print(f"  uniform thresholds 0..{n-1}            -> {a_riot} of {n} act  (riot)")
    print(f"  one person nudged from t=1 to t=2     -> {a_fizzle} of {n} act  (fizzle)")
    print(f"  a single marginal individual flips {a_riot} -> {a_fizzle}.")
    print("  Lesson: identical-looking crowds, opposite outcomes. Mechanism, not prediction.")


if __name__ == "__main__":
    sys.exit(main())
