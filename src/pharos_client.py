# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""pharos_client — the one-file, stdlib-only reader for the Pharos data (vendor me).

This module is the reuser's on-ramp promised by docs/DATA_CONTRACT.md: copy this single file
into your project (or import it from a checkout) and every published Pharos table loads as
plain Python dicts and lists in one line. No dependencies, no install, read-only — it never
writes, fetches, or mutates anything.

    import pharos_client as px
    rows = px.governance_table()          # 1,222 country x dimension changes, typed
    concur = [r for r in px.divergence_table() if r["label"] == "CONCUR-DECLINE"]
    print(px.forecast()["verdict"])       # the honest one

Column meanings, categorical vocabularies, and the stability guarantees are in
docs/DATA_CONTRACT.md — this file intentionally contains no interpretation, only access.
The data license is CC0-1.0; cite the project via CITATION.cff.
"""
import csv
import json
import math
import os

# Contract version — bumped only with docs/DATA_CONTRACT.md when a breaking change ships.
CONTRACT_VERSION = 1


def find_root(root=None):
    """Locate a Pharos checkout: the given path, or walk upward from cwd until one is found."""
    if root is not None:
        if not os.path.isdir(os.path.join(root, "data", "derived")):
            raise FileNotFoundError(f"{root!r} is not a Pharos checkout (no data/derived)")
        return root
    d = os.getcwd()
    while True:
        if os.path.isdir(os.path.join(d, "data", "derived")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise FileNotFoundError("no Pharos checkout found upward from cwd — pass root=<path>")
        d = parent


def _coerce(value):
    """CSV cells -> useful Python: '' -> None, ints, floats, True/False; anything else stays str."""
    if value == "":
        return None
    if value in ("True", "False"):
        return value == "True"
    try:
        return int(value)
    except ValueError:
        pass
    try:
        f = float(value)
        # 'nan'/'inf' parse as non-finite floats that silently poison comparisons and sums;
        # for a data-reading client the honest behavior is to leave such cells as text
        return f if math.isfinite(f) else value
    except ValueError:
        return value


def _table(root, name):
    path = os.path.join(find_root(root), "data", "derived", name)
    with open(path, newline="", encoding="utf-8") as f:
        return [{k: _coerce(v) for k, v in row.items()} for row in csv.DictReader(f)]


def _doc(root, *parts):
    with open(os.path.join(find_root(root), *parts), encoding="utf-8") as f:
        return json.load(f)


def governance(root=None):
    """The WGI governance summary (method, per-dimension counts, overall tallies, robustness)."""
    return _doc(root, "data", "derived", "wgi_governance_summary.json")


def governance_table(root=None):
    """Per country x dimension decade changes with 90% CI z-tests (verdict: DECLINE/IMPROVE/NO_SIG_CHANGE)."""
    return _table(root, "wgi_governance.csv")


def divergence(root=None):
    """The full voice-divergence document (three instruments, per-country agreement labels)."""
    return _doc(root, "data", "derived", "voice_divergence.json")


def divergence_table(root=None):
    """Per-country instrument comparison; label is the six-value agreement vocabulary, never a blend."""
    return _table(root, "voice_divergence.csv")


def forecast(root=None):
    """The pre-registered forecast backtest (scoring, per-model skill, the honest verdict)."""
    return _doc(root, "data", "derived", "forecast_backtest.json")


def forecast_table(root=None):
    """Per-model CRPS/Brier scores and skill vs the no-change baseline."""
    return _table(root, "forecast_backtest.csv")


def ledger(root=None):
    """The graded evidence entries: [{id, grade, domain, file, title}, ...]."""
    return _doc(root, "ledger", "index.json")["entries"]


def entry_text(entry_id, root=None):
    """The full markdown of one ledger entry (frontmatter included), by id like 'SAA-007'."""
    for e in ledger(root):
        if e["id"] == entry_id:
            path = os.path.join(find_root(root), "ledger", e["file"])
            with open(path, encoding="utf-8") as f:
                return f.read()
    raise KeyError(f"no ledger entry {entry_id!r}")


if __name__ == "__main__":
    # Smoke demo: one line per surface, so `python3 pharos_client.py` proves the contract loads.
    print(f"pharos_client contract v{CONTRACT_VERSION} @ {find_root()}")
    print(f"  governance : {len(governance_table())} rows; "
          f"{governance()['overall']['within_noise']} within noise")
    labels = {}
    for r in divergence_table():
        labels[r["label"]] = labels.get(r["label"], 0) + 1
    print(f"  divergence : {len(divergence_table())} countries; {labels}")
    print(f"  forecast   : {forecast()['verdict']}")
    print(f"  ledger     : {len(ledger())} entries")
