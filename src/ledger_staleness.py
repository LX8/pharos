# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Ledger staleness gate — make maintainer lapse *loud*.

A living, self-falsifying evidence ledger is a perpetual-maintenance object: its
whole value is that it is never finished. The failure mode the plan-for-peace
self-verification graded SERIOUS (R5) is that, the moment maintenance lapses, the
ledger does not fail loudly — it *freezes mid-update and rots into the exact
"stale authority" the project exists to oppose*, still wearing the credibility
uniform while a grade quietly becomes a lie because the replication that should
have downgraded it was never entered.

This module turns that silent rot into an announced fact. Every entry carries a
`last_reviewed` date and a `review_interval_days`; once more than the interval has
elapsed, the entry is STALE and the gate fails (wired into `make verify`). Lapse
becomes self-announcing honest silence instead of false authority — the *manage*
step of the ledger's write -> manage -> read cycle.

Pure stdlib, no pip. The core (`parse_frontmatter`, `is_stale`, `entry_status`)
is pure and fully unit-tested; only `main()` reads the clock.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import date, datetime

GRADES = ("ROBUST", "CONTESTED", "OPEN", "REFUTED")

# Live debates must be re-checked sooner than settled questions. CONTESTED/OPEN
# claims sit closest to the moving frontier, so they get the shortest leash.
DEFAULT_INTERVAL_DAYS = {
    "ROBUST": 540,
    "CONTESTED": 270,
    "OPEN": 180,
    "REFUTED": 540,
}
FALLBACK_INTERVAL_DAYS = 365  # used only if an entry's grade is unrecognized


def parse_frontmatter(text):
    """Minimal YAML-frontmatter scalar parser (stdlib only, no PyYAML).

    Returns the top-level ``key: value`` scalars in the first ``---`` block. List
    blocks (e.g. ``sources:``) and their items are skipped — the gate only needs
    scalars (id, grade, verified, last_reviewed, review_interval_days).
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    meta = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line or line[0] in (" ", "\t", "-"):  # nested / list line — skip
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        val = val.strip().strip('"').strip("'")
        if val == "":  # parent of a block (e.g. `sources:`) — no scalar value
            continue
        meta[key.strip()] = val
    return meta


def read_entries(ledger_dir):
    """O(n) over the ledger. (filename, frontmatter-meta) for every ``SAA-*.md``, sorted by filename.

    The single shared "what counts as a ledger entry" rule — pharos, the digest, and this gate
    all read the ledger through it, so the definition can't drift between modules.
    """
    out = []
    for name in sorted(os.listdir(ledger_dir)):
        if name.startswith("SAA-") and name.endswith(".md"):
            with open(os.path.join(ledger_dir, name), encoding="utf-8") as fh:
                out.append((name, parse_frontmatter(fh.read())))
    return out


def _parse_date(s):
    return datetime.strptime(str(s).strip(), "%Y-%m-%d").date()


def review_interval(meta):
    """Days an entry may go un-reviewed: explicit override, else grade default."""
    raw = meta.get("review_interval_days")
    if raw is not None and str(raw).strip() != "":
        return int(raw)
    return DEFAULT_INTERVAL_DAYS.get(str(meta.get("grade", "")).upper(), FALLBACK_INTERVAL_DAYS)


def last_reviewed(meta):
    """Reference date for staleness: ``last_reviewed`` if present, else ``verified``."""
    raw = meta.get("last_reviewed") or meta.get("verified")
    return _parse_date(raw) if raw else None


def is_stale(reviewed, interval_days, today):
    """O(1). Stale once strictly more than the interval has elapsed since review.

    An entry with no review date is treated as stale: it cannot be vouched for.
    """
    if reviewed is None:
        return True
    return (today - reviewed).days > interval_days


def entry_status(meta, today):
    """Pure per-entry verdict — everything the report and the gate need."""
    reviewed = last_reviewed(meta)
    interval = review_interval(meta)
    age = None if reviewed is None else (today - reviewed).days
    return {
        "id": meta.get("id", "?"),
        "grade": meta.get("grade", "?"),
        "reviewed": reviewed.isoformat() if reviewed else None,
        "interval_days": interval,
        "age_days": age,
        "days_left": None if age is None else interval - age,
        "stale": is_stale(reviewed, interval, today),
    }


def scan(ledger_dir, today):
    """O(n) over ledger entries. Returns one status dict per ``SAA-*.md`` file."""
    out = []
    for name, meta in read_entries(ledger_dir):
        status = entry_status(meta, today)
        status["file"] = name
        out.append(status)
    return out


def _default_ledger_dir():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "ledger"))


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Ledger staleness gate: fail if any entry is past its review interval."
    )
    ap.add_argument("--ledger", default=_default_ledger_dir(), help="ledger directory")
    ap.add_argument("--today", default=None, help="YYYY-MM-DD; defaults to the system date")
    ap.add_argument("--warn", action="store_true", help="report but never fail (exit 0)")
    args = ap.parse_args(argv)

    today = _parse_date(args.today) if args.today else date.today()
    rows = scan(args.ledger, today)
    stale = [r for r in rows if r["stale"]]

    print(f"ledger staleness @ {today.isoformat()} — {len(rows)} entries, {len(stale)} stale")
    for r in rows:
        flag = "STALE" if r["stale"] else "ok"
        left = "n/a" if r["days_left"] is None else f"{r['days_left']:+d}d"
        print(
            f"  [{flag:>5}] {r['id']:<8} {str(r['grade']):<10} "
            f"reviewed {r['reviewed']}  interval {r['interval_days']}d  ({left})"
        )
    if stale and not args.warn:
        print(
            f"FAIL: {len(stale)} entry(ies) past review interval — re-review and bump "
            "`last_reviewed`, or the lighthouse is showing stale light."
        )
        return 1
    print("staleness: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
