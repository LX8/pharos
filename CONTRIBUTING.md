<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Contributing

This is an open, falsifiable evidence commons. The most valuable contribution is **meeting a
claim's falsification trigger with evidence** — proving an entry wrong, in public, on the record.
The second-most valuable is adding a new, carefully-graded entry, fixing a citation, or
strengthening the tooling that keeps every public number honest.

Two laws govern everything here. They are not slogans; the build gates enforce them.

1. **Cite only what is measured.** A grade rests on the evidence *actually cited in the entry* —
   not plausibility, vibe, or your prior. If it isn't measured and cited, it doesn't raise the
   grade. (This is the rule that most often trips people; see [the entry workflow](#adding-or-re-grading-an-evidence-entry).)
2. **Watch power, not people.** Everything published is country/institution level — never
   sub-national, geolocated, or person-level. See [`THREAT_MODEL.md`](THREAT_MODEL.md); the
   `make threat-model` gate enforces it on the data.

The full standards are in [`docs/GRADING_PROTOCOL.md`](docs/GRADING_PROTOCOL.md) (how grades are
decided) and [`docs/VERIFYING.md`](docs/VERIFYING.md) (how the repo checks itself). This file is
the on-ramp.

---

## Quick start

Stdlib-only Python; **no `pip install`**, no build step.

```bash
git clone https://github.com/LX8/pharos && cd pharos
make hooks        # free local CI: pre-commit -> dashboard, pre-push -> verify-offline
make dashboard    # one GREEN/RED report across the seven audits  (start here)
./pharos stats    # one-glance summary of the project
./pharos verify   # same as make dashboard, from the CLI
```

If `make dashboard` is GREEN, your checkout is sound. Browse with `./pharos ledger`,
`./pharos watch` (the falsification watch), `./pharos coverage` (where the evidence is thin).

---

## What you can contribute

| Contribution | Discipline |
| --- | --- |
| **Meet a falsification trigger** | Bring the evidence the trigger names; open an issue/PR citing it. This is the point of the whole thing. |
| **Re-grade an entry** | Per [`GRADING_PROTOCOL.md` §4](docs/GRADING_PROTOCOL.md); on a genuine tie the **more conservative grade wins**. |
| **Add an evidence entry** | The full workflow below — every citation web-verified first. |
| **Fix a citation** | Correct author/year/venue/DOI to the published record; bump `last_reviewed`. |
| **Tooling / docs / tests** | Fully open. Keep it stdlib-only; add a test; keep `make dashboard` GREEN. |

New visible *scientific claims* are the maintainer's call to grade and frame — propose them in an
issue first. Tooling, tests, citation fixes, and docs don't need that.

**Opening a PR.** Branch (`claude/<topic>` for AI-driven work, `<author>/<topic>` for human),
keep history linear (rebase, not merge commits), and fill the pull-request checklist — it just
restates the gate: `make dashboard` GREEN, counts re-pinned if they changed, SPDX/REUSE on new
files, and the spatial floor held. To challenge an entry, the **falsification-challenge** issue
template walks you through the trigger, the evidence, and the grade it implies.

---

## Adding (or re-grading) an evidence entry

The grade discipline first, then the mechanics — **both matter**.

### The discipline (this is the hard part)

- **Web-verify every citation before you write it.** Confirm each source exists with the exact
  author / year / venue / volume / DOI, that it is **not retracted**, and that it actually supports
  the sentence it backs. (Citation review has repeatedly caught fabricated, retracted, and
  mis-attributed sources here — including in entries that were "verified" once already.)
- **Steelman, then break.** Build the strongest version of the claim, then attack it. A claim that
  survived no attack has been asserted, not graded.
- **Separate the layers.** Grade *effect* vs *interpretation*, *correlation* vs *causation*,
  *mechanism* vs *threshold* — each on its own evidence. Never let a robust core launder an oversold
  headline. The single frontmatter grade tracks what the **title** asserts (rule 4, "compose to the
  headline"); the per-layer split lives in the Claim prose and the `falsification_trigger`.
- **Be conservative.** Default to the lower-confidence grade when genuinely torn.
- **A claim that can't be withdrawn is dogma.** Every entry needs a real, *fireable*
  `falsification_trigger` — the specific observation that would downgrade it.

### The mechanics (and the count cascade)

Adding an entry touches more than one file. Miss a step and the gates fail — here is the whole chain:

1. **Write** `ledger/SAA-NNN-short-slug.md` (next free number) from the template in
   [`GRADING_PROTOCOL.md` §5](docs/GRADING_PROTOCOL.md). `last_reviewed` starts equal to `verified`;
   `review_interval_days` follows the grade default (ROBUST/REFUTED 540, CONTESTED 270, OPEN 180).
2. **Register it** in `ledger/index.json` — add `{id, grade, domain, file, title}` and bump
   `updated`. (`id`/`grade`/`domain` must match the frontmatter; `make validate` checks this. The
   index `title` is a curated short label and is *intentionally* allowed to differ from the
   frontmatter title.)
3. **Regenerate the read surface:** `make index` rewrites `ledger/INDEX.md` (the human index +
   falsification watch + coverage map) from the entries. Commit it.
4. **Update the headline counts** the doc-count gate pins: the entry count in
   [`README.md`](README.md), [`STATUS.md`](STATUS.md), and [`site/index.html`](site/index.html), and
   the per-grade tally in `STATUS.md`. Then **re-pin**: `python3 src/audit_counts.py --update`
   (review the `data/expected_counts.json` diff).
5. **Update any test that asserts the count** — the `pharos` tests assert the live entry count
   (e.g. `tests/test_pharos.py`); bump them to match.
6. **`make dashboard`** must be GREEN (validate · staleness · overstatement · counts · threat-model ·
   ledger-index · all unit tests). The overstatement gate will reject unconditional-certainty
   language (`proven`, `definitively`, bare `impossible`, …) — keep the prose hedged to the evidence.

> Tip: run `./pharos coverage` to see which domains are thin — that's where new entries add the most.

### Re-grading

Edit the grade in **both** the frontmatter and `ledger/index.json`, bump `last_reviewed`, update the
per-grade tally + re-pin (step 4), and run `make dashboard`. A second grader reconciling with the
first: the **more conservative grade wins** a genuine tie (see [`GRADING_PROTOCOL.md` §6](docs/GRADING_PROTOCOL.md)).

---

## Commits & PRs

- **Identity** — commit with a no-reply e-mail address (for example your GitHub
  `users.noreply.github.com` address), never a personal one.
- **Subject** — Conventional Commits: `feat(scope):`, `fix(scope):`, `docs:`, `test:`, `chore:`.
  The body explains *why* and lists what's verified (test counts, gate status).
- **Co-author** — when an AI assistant pair-coded the change, add a
  `Co-Authored-By:` trailer. AI assistants are not authors and hold no copyright; every retained
  claim is checked against cited, measured sources by a human.
- **Before you push** — `make dashboard` GREEN; for anything touching the indicators,
  `make verify-offline` (deterministic, no network, drift-checked). The pre-push hook runs it.
- **Licensing** — every new file carries an SPDX header (or a `REUSE.toml` entry): code
  `GPL-3.0-or-later`, prose `CC-BY-SA-4.0`, derived data `CC0-1.0`.

---

## Publishing and reuse

This repository is public. Its prose is CC BY-SA 4.0, its code GPL-3.0-or-later and its derived
data CC0 1.0, so you may mirror, adapt and republish it under those terms (see `LICENSE` and
`REUSE.toml`, and please respect the ethical-use covenant in `NOTICE` §7). Contributions arrive as
public issues and pull requests and pass the same gates before merge.

---

*Thank you. The antidote to a politics that subordinates truth to power is knowledge anyone can
audit — and that only works if more than one person keeps it honest.*
