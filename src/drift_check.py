#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Input-drift reconnaissance — has the upstream data moved since we pinned it?

The ledger has a staleness gate; the *input data* did not. The published indicators and the
forecast are computed from snapshots pinned on a fixed date, but upstream (World Bank WGI, and
V-Dem / Freedom House via Our World in Data) can publish new data at any time. This answers one
question without changing anything: **is the pin still current?**

It reads the committed derived outputs into memory, recomputes them from the **LIVE** sources,
compares the *substantive* content (ignoring the `mode` / `fetched_utc` provenance stamps that
always differ between an offline and a live run), reports what — if anything — moved, and then
**restores the committed pin byte-for-byte** in a `finally`, so a clean checkout is left exactly
as it was found even if the fetch fails midway.

It never adopts new data. Adopting upstream changes shifts the project's published numbers — a
deliberate re-pin decision (`make snapshot`), reviewed by a human — not something a drift check
should do silently. So this is *reconnaissance*: run it periodically, and it tells you whether a
re-pin conversation is due.

Exit 0 = pin current (or upstream unreachable — reported, not asserted); exit 1 = real drift.
Pure core (`substantive`, `diff_derived`) is offline-testable; only `main()` touches the network.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DERIVED = os.path.join(REPO, "data", "derived")

# The committed derived outputs, and the LIVE modules that (re)compute them (in dependency order —
# voice reads WGI's output, so WGI must recompute first).
DERIVED_FILES = (
    "wgi_governance.csv", "wgi_governance_summary.json",
    "voice_divergence.csv", "voice_divergence.json",
    "forecast_backtest.json", "forecast_backtest.csv",
)
LIVE_MODULES = (
    "src/indicators/wgi_governance.py",
    "src/indicators/voice_divergence.py",
    "src/forecast/pharos_forecast.py",
)

# Provenance keys that differ between an offline and a live run and carry no computed meaning.
VOLATILE_KEYS = {"mode", "fetched_utc"}


def substantive(text, filename):
    """Pure. The comparable content of one derived file: JSON with volatile provenance keys
    stripped (recursively), or CSV text verbatim (CSVs carry only data rows, no stamps)."""
    if filename.endswith(".json"):
        return _strip(json.loads(text))
    return text


def _strip(obj):
    if isinstance(obj, dict):
        return {k: _strip(v) for k, v in obj.items() if k not in VOLATILE_KEYS}
    if isinstance(obj, list):
        return [_strip(x) for x in obj]
    return obj


def diff_derived(committed, fresh):
    """Pure. ``committed`` / ``fresh`` are {filename: text}. Return the sorted list of filenames
    whose *substantive* content differs (a real upstream-data change). O(files)."""
    changed = []
    for name in committed:
        if name in fresh and substantive(committed[name], name) != substantive(fresh[name], name):
            changed.append(name)
    return sorted(changed)


def _read_bytes(name):
    with open(os.path.join(DERIVED, name), "rb") as f:
        return f.read()


def _write_bytes(name, data):
    with open(os.path.join(DERIVED, name), "wb") as f:
        f.write(data)


def _new_year_note():
    """The derived comparison cannot see a year published after the pin (the backtest and the pin
    are capped at 2024), so report the newest year of the live forecast series. Added 2026-10-31,
    after the July check called the forecast input "current" while 2025 was already published."""
    try:
        sys.path.insert(0, os.path.join(REPO, "src", "forecast"))
        import pharos_forecast as pf
        pf._OFFLINE = False
        newest = max(y for s in pf._load_panel(max_year=None).values() for y in s)
    except Exception as e:  # noqa: BLE001 - reconnaissance only
        print(f"drift-check: newest upstream V-Dem year UNVERIFIED ({type(e).__name__})")
        return
    if newest > pf.SNAP_MAX:
        print(f"drift-check: V-Dem now publishes {newest} (the pin stops at {pf.SNAP_MAX}); "
              "the forward registry can be scored: `make score`.")
    else:
        print(f"drift-check: newest upstream V-Dem year is {newest}; nothing new to score.")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Reconnaissance: has upstream data changed since the pin? Never adopts, always restores.")
    ap.add_argument("--warn", action="store_true", help="report drift but exit 0 (never fail)")
    ap.add_argument("--timeout", type=int, default=300, help="per-source live-fetch timeout, seconds")
    args = ap.parse_args(argv)

    # Hold the pin as raw BYTES so the restore is exact — the derived CSVs use CRLF, which a
    # text-mode round-trip would silently rewrite.
    try:
        committed = {name: _read_bytes(name) for name in DERIVED_FILES}
    except FileNotFoundError as e:
        print(f"drift-check: derived output {os.path.basename(e.filename or '?')} is missing — "
              "run `make snapshot` (or restore data/derived) to build the pin first")
        return 2

    # Force the children LIVE: never inherit an ambient SAA_OFFLINE=1 (the Makefile sets it), which
    # would make them recompute from the snapshot — fresh==committed by construction — and report a
    # confident, false "current" without ever touching the network.
    live_env = {**os.environ, "SAA_OFFLINE": "0"}
    unreachable = None
    try:
        for mod in LIVE_MODULES:
            try:
                r = subprocess.run([sys.executable, mod], cwd=REPO, env=live_env,
                                   capture_output=True, text=True, timeout=args.timeout)
            except (subprocess.TimeoutExpired, OSError) as e:
                unreachable = (mod, [type(e).__name__])
                break
            if r.returncode != 0:
                unreachable = (mod, (r.stderr or r.stdout).strip().splitlines()[-1:] or [""])
                break
        fresh = {name: _read_bytes(name) for name in DERIVED_FILES}
    finally:
        for name, data in committed.items():   # restore the pin byte-for-byte, come what may
            _write_bytes(name, data)

    if unreachable:
        mod, tail = unreachable
        print(f"drift-check: could not complete a live fetch ({mod}: {tail[0] if tail else '—'})")
        print("             upstream freshness UNVERIFIED (offline / slow / rate-limited?) — the pin is unchanged.")
        return 0

    _new_year_note()
    drifted = diff_derived({n: b.decode("utf-8") for n, b in committed.items()},
                           {n: b.decode("utf-8") for n, b in fresh.items()})
    if not drifted:
        print("drift-check: ok — live upstream matches the committed pin; every published number is current.")
        return 0

    print(f"drift-check: DRIFT — upstream data changed in {len(drifted)} file(s):")
    for name in drifted:
        print(f"  ↳ {name}")
    print("This is NOT an error — it means a re-pin is due. Review with `make snapshot`, inspect the "
          "`git diff` of data/derived, and (if the new numbers are correct) commit the re-pin.")
    return 0 if args.warn else 1


if __name__ == "__main__":
    sys.exit(main())
