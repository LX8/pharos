#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Master audit dashboard — one command, one GREEN/RED verdict.

Runs every offline gate in sequence (fastest first) and prints a single status a
human reads in seconds — and a `--json` mode for CI. The credibility claim it backs:
*every load-bearing property of this repo is machine-checked, and you can run the
check yourself.*

Exit 0 only if all audits pass.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass

PY = sys.executable


@dataclass
class AuditSpec:
    name: str
    argv: list
    timeout: int = 180


AUDITS = (
    AuditSpec("unit tests", [PY, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]),
    AuditSpec("ledger structure", [PY, "src/ledger_validate.py"]),
    AuditSpec("ledger freshness", [PY, "src/ledger_staleness.py"]),
    AuditSpec("overstatement", [PY, "src/audit_overstatement.py"]),
    AuditSpec("doc counts", [PY, "src/audit_counts.py"]),
    AuditSpec("threat model", [PY, "src/audit_threat_model.py"]),
    AuditSpec("ledger index", [PY, "src/ledger_digest.py"]),
)


def run_audit(spec, repo):
    """Run one audit as a subprocess. Returns (ok, seconds, tail-of-output)."""
    t0 = time.monotonic()
    try:
        p = subprocess.run(spec.argv, cwd=repo, capture_output=True, text=True, timeout=spec.timeout)
        ok = p.returncode == 0
        tail = (p.stdout + p.stderr).strip().splitlines()[-1:] if not ok else []
    except subprocess.TimeoutExpired:
        ok, tail = False, [f"timeout after {spec.timeout}s"]
    return ok, time.monotonic() - t0, (tail[0] if tail else "")


def _default_repo():
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Run all offline audits; one GREEN/RED report.")
    ap.add_argument("--repo", default=_default_repo())
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    results = []
    for spec in AUDITS:
        ok, secs, tail = run_audit(spec, args.repo)
        results.append({"name": spec.name, "ok": ok, "seconds": round(secs, 2), "detail": tail})

    npass = sum(r["ok"] for r in results)
    overall = npass == len(results)

    if args.json:
        print(json.dumps({"overall": "GREEN" if overall else "RED",
                          "passed": npass, "total": len(results), "audits": results}, indent=2))
    else:
        print(f"\n  PHAROS LEDGER — audit dashboard ({npass}/{len(results)})\n")
        for r in results:
            mark = "✓" if r["ok"] else "✗"
            line = f"   {mark}  {r['name']:<20} {r['seconds']:>6.2f}s"
            if not r["ok"]:
                line += f"   ← {r['detail']}"
            print(line)
        print(f"\n  OVERALL: {'GREEN — all audits pass' if overall else 'RED — see ✗ above'}\n")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
