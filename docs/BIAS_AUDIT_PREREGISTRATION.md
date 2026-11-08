<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# BIAS_AUDIT_PREREGISTRATION.md — testing our own instrument for directional skew (v1)

> **Status: DESIGNED, NOT RUN.** This is a pre-registration (IMPACT.md lever L6). The
> methodology below is fixed *before* anyone looks at the answer. The run itself is
> founder-gated: the grades are the maintainer's intellectual product, so the audit of
> their bias must be signed off and executed by the founder — with the human second grader
> as the blind coder, which makes this the natural second-grader onboarding task. Once the
> run begins, this document is immutable; any deviation is documented as a deviation.

## Why pre-register a test of ourselves

The standing dismissal of any democracy-monitoring instrument is *"your index is just
biased pessimists."* The verified evidence (docs/IMPACT.md, claim 10 — SUPPORTED) says the
winning defense is not rebuttal but **testing for the bias directly and publishing the
result, including nulls**: Bright Line Watch tested its own expert panel for systematic
pessimism across 19 waves and published the null (Bergeron-Boutin, Carey, Helmke & Rau);
V-Dem's affiliated researchers ran direct tests of the "coder bad-vibes" hypothesis
(Knutsen et al. 2024, *PS: Political Science & Politics*) rather than dismissing it. Our own
ledger grades that debate in [SAA-028](../ledger/SAA-028-democratic-recession-2024.md) —
so the project is already on record that the coder-bias question is legitimate. This
pre-registration turns it on ourselves.

**Pre-registered prediction:** the ledger and indicator framing show **no directional skew**
under the criteria below. If that prediction fails, §6 says exactly what we do.

## 1. H1 — Valence–grade independence (the core test)

*The charge:* claims that say "things are bad" get graded ROBUST more easily than claims
that are reassuring.

- **Blind coding.** `python3 src/bias_audit.py --pack <dir>` generates a deterministic
  blind pack: every ledger entry's title + Claim section, grade tokens
  (ROBUST/CONTESTED/REFUTED/OPEN) masked, entries pseudo-shuffled (ordered by SHA-256 of
  id) under opaque codes, with the code→id key in a separate file the coder never opens.
- **Coders.** Two humans, neither the founder; the second grader is coder A. No LLM
  coding — the test is of human-legible valence.
- **The variable.** Each blinded entry gets one VALENCE code:
  - **D** — the claim, if true, supports "decline/authoritarian dynamics are real,
    serious, or worsening";
  - **R** — the claim, if true, is reassuring, cuts against an alarm, or debunks a
    decline-side belief (e.g. the overestimation of support for political violence);
  - **N** — mechanism, definition, or method claim with no directional implication.
  Coders also mark confidence (high/low). Disagreements are discussed once; unresolved
  → N (conservative, matching the grading protocol's tie rule).
- **Analysis.** The 2×2 table valence (D vs R) × grade (ROBUST vs not). Statistic:
  ΔP = P(ROBUST | D) − P(ROBUST | R), Fisher exact test (two-sided), and an exact
  (Clopper–Pearson) 95% CI on each proportion — all computed by the shipped scorer.
- **Pre-registered skew criterion:** ΔP > 0.25 **and** Fisher p < 0.10. N is small
  (a few dozen entries, few R by construction of the field) — so **the full contingency
  table, ΔP, CI, and p are published regardless of outcome**, and a result below the
  criterion is reported as a null *with* its power limitation, never as "proof of no bias."

## 2. H2 — Partisan-object asymmetry

*The charge:* the ledger is a partisan instrument aimed at one side.

- **Test:** count entries whose Claim names a living politician or a specific party as the
  *object of blame* (not as a dataset label or historical example). Both coders count
  independently on the unblinded ledger (this test needs the full text).
- **Pre-registered expectation: 0.** Any instance is a flag → the entry is re-framed to the
  mechanism level or its exception is justified in writing.

## 3. H3 — Symmetric reporting (mechanical; standing rule)

*The charge:* the framing amplifies decline beyond what the data shows.

- **Rule:** any project surface that reports the count of meaningful declines must report
  the count of meaningful improvements with equal prominence (same sentence or same visual
  element), and any decline headline must carry its noise denominator. The site
  ("declines to improvements 88:54"), the brief, and the indicator docs already follow it.
- **Check:** part of the audit run is a documented walk of every surface (site, README,
  BRIEF, indicator docs) against this rule; violations are fixed, and the rule is a
  candidate for a future machine gate.

## 4. H4 — Trigger-firability symmetry

*The charge:* falsification triggers on decline-affirming claims are written to be
unfireable (dogma with paperwork).

- **Test:** for every entry, coders mark the `falsification_trigger` as **SPECIFIC** (names
  a dataset, measure, threshold, or timeframe that could actually fire) or **VAGUE**.
- **Pre-registered skew criterion:** specificity rate for D-valence ROBUST entries lower
  than for R-valence entries by more than 0.30. Publish the rates regardless.

## 5. What this audit does NOT test (honest scope)

- **Selection bias in what gets graded** — H1 conditions on the entries that exist; it
  cannot see the claims never written. Mitigation lives elsewhere: the coverage-by-domain
  table in [`ledger/INDEX.md`](../ledger/INDEX.md) and the OPEN-backlog note in the README.
- **Partial blindness** — masking grade tokens does not erase every cue (titles can be
  suggestive; layered-claim prose has a recognizable shape; and the word "open" is masked
  only in its uppercase grade form, since masking ordinary "open" would shred the text —
  a residual that affects at most the one OPEN-graded entry). Reported as a design limit.
- **Small-N power** — with ~38 entries this is a descriptive audit with pre-registered
  criteria, not a hypothesis test with comfortable power. We say so wherever results appear.

## 6. Commitments (what happens with the result)

1. The result — **including a null** — is published in
   [`docs/TRUST_SIGNALS.md`](TRUST_SIGNALS.md) §1 and as a dated report under
   `docs/verifications/bias-audit-<date>.md`, with the raw coding tables.
2. If any criterion fires: a founder re-grade pass over the flagged axis, each outcome
   documented in the entries' `last_reviewed` history and the CHANGELOG; the audit is
   re-run after the pass.
3. The blind pack generator, this protocol, and the published result together become the
   citable answer to the partisanship charge — modeled on the Bright Line Watch playbook.
4. Timing: the audit runs **before the publication gate opens**, so the first public
   impression includes it.

## 7. How to run this (the operator steps)

The whole run is an afternoon. Nothing here is automatable away — that is the point; the two
human coders *are* the instrument. The tooling only removes the friction around them.

1. **Founder signs off** the methodology in §8 (freezes this document; from here it is
   immutable — any deviation is logged as a deviation, not edited in).
2. **Generate the blind pack** from the current ledger:
   ```
   make bias-pack                      # writes build/bias-audit/blind_pack.md + blind_key.json
   ```
   `blind_pack.md` has grade words masked and entries shuffled; `blind_key.json` is the
   sealed code→id map. **Give each coder only `blind_pack.md`.** (`build/` is gitignored —
   the pack and coded results are working files, not committed until the dated report.)
3. **Two coders code independently** — the second grader is coder A. Recruiting and briefing
   them is one send: [`SECOND_GRADER_PACKET.md`](SECOND_GRADER_PACKET.md) contains the
   invitation, the self-contained coding brief (with synthetic worked examples, so reading it
   cannot pre-expose a coder), and the deliverable format. Each coder reads every item's
   text and records H1 valence (**D**/**R**/**N**), and while unblinded also does the H2
   partisan-object count and H4 trigger-specificity marks (§2, §4). Save each coder's H1
   valences as a small JSON, `{ "E01": "D", "E02": "N", … }`.
4. **Reconcile** the two H1 codings once (§1 rule: discuss; unresolved → N).
5. **Score H1** — the pre-registered statistics, computed for you:
   ```
   python3 src/bias_audit.py --score reconciled.json --key build/bias-audit/blind_key.json
   ```
   prints the 2×2 table, P(ROBUST|D), P(ROBUST|R), their exact 95% CIs, ΔP, the exact
   two-sided Fisher *p*, and
   the frozen verdict (skew fires only if ΔP > 0.25 **and** *p* < 0.10).
6. **Write the dated report** at `docs/verifications/bias-audit-<date>.md` with the raw
   coding tables and the H1/H2/H4 results — **including a null** — and add the headline to
   [`TRUST_SIGNALS.md`](TRUST_SIGNALS.md) §1 (§6 commitments). If skew fired, run the
   founder re-grade pass and re-audit.

## 8. Sign-off

| Role | Name | Date |
|---|---|---|
| Methodology sign-off (founder) | *pending* | |
| Coder A (second grader) | *pending* | |
| Coder B | *pending* | |

*Designed 2026-07-10 from the verified impact research (IMPACT.md, claim 10 SUPPORTED —
Bright Line Watch/V-Dem precedent). The protocol is fully executable, not aspirational: the
generator (`make bias-pack`) and the pre-registered H1 scorer (`--score`, exact Fisher test,
pure stdlib) both ship and are tested. All that is missing is the two human coders — which is
exactly the founder-gated, second-grader-onboarding step this audit is designed to require.*
