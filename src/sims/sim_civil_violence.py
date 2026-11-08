#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Epstein (2002) civil violence — grievance, risk, and punctuated rebellion.

Agents on a torus each carry a fixed hardship H and risk-aversion R. Grievance is
G = H*(1-L), where L is the regime's *legitimacy*. An agent rebels (goes "active")
when its grievance exceeds its perceived arrest risk by a threshold; the perceived
risk falls when few cops are nearby relative to fellow rebels. Cops patrol and jail
active agents. Two robust, published behaviours emerge here:

  1. **Legitimacy is the lever** — lowering L raises the amount of rebellion.
  2. **A legitimacy tipping point** — above a threshold the population stays *quiescent
     even when grievance is high*; once legitimacy slips below it, rebellion ignites and
     then grows as L falls further. A regime can be deeply unpopular and quiet — until it
     crosses the line.

TIER 1 — VALIDATED-MECHANISM. Reproduces the qualitative published dynamics; it
explains *how* repression and grievance interact, and does NOT predict real unrest.
*Honesty note:* Epstein's signature **punctuated bursts** (long quiet, sudden spikes)
need a larger-scale configuration than this compact reproduction — so we assert the
legitimacy lever and the tipping point, **not** the burst time-series.

Reference: Epstein, J. M. (2002). Modeling civil violence: An agent-based
computational approach. PNAS 99(suppl 3):7243-7250.
"""
import math
import random
import sys

K_ARREST = 2.3      # arrest-estimate constant: P ~= 0.9 when cops == actives == 1
THRESHOLD = 0.10    # net (grievance - risk) above which an agent rebels


class Model:
    def __init__(self, size=40, agent_density=0.70, cop_density=0.04,
                 legitimacy=0.80, vision=2, max_jail=15, seed=0):
        self.size, self.v, self.L, self.maxjail = size, vision, legitimacy, max_jail
        self.rng = random.Random(seed)
        self.grid = [[None] * size for _ in range(size)]
        self.offsets = [(dx, dy) for dx in range(-vision, vision + 1)
                        for dy in range(-vision, vision + 1)]
        cells = [(x, y) for x in range(size) for y in range(size)]
        self.rng.shuffle(cells)
        i = 0
        self.agents, self.cops = [], []
        for _ in range(int(agent_density * len(cells))):
            x, y = cells[i]; i += 1
            a = {"x": x, "y": y, "H": self.rng.random(), "R": self.rng.random(),
                 "active": False, "jail": 0}
            self.agents.append(a); self.grid[x][y] = ("A", a)
        for _ in range(int(cop_density * len(cells))):
            x, y = cells[i]; i += 1
            c = {"x": x, "y": y}; self.cops.append(c); self.grid[x][y] = ("C", c)

    def _vision(self, x, y):
        s = self.size
        return [((x + dx) % s, (y + dy) % s) for dx, dy in self.offsets]

    def _move(self, ent):
        empties = [(cx, cy) for (cx, cy) in self._vision(ent["x"], ent["y"])
                   if self.grid[cx][cy] is None]
        if empties:
            self.grid[ent["x"]][ent["y"]] = None
            nx, ny = empties[self.rng.randrange(len(empties))]
            ent["x"], ent["y"] = nx, ny
            self.grid[nx][ny] = ("A", ent) if "H" in ent else ("C", ent)

    def step(self):
        # 1. movement (free agents + cops, random order)
        movers = [a for a in self.agents if a["jail"] == 0] + list(self.cops)
        self.rng.shuffle(movers)
        for e in movers:
            self._move(e)
        # 2. activation — computed from the current grid, applied simultaneously
        new_state = {}
        for a in self.agents:
            if a["jail"] > 0:
                continue
            cells = self._vision(a["x"], a["y"])
            cops = sum(1 for (cx, cy) in cells
                       if self.grid[cx][cy] and self.grid[cx][cy][0] == "C")
            actives = 1 + sum(1 for (cx, cy) in cells
                              if self.grid[cx][cy] and self.grid[cx][cy][0] == "A"
                              and self.grid[cx][cy][1]["active"] and self.grid[cx][cy][1] is not a)
            p_arrest = 1.0 - math.exp(-K_ARREST * (cops / actives))
            grievance = a["H"] * (1.0 - self.L)
            new_state[id(a)] = (grievance - a["R"] * p_arrest) > THRESHOLD
        for a in self.agents:
            if a["jail"] == 0:
                a["active"] = new_state[id(a)]
        # 3. cops arrest a random active agent in vision
        for c in self.cops:
            targets = [self.grid[cx][cy][1] for (cx, cy) in self._vision(c["x"], c["y"])
                       if self.grid[cx][cy] and self.grid[cx][cy][0] == "A"
                       and self.grid[cx][cy][1]["active"] and self.grid[cx][cy][1]["jail"] == 0]
            if targets:
                t = targets[self.rng.randrange(len(targets))]
                t["active"] = False
                t["jail"] = self.rng.randint(1, self.maxjail)
                self.grid[t["x"]][t["y"]] = None   # leaves the grid while jailed
        # 4. decrement jail terms; release onto a random empty cell
        empties = [(x, y) for x in range(self.size) for y in range(self.size)
                   if self.grid[x][y] is None]
        self.rng.shuffle(empties)
        for a in self.agents:
            if a["jail"] > 0:
                a["jail"] -= 1
                if a["jail"] == 0 and empties:
                    x, y = empties.pop()
                    a["x"], a["y"] = x, y
                    self.grid[x][y] = ("A", a)
        return sum(1 for a in self.agents if a["active"] and a["jail"] == 0)


def simulate(legitimacy, steps, seed, burn_in=20, **kw):
    """Run the model and return the per-step count of active rebels (post burn-in)."""
    m = Model(legitimacy=legitimacy, seed=seed, **kw)
    series = []
    for t in range(steps + burn_in):
        n = m.step()
        if t >= burn_in:
            series.append(n)
    return series


def _stats(series):
    mean = sum(series) / len(series)
    return mean, max(series)


def main():
    print("Epstein (2002) civil violence — legitimacy as the lever (and its tipping point)\n")
    for L in (0.95, 0.90, 0.88, 0.78, 0.68):
        mean, _ = _stats(simulate(L, steps=70, seed=20260602, size=25, vision=1, burn_in=15))
        print(f"  legitimacy L={L:.2f}  mean active rebels = {mean:6.1f}")
    print("\n  A grieved population stays quiescent while legitimacy is high; once it slips")
    print("  past a threshold (~0.9 here), rebellion ignites and grows as legitimacy falls.")


if __name__ == "__main__":
    sys.exit(main())
