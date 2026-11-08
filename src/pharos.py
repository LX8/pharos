#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""pharos — one command for the whole project.

Browse and search the graded evidence ledger, read its falsification watch (every entry's
pre-registered "what would change our minds" trigger), see coverage by domain, read the open
indicators and the forecast result, and run the verification suite — all from one stdlib-only
command. It wraps the pure cores that already exist (no reimplementation, no dependencies); the
data it reads is the committed source of truth, so every number it prints is the verified one.

    pharos ledger [--grade G] [--domain D] [--search TEXT] [--json]   # browse/search the graded entries
    pharos show SAA-031          # one entry, in full (a bare number works: `pharos show 31`)
    pharos watch                 # the falsification watch
    pharos coverage              # entries by domain
    pharos stale [--within N]    # live review status — what is due for re-review
    pharos stats                 # a one-glance project summary
    pharos indicators            # the WGI governance headline
    pharos divergence            # WGI × V-Dem × Freedom House
    pharos forecast              # the CRPS/Brier backtest result
    pharos verify                # run the offline audit dashboard (all machine-checks)

Run as `python3 src/pharos.py <cmd>`, via the `./pharos` wrapper, or `make pharos ARGS="<cmd>"`.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from ledger_staleness import last_reviewed, read_entries, review_interval, scan  # noqa: E402

LEDGER = os.path.join(ROOT, "ledger")
DERIVED = os.path.join(ROOT, "data", "derived")
GRADE_ORDER = ("ROBUST", "CONTESTED", "REFUTED", "OPEN")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _json(name):
    path = os.path.join(DERIVED, name)
    try:
        return json.loads(_read(path))
    except FileNotFoundError:
        sys.exit(f"pharos: missing derived data {os.path.relpath(path, ROOT)} — "
                 "it is committed; restore it with `git checkout -- data/derived` "
                 "or regenerate with `make snapshot`")
    except json.JSONDecodeError as e:
        sys.exit(f"pharos: unreadable derived data {os.path.relpath(path, ROOT)} ({e}) — "
                 "restore it with `git checkout -- data/derived` or regenerate with `make snapshot`")


def entries():
    """(filename, meta) for every ledger entry — the shared `read_entries` rule, one place."""
    return read_entries(LEDGER)


def _next_review(meta):
    rev = last_reviewed(meta)
    return (rev + timedelta(days=review_interval(meta))).isoformat() if rev else "—"


def _date_arg(s):
    """argparse type for --today: a friendly usage error instead of a strptime traceback."""
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM-DD, got {s!r}")


# ---- commands (each pure-ish: reads committed files, prints, returns an exit code) ----

def cmd_ledger(args):
    rows = all_rows = entries()
    if args.grade:  # argparse has already validated + uppercased the value
        rows = [r for r in rows if r[1].get("grade", "").upper() == args.grade]
    if args.domain:
        rows = [r for r in rows if args.domain.lower() in r[1].get("domain", "").lower()]
    if args.search:
        q = args.search.lower()
        rows = [r for r in rows if q in r[1].get("title", "").lower()]
    if args.json:
        print(json.dumps([m for _f, m in rows], indent=2, ensure_ascii=False))
        return 0
    print(f"{len(rows)} of {len(all_rows)} graded entries"
          + (f"  ·  grade={args.grade}" if args.grade else "")
          + (f"  ·  domain~{args.domain}" if args.domain else "")
          + (f"  ·  \"{args.search}\"" if args.search else ""))
    for _f, m in rows:
        print(f"  {m.get('id', '?'):8} {m.get('grade', '?'):10} "
              f"{(m.get('title', '?')[:62]):62}  review {_next_review(m)}")
    if not rows and (args.domain or args.search):
        print("  (no matches — `pharos coverage` lists the domains; --search matches titles only)")
    return 0


def cmd_show(args):
    want = args.id.strip().upper()
    if want.isdigit():  # `pharos show 31` → SAA-031
        want = f"SAA-{int(want):03d}"
    for f, m in entries():
        if m.get("id", "").upper() == want:
            print(_read(os.path.join(LEDGER, f)).rstrip())
            return 0
    print(f"no ledger entry '{want}' (try `pharos ledger` for the list of ids)")
    return 1


def cmd_watch(_args):
    rows = entries()
    print(f"Falsification watch — the pre-registered trigger for each of {len(rows)} entries.")
    print("Meet one with evidence and the grade moves, in public, on the record.\n")
    for _f, m in rows:
        print(f"  {m.get('id', '?')} · {m.get('grade', '?')} · {m.get('title', '?')}")
        print(f"     ↳ {str(m.get('falsification_trigger', '')).strip() or '(none recorded)'}\n")
    return 0


def cmd_coverage(_args):
    dom = {}
    for _f, m in entries():
        dom.setdefault(m.get("domain", "—"), []).append(m.get("grade", "?"))
    print("Coverage by domain — where the evidence sits, and (by thinness) where it's thin.\n")
    for d in sorted(dom, key=lambda k: (-len(dom[k]), k)):
        gs = dom[d]
        breakdown = ", ".join(f"{gs.count(g)} {g}" for g in GRADE_ORDER if g in gs)
        print(f"  {d:24} {len(gs):>2}   ({breakdown})")
    return 0


def cmd_indicators(_args):
    d = _json("wgi_governance_summary.json")
    o = d["overall"]
    pct = round(o["within_noise"] / o["dimension_country_cells"] * 100)
    print(f"WGI governance {d['baseline_year']}→{d['latest_year']} "
          f"({d.get('mode', '?')}) — {o['dimension_country_cells']} dimension×country cells")
    print(f"  {pct}% within measurement noise · declines {o['meaningful_declines']} "
          f": improvements {o['meaningful_improvements']} ({o['decline_to_improve_ratio']} : 1)")
    va = d.get("va_robustness", {})
    if va:
        p, a = va.get("primary", {}), va.get("alt_window", {})
        print(f"  Voice & Accountability decline:improve — "
              f"{p.get('window')} {p.get('bar_90', {}).get('DECLINE')}:{p.get('bar_90', {}).get('IMPROVE')} (90%), "
              f"{a.get('window')} {a.get('bar_90', {}).get('DECLINE')}:{a.get('bar_90', {}).get('IMPROVE')} (90%)")
    print("  → the measurable erosion is concentrated in democratic voice & accountability.")
    return 0


def cmd_divergence(_args):
    d = _json("voice_divergence.json")
    c = d["counts"]
    print(f"Voice divergence (WGI × V-Dem × Freedom House), {d.get('window')} — publish divergence, not a single score")
    for k in ("CONCUR-DECLINE", "CONCUR-IMPROVE", "CONFLICT", "MIXED-WEAK", "ALL-FLAT", "INSUFFICIENT"):
        if k in c:
            print(f"  {k:16} {c[k]:>3}")
    full = d.get("headline_concur_decline_n_sig_3")
    if isinstance(full, list):
        print(f"  → {c.get('CONCUR-DECLINE', 0)} countries where all three instruments concur on a voice decline "
              f"({len(full)} at full significance); {c.get('CONFLICT', 0)} conflicts surfaced, never blended away.")
    return 0


def cmd_forecast(_args):
    d = _json("forecast_backtest.json")
    r = d["result"]
    print(f"pharos-forecast v0 — {r['n_forecasts']} pre-registered forecasts "
          f"(σ={r['sigma']}, decline base-rate={r['base_rate']}); scored vs a no-change baseline")
    print(f"  {'model':<14}{'CRPS':>9}{'skill':>9}{'Brier':>9}{'skill':>9}")
    for name, m in r["per_model"].items():
        print(f"  {name:<14}{m['crps']:>9}{m['crps_skill']:>+9}{m['brier']:>9}{m['brier_skill']:>+9}")
    print(f"  → {d.get('verdict', '')}")
    return 0


def cmd_stale(args):
    """Live review status (clock-dependent, so it isn't a committed file): what is due for re-review."""
    today = args.today or date.today()
    rows = scan(LEDGER, today)
    shown = rows if args.all else [r for r in rows
                                   if r["stale"] or (r["days_left"] is not None and r["days_left"] <= args.within)]
    shown.sort(key=lambda r: r["days_left"] if r["days_left"] is not None else -10 ** 9)
    n_stale = sum(1 for r in rows if r["stale"])
    suffix = "" if args.all else f" (stale or due ≤ {args.within}d; --all for everything)"
    print(f"Review status @ {today.isoformat()} — {n_stale} stale of {len(rows)}; {len(shown)} shown{suffix}")
    for r in shown:
        flag = "STALE" if r["stale"] else f"{r['days_left']:+d}d"
        print(f"  [{flag:>6}] {r['id']:8} {str(r['grade']):10} reviewed {r['reviewed']}  "
              f"interval {r['interval_days']}d")
    if n_stale and not args.all:
        print("  → re-review and `git`-bump `last_reviewed`, or `make staleness` fails the gate.")
    return 0


def cmd_stats(_args):
    """A one-glance project summary, all derived (no hardcoded numbers to drift)."""
    import audit_dashboard
    es = entries()
    by = {}
    for _f, m in es:
        by[m.get("grade", "?")] = by.get(m.get("grade", "?"), 0) + 1
    sims = [f for f in os.listdir(os.path.join(ROOT, "src", "sims"))
            if f.startswith("sim_") and f.endswith(".py")]
    print("Pharos — an open, falsifiable evidence commons. Watch power, not people.")
    print(f"  ledger     {len(es)} graded entries — "
          + " · ".join(f"{by[g]} {g}" for g in GRADE_ORDER if by.get(g)))
    print(f"  simulators {len(sims)} validated mechanisms (each reproduces a published result)")
    print(f"  audits     {len(audit_dashboard.AUDITS)} machine-checks — `pharos verify` (or `make dashboard`)")
    print("  forecast   a calibration layer, CRPS/Brier-scored vs a no-change baseline — `pharos forecast`")
    return 0


def _strip_html_comments(text):
    """Drop leading HTML comment blocks (the SPDX header + generated-by note) for terminal display."""
    text = text.lstrip()
    while text.startswith("<!--"):
        end = text.find("-->")
        if end == -1:
            break
        text = text[end + 3:].lstrip()
    return text


def _print_doc(rel, make_target):
    path = os.path.join(ROOT, rel)
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"pharos: {rel} not found — run `make {make_target}` to generate it")
        return 1
    print(_strip_html_comments(text).rstrip())
    return 0


def cmd_brief(_args):
    # the plain-language read (docs/IMPACT.md lever L4), generated from the committed data
    return _print_doc(os.path.join("docs", "BRIEF.md"), "brief")


def cmd_report(_args):
    # the flagship watch-report prototype (lever L2)
    return _print_doc(os.path.join("docs", "WATCH_REPORT.md"), "watch-report")


def cmd_verify(_args):
    import audit_dashboard
    return audit_dashboard.main([])


def _port_arg(value):
    port = int(value)
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def cmd_serve(args):
    from pharos_server import serve
    return serve(args.port)


def build_parser():
    ap = argparse.ArgumentParser(prog="pharos", description="One command for the Pharos project.")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("serve", help="open the local research observatory")
    p.add_argument("--port", type=_port_arg, default=8796, help="loopback port (default: 8796)")
    p.set_defaults(fn=cmd_serve)

    p = sub.add_parser("ledger", help="browse / search the graded evidence entries")
    p.add_argument("--grade", type=str.upper, choices=list(GRADE_ORDER), metavar="GRADE",
                   help="filter by grade: ROBUST, CONTESTED, REFUTED or OPEN (case-insensitive)")
    p.add_argument("--domain", help="filter by domain substring (e.g. political-economy)")
    p.add_argument("--search", help="filter by title substring")
    p.add_argument("--json", action="store_true", help="emit the filtered entries as JSON (for scripting)")
    p.set_defaults(fn=cmd_ledger)

    p = sub.add_parser("show", help="print one entry in full")
    p.add_argument("id", help="entry id, e.g. SAA-031")
    p.set_defaults(fn=cmd_show)

    p = sub.add_parser("stale", help="live review status — what is due for re-review")
    p.add_argument("--today", type=_date_arg, metavar="YYYY-MM-DD",
                   help="evaluate as of this date; defaults to the system date")
    p.add_argument("--within", type=int, default=90, help="show entries due within N days (default 90)")
    p.add_argument("--all", action="store_true", help="show every entry, not just due/stale ones")
    p.set_defaults(fn=cmd_stale)

    for name, fn, helptext in (
        ("watch", cmd_watch, "the falsification watch — every entry's trigger"),
        ("coverage", cmd_coverage, "entries by domain"),
        ("stats", cmd_stats, "a one-glance project summary"),
        ("brief", cmd_brief, "the plain-language read of what the data says"),
        ("report", cmd_report, "the flagship watch-report prototype"),
        ("indicators", cmd_indicators, "the WGI governance headline"),
        ("divergence", cmd_divergence, "WGI × V-Dem × Freedom House triangulation"),
        ("forecast", cmd_forecast, "the CRPS/Brier backtest result"),
        ("verify", cmd_verify, "run the offline audit dashboard (all machine-checks)"),
    ):
        sp = sub.add_parser(name, help=helptext)
        sp.set_defaults(fn=fn)
    return ap


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    if not getattr(args, "fn", None):
        ap.print_help()
        return 0
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
