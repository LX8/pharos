<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# TRUST_SIGNALS.md — how to check us

Trust in scientific work rises when adherence to its norms is **visible and checkable**, not
merely practiced (Jamieson, McNutt, Kiermer & Sever, *PNAS* 2019 — "Signaling the
trustworthiness of science"). This project practices the norms below throughout the repo;
this page makes each one **legible**: the norm, the mechanism that enforces it, and the
command that lets a stranger verify it *without trusting us*.

One honest framing note before the list: the evidence says pre-registration **alone** does
not move a reader's trust — what differentiates is a visible **self-correction record**
combined with independence signals. So that record comes first.

---

## 1. Self-correction — the record, not the promise

A project that has never withdrawn anything is not rigorous; it is untested.

- The ledger keeps a **REFUTED** grade in public view
  ([`ledger/SAA-011`](../ledger/SAA-011-refuted-pseudoscience.md)) — claims graded down are
  *kept*, not deleted.
- The forecast's headline result is **negative**: pharos-forecast v0 does **not** beat the
  no-change baseline, and that is published as the finding
  ([`docs/forecast/pharos-forecast-v0.md`](forecast/pharos-forecast-v0.md)), with a
  plain-language explainer of why a calibrated miss is the system working
  ([`CALIBRATED_MISS_EXPLAINER.md`](forecast/CALIBRATED_MISS_EXPLAINER.md)).
- The adversarial review rounds are on the record — including the defects they found in
  **our own** work and the fixes ([`docs/VERIFYING.md`](VERIFYING.md) §4,
  [`docs/CHRONICLE.md`](CHRONICLE.md)): a mislabeled simulator claim, citation attribution
  errors, a skill-computation bug, an overclaim in a fresh entry — and, most recently, two
  overstated significance claims in **our own summary prose and on the site** (the canonical
  indicator doc was right; the summaries drifted). Found, fixed, documented, then pinned so
  they cannot recur.
- A **pre-registered self-audit of our own instrument for directional bias** is committed
  *before* being run ([`BIAS_AUDIT_PREREGISTRATION.md`](BIAS_AUDIT_PREREGISTRATION.md)):
  blind valence coding, fixed skew criteria, a partisan-object count — the methodology is
  frozen before anyone sees the answer, and the result publishes here **including a null**.

**Check it:** `./pharos show SAA-011` · `./pharos forecast` · the dated corrections in
[`CHANGELOG.md`](../CHANGELOG.md) and [`CHRONICLE.md`](CHRONICLE.md) (the public repository starts from a
single 2026-11-08 commit; earlier history is not public)

## 2. Reproducibility — bytes, not vibes

- Everything recomputes **offline, deterministically, with no network and no install**
  (stdlib-only Python) from pinned input snapshots (source URL + sha256 + fetch time
  stamped in [`data/snapshots/`](../data/snapshots/)).
- The recompute must match the committed outputs **byte-for-byte** or the gate fails —
  including line endings, pinned cross-platform via `.gitattributes`.

**Check it:** `make verify-offline` — **306 offline tests** plus the full recompute; any
drift between what the code produces and what the docs claim is a build failure.

## 3. Falsifiability — pre-registered, in one place

- Every one of the **41 graded, falsifiable evidence entries** carries a
  `falsification_trigger`: the pre-registered observation that would force a downgrade.
  They are collected in one auditable place — the falsification watch in
  [`ledger/INDEX.md`](../ledger/INDEX.md).
- The forecast's success bar (beat the no-change baseline by CRPS) was pre-registered
  before scoring. The threat model carries a falsification trigger for the safety claim
  itself. Even the impact strategy ([`IMPACT.md`](IMPACT.md)) carries one.

**Check it:** `./pharos watch` · `make validate`

## 4. Uncertainty first — the headline, not the footnote

- The governance indicator's most prominent number is its own noise floor: **88%** of
  measured changes are within measurement noise (90% CI). What survives that filter is
  reported with the interval, never as a point score.
- Where instruments disagree, we publish the **divergence** (WGI × V-Dem × Freedom House,
  conflicts surfaced by name) — never a blended single score.

**Check it:** `./pharos indicators` · `./pharos divergence`

## 5. Citation integrity — cite only what is measured

- Every citation is web-verified before it enters an entry: the source exists, the
  author/year/venue/DOI are exact, it is not retracted, and it supports the *specific
  sentence* it is attached to ([`docs/GRADING_PROTOCOL.md`](GRADING_PROTOCOL.md)).
- The whole ledger passed an independent full-corpus citation sweep (every source
  re-verified; result: zero fabricated, zero retracted; the attribution errors it *did*
  find are fixed and on the record — see §1).

**Check it:** any entry's sources are plain URLs/DOIs — follow them.

## 6. Machine-enforced honesty — gates, not intentions

The audit suite runs as one command and fails the build on violation: unit tests, ledger
structure, entry staleness, an **overstatement guard** (unqualified "proven/only/unique"
language fails), count/figure consistency (every public number in the README, site, and
docs is pinned to the computed data), the **spatial-floor gate** (any data below
country/institution level fails — "watch power, not people" is code, not a slogan), and
index freshness.

**Check it:** `make dashboard` (or `./pharos verify`)

## 7. Do-no-harm by design

- Published layers are country/institution-level **only** — no sub-national, geolocated,
  group-attributed, or person-level data, enforced by the gate above and governed by an
  explicit, falsifiable [`THREAT_MODEL.md`](../THREAT_MODEL.md) with a publish/withhold
  decision procedure.
- An ethical-use covenant (NOTICE §7) asks that the work never be used for surveillance,
  scoring, or targeting — a good-faith request; the threat-model gate is the enforced part.
- The same law binds our own telemetry: no tracking, no visitor analytics beyond host
  aggregates ([`IMPACT.md`](IMPACT.md) §4).

**Check it:** `make threat-model` — then try adding a `latitude` column to a derived file
and watch the build fail.

## 8. Independence and funding

- **Current funding: none.** The project is unfunded, independent work by its contributors. If
  that ever changes, every funder will be disclosed here, and the funding-independence
  policy (which sources are refused, single-source caps) is committed to *before* any
  money is accepted ([`IMPACT.md`](IMPACT.md) §5–6).
- Non-partisan by construction: the unit of analysis is mechanisms (how backsliding
  propagates and de-escalates), never a party or leader; scope is global.

**Check it:** `grep -ri` the ledger for any party or politician endorsement — the
overstatement and grading gates are designed so you won't find one.

---

*If any signal above stops being checkable by the stated command, that is a bug — file it
against this page. A trust page that can drift from reality is worse than none; the count
and figure claims on this page are themselves pinned by the doc-consistency gate (§6).*
