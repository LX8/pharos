#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reverse dominance — how a coalition of the weak can level a strong dominator.

Boehm's "reverse dominance hierarchy": subordinates *collectively* suppress a
would-be dominator. The mechanism's quantitative core is **Lanchester's square
law** of combat (Johnson & MacKay 2015): a force's fighting power scales with the
*square* of its numbers times individual effectiveness. So a coalition of k
subordinates (effectiveness 1) overpowers a single dominator of effectiveness r
**iff k² > r** — numbers crush individual strength (k ≈ √r levellers beat an
r-times-stronger tyrant). Whether the coalition actually forms is then a
collective-action problem with a tipping point. Gavrilets et al.'s "egalitarian
revolution" is the *inspiration* for that framing — an emergent bistable basin from
coupled payoff dynamics; here we do not reproduce that emergence, we show the simpler
fact that the Lanchester critical mass is the **separatrix of a level-or-submit
best-response dynamic by construction**. This is the anthropology of containing tyranny
meeting the project's own critical-mass theory ([[SAA-008]], [[SAA-012]]).

TIER 1 — VALIDATED-MECHANISM. The validated published result is the Lanchester-square
levelling threshold (exact); `egalitarian_revolution()` then *illustrates* that same
threshold as a deterministic tipping point — it is a thin best-response classifier whose
separatrix equals k_min by construction, **not** an independent reproduction of Gavrilets'
emergent basin. It shows the *logic* of reverse dominance under stated assumptions; it does
NOT establish that real societies do this — the empirical claim (ledger SAA-012) is
**CONTESTED**. See docs/sims/README.md.

References: Boehm (1993/2001); Gavrilets, Duenez-Guzman & Vose (2008), PLOS ONE
"Dynamics of Alliance Formation and the Egalitarian Revolution"; Johnson & MacKay
(2015), Evolution & Human Behavior, "Fight the power: Lanchester's laws."
"""
import math
import sys


# ---- pure, testable core ---------------------------------------------------

def min_winning_coalition(strength_ratio):
    """Smallest coalition size k that overpowers a dominator of relative
    effectiveness `strength_ratio` under Lanchester's square law (k² > r).

    A tie (k² == r) is mutual destruction, not a successful levelling, so the
    inequality is strict. r < 1 (a dominator weaker than one subordinate) → 1.
    """
    k = 1
    while k * k <= strength_ratio:
        k += 1
    return k


def coalition_wins(k, strength_ratio):
    """True iff k subordinates (effectiveness 1) overpower the dominator (square law)."""
    return k * k > strength_ratio


def egalitarian_revolution(n_subordinates, strength_ratio, initial_committed, rounds=60):
    """Deterministic level-or-submit best-response dynamic — a thin classifier on k_min.

    Each round subordinates move toward the *winning* side: committing to level is best
    when the coalition would already win (free-riders are shamed/excluded), and a failed
    revolt is punished, so support collapses when it would lose. With this step
    best-response the side of the Lanchester critical mass is invariant, so the dynamic is
    bistable with its **separatrix exactly at k_min by construction**: it converges to
    EGALITARIAN iff `initial_committed >= min_winning_coalition`, else DESPOTIC. We pin
    that (modest) property honestly rather than claim an emergent Gavrilets basin — the
    only independently-validated result here is the Lanchester threshold itself.
    """
    kmin = min_winning_coalition(strength_ratio)
    if kmin > n_subordinates:
        return {"outcome": "DESPOTIC", "w": 0.0, "kmin": kmin, "note": "unbeatable even by all"}
    w = float(initial_committed)
    for _ in range(rounds):
        target = float(n_subordinates) if w >= kmin else 0.0
        w += 0.34 * (target - w)  # partial best-response adjustment
    outcome = "EGALITARIAN" if w >= kmin else "DESPOTIC"
    return {"outcome": outcome, "w": round(w, 1), "kmin": kmin}


def main():
    print("Reverse dominance — Lanchester square law: a coalition levels a tyrant iff k² > r")
    print("  dominator strength r   critical mass to level (k_min)   √r")
    for r in (1, 4, 16, 64, 256, 1024):
        print(f"     r={r:>5}                k_min = {min_winning_coalition(r):>3}                  {math.sqrt(r):.0f}")
    print("  → numbers crush strength: ~√r levellers beat an r-times-stronger dominator.")
    print()
    n, r = 30, 64  # 30 subordinates vs a dominator 64x as strong (k_min = 9)
    kmin = min_winning_coalition(r)
    print(f"Egalitarian revolution (N={n} subordinates, dominator r={r}, critical mass k_min={kmin}):")
    for w0 in (kmin - 1, kmin, kmin + 3):
        res = egalitarian_revolution(n, r, w0)
        print(f"   start committed={w0:>2}  ->  {res['outcome']}  (settles at {res['w']})")
    print("  Bistable: below the critical mass → despotism; at/above it → the many level the one.")


if __name__ == "__main__":
    sys.exit(main())
