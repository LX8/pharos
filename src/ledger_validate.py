# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Ledger structural validator — make the grading protocol *runnable*, not trust-me prose.

The plan-for-peace self-verification graded the project's durability SERIOUS (R5):
the grading method lived only in the author's head and notes, so the ledger had a
bus-factor of one. The fix is to put the method in the repo as open, runnable
artifacts — [`docs/GRADING_PROTOCOL.md`](../docs/GRADING_PROTOCOL.md) for the human
rubric, and this validator so a second grader's entries are checked against that
rubric automatically.

It enforces the protocol's machine-checkable parts: every entry carries the
required fields, a grade drawn from the controlled vocabulary, an id that matches
its filename, sane dates, a sources block, a falsification trigger — and the ledger
and its `index.json` agree. Any violation fails the gate (wired into `make verify`).

Pure stdlib, no pip. Pure core (`validate_entry`, `validate_against_index`); only
`main()` touches the filesystem.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# Reuse the staleness module's frontmatter parser AND date parser — one of each, one behavior.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger_staleness import parse_frontmatter, _parse_date as _date  # noqa: E402

GRADES = ("ROBUST", "CONTESTED", "REFUTED", "OPEN")
REQUIRED_SCALARS = ("id", "title", "grade", "domain", "verified",
                    "last_reviewed", "review_interval_days")


def _frontmatter_block(text):
    """Return the raw text between the first two `---` fences (or '')."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    out = []
    for line in lines[1:]:
        if line.strip() == "---":
            return "\n".join(out)
        out.append(line)
    return ""  # unterminated frontmatter — caught as a structural problem below


def validate_entry(meta, text, filename):
    """Pure. Return a list of human-readable problems for one entry ('' = clean)."""
    problems = []
    block = _frontmatter_block(text)
    if not block:
        return [f"{filename}: missing or unterminated YAML frontmatter"]

    for key in REQUIRED_SCALARS:
        if key not in meta:
            problems.append(f"{filename}: missing required field `{key}`")

    grade = meta.get("grade")
    if grade is not None and grade not in GRADES:
        problems.append(f"{filename}: grade `{grade}` not in {GRADES}")

    ident = meta.get("id", "")
    if ident and not filename.startswith(ident + "-"):
        problems.append(f"{filename}: id `{ident}` does not match filename")

    # dates: parse, and a claim cannot be reviewed before it was first verified.
    try:
        verified = _date(meta["verified"]) if "verified" in meta else None
        reviewed = _date(meta["last_reviewed"]) if "last_reviewed" in meta else None
        if verified and reviewed and reviewed < verified:
            problems.append(f"{filename}: last_reviewed {reviewed} precedes verified {verified}")
    except (ValueError, KeyError):
        problems.append(f"{filename}: verified/last_reviewed not a valid YYYY-MM-DD date")

    raw = meta.get("review_interval_days")
    if raw is not None:
        try:
            if int(raw) <= 0:
                problems.append(f"{filename}: review_interval_days must be positive")
        except ValueError:
            problems.append(f"{filename}: review_interval_days `{raw}` is not an integer")

    # a graded claim that cannot be withdrawn is dogma — require the falsifier + sources.
    if "falsification_trigger:" not in block:
        problems.append(f"{filename}: no falsification_trigger (a claim must say how it could be withdrawn)")
    if "sources:" not in block or not any(
        ln.lstrip().startswith("- ") for ln in block.splitlines()
    ):
        problems.append(f"{filename}: no sources block with at least one source")

    return problems


def validate_against_index(entries, index):
    """Pure. Cross-check that the ledger files and index.json agree.

    ``entries`` is a list of (filename, meta). ``index`` is the parsed index.json.
    A second grader who edits one without the other is caught here.
    """
    problems = []
    idx_by_file = {e.get("file"): e for e in index.get("entries", [])}
    files_on_disk = {fn for fn, _ in entries}

    missing_from_index = files_on_disk - set(idx_by_file)
    for fn in sorted(missing_from_index):
        problems.append(f"index.json: entry file `{fn}` exists on disk but is not listed")
    orphan_in_index = set(idx_by_file) - files_on_disk
    for fn in sorted(orphan_in_index):
        problems.append(f"index.json: lists `{fn}` but no such file on disk")

    for fn, meta in entries:
        e = idx_by_file.get(fn)
        if not e:
            continue
        # `title` is intentionally NOT cross-checked: index.json carries a *curated short
        # label* (e.g. "Prebunking raises manipulation-resistance at scale") that is
        # deliberately not byte-identical to the entry's fuller frontmatter title, so an
        # exact-match check would false-fail. id/grade/domain are the load-bearing keys.
        for field in ("id", "grade", "domain"):
            if str(meta.get(field, "")) != str(e.get(field, "")):
                problems.append(
                    f"{fn}: `{field}` disagrees — frontmatter `{meta.get(field)}` "
                    f"vs index.json `{e.get(field)}`"
                )
    return problems


def _scan(ledger_dir):
    entries = []
    for name in sorted(os.listdir(ledger_dir)):
        if name.startswith("SAA-") and name.endswith(".md"):
            with open(os.path.join(ledger_dir, name), encoding="utf-8") as fh:
                text = fh.read()
            entries.append((name, parse_frontmatter(text), text))
    return entries


def _default_ledger_dir():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "ledger"))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate ledger entries against the grading protocol.")
    ap.add_argument("--ledger", default=_default_ledger_dir())
    args = ap.parse_args(argv)

    scanned = _scan(args.ledger)
    problems = []
    for name, meta, text in scanned:
        problems += validate_entry(meta, text, name)

    index_path = os.path.join(args.ledger, "index.json")
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as fh:
            try:
                index = json.load(fh)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"{index_path}: invalid JSON ({e})") from e
        problems += validate_against_index([(n, m) for n, m, _ in scanned], index)
    else:
        problems.append("index.json: missing")

    print(f"ledger validation — {len(scanned)} entries, {len(problems)} problem(s)")
    for p in problems:
        print(f"  ✗ {p}")
    if problems:
        print("FAIL: ledger does not conform to the grading protocol (docs/GRADING_PROTOCOL.md).")
        return 1
    print("validate: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
