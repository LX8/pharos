# Grading protocol — how a claim earns (and loses) its grade

*Why this file exists.* The plan-for-peace self-verification graded the project's
durability **SERIOUS** (angle R5): the grading method lived in the author's head and
working memory, so the ledger had a **bus-factor of one** — if the maintainer stopped,
nobody else could grade, re-grade, or even check an entry, and the "self-falsifying" ledger
would quietly stop falsifying itself. This document is **Tier-0 ②** of the launch
preconditions: it moves the method out of one head and into the repo as an **open, runnable
artifact**, so a second grader can be onboarded and so the machine can enforce the parts that
are mechanical.

This protocol is enforced, not just described:

- **`make validate`** ([`../src/ledger_validate.py`](../src/ledger_validate.py)) checks every
  entry against the structural rules below and fails the build on any violation.
- **`make staleness`** ([`../src/ledger_staleness.py`](../src/ledger_staleness.py)) fails the
  build when an entry is past its review interval.
- Both run inside **`make verify`**. A grade that doesn't follow the protocol cannot ship.

---

## 1. The grade vocabularies

### Ledger entries (evidence)

| Grade | Means | Bar |
|---|---|---|
| **ROBUST** | Replicated, broadly accepted, survives adversarial reading | Multiple independent lines of evidence; no live, credible refutation of the *core* claim |
| **CONTESTED** | Real but genuinely disputed; live debate in the literature | At least one strong supporting *and* one strong opposing body of evidence; the question is open |
| **REFUTED** | The claim is false or the construct does not hold | The weight of evidence cuts against it; held in the ledger so the refutation is *recorded*, not hidden |
| **OPEN** | Important but unresolved; not enough to grade either way | The evidence is thin, absent, or methodologically blocked from settling the question |

### Verification claims (a plan or a source held to the bar)

| Grade | Means |
|---|---|
| **HOLDS** | Well-supported as stated |
| **QUALIFIED** | True only under stated conditions / the headline overstates the body |
| **WEAK** | Thin or contested support |
| **BREAKS** | The evidence cuts against it |

### Red-team severities (an attack on a whole plan)

| Severity | Means |
|---|---|
| **FATAL** | Sinks the plan as conceived |
| **SERIOUS** | Survivable only with a real redesign |
| **MANAGEABLE** | Survivable with a stated mitigation |

---

## 2. The rubric — how grades are decided

Four rules govern every grade. They are the project's discipline, made explicit:

1. **Cite only what is measured.** A grade rests on the *evidence actually cited in the
   entry*, not on plausibility, consensus-by-vibe, or the grader's prior. If it isn't
   measured and cited, it doesn't raise the grade.
2. **Steelman first, then try hardest to break it.** Build the strongest version of the claim
   before attacking it. A claim that survives a genuine refutation attempt earns its grade; one
   that was never attacked has not been graded, only asserted.
3. **Separate the layers.** Distinguish *effect* from *interpretation* (Milgram), *instrument*
   from *construct* (the F-scale → RWA), *mechanism* from *threshold* (a cascade is real even
   where the "3.5%" number is contested). Grade each layer on its own evidence; never let a
   robust core launder an oversold headline (this is exactly the failure the self-verification
   found in 8 of 9 of the project's own claims).
4. **Compose to the headline.** A multi-layer entry still carries **one** `grade` in its
   frontmatter, and it is scoped to **what the entry's title actually asserts** — *not*
   mechanically to the most-conservative layer. The per-layer split lives in the Claim prose and
   the `falsification_trigger`, not necessarily in a second grade-line. So a *pre-hedged* title
   ("real but conditional, not universal"; "…are systematically *followed by*…") keeps the robust
   core's grade while its REFUTED/OPEN sub-layers are tracked below it (SAA-025, SAA-031); a title
   that *implies* the contested causal reading must instead drop to that layer's grade
   (SAA-023/024, SAA-032–035). This does **not** relax rule 3 — the title must not overstate; it
   is the rule that decides *which* layer the single grade tracks. (An independent
   grade-calibration of all 35 entries, 2026-06-21, found this convention applied consistently,
   with 0 rubric violations.)

**Movement between grades** is driven by evidence, not time: a new replication, a failed
replication, a meta-analysis, a methodological critique, or a **`falsification_trigger` firing**
(see §3). Default to the *more conservative* grade when genuinely torn — the project's whole
value is that it does not over-claim.

---

## 3. The reusable adversarial prompts

These are the actual prompts the verification runs use, kept here so anyone — a second grader,
a contributor, a future model — can reproduce the process rather than trust its output.

### 3a. Grade / re-grade a single claim

> Adversarially verify ONE claim. Default to skepticism. Steelman the strongest version first,
> then try hardest to refute it against the empirical literature. Grade it **ROBUST /
> CONTESTED / REFUTED / OPEN** (evidence) — or **HOLDS / QUALIFIED / WEAK / BREAKS** if it is a
> plan/source claim. Give: the strongest evidence *for*, the strongest evidence *against*, your
> reasoning, and the **minimal fix** that would strengthen the claim or force an honest
> downgrade. Cite sources with URLs. Separate effect from interpretation, instrument from
> construct, mechanism from threshold.

### 3b. Red-team a whole plan from one angle

> Try hard to make this plan FATAL from ONE angle (co-option, infeasibility, the
> measurement-doesn't-change-power objection, reflexivity, the cascade never igniting, …).
> Mount the strongest version of the attack with historical precedent and base rates. Then judge
> severity: **FATAL** (sinks it), **SERIOUS** (needs redesign), **MANAGEABLE** (survivable with a
> stated mitigation). Give the concrete mitigation. Be honest — if it's fatal, say so.

### 3c. Re-check before committing (the discipline that catches errors)

> Before this grade is committed, re-check it adversarially: is the venue/citation correct? Is
> the grade over-promoted? Is any refutation too strong to be fair? *(This step has repeatedly
> caught real errors — a wrong journal, an over-graded ROBUST, an over-refutation — see
> [`CHRONICLE.md`](CHRONICLE.md) § Method lessons.)*

---

## 4. The re-grade workflow

A re-grade is triggered by **(a)** new evidence, **(b)** a `falsification_trigger` firing, or
**(c)** the **staleness gate** flagging an entry past its `review_interval_days`. Then:

1. Re-run prompt **3a** on the claim against current evidence.
2. Compare the result to the entry's current grade.
3. **If the grade changes:** update `grade:` (and `index.json`), rewrite the evidence section,
   and record the change + date.
4. **If the grade holds:** that is still a review — update `last_reviewed:` to today so the
   staleness gate resets.
5. Run `make verify` (validate + staleness + tests + recompute) before committing.

Either way, **`last_reviewed` moves** — a review that found "no change" is a real review, and
the gate must see it.

---

## 5. Adding a new entry

1. Copy the template below to `ledger/SAA-NNN-short-slug.md` (next free number).
2. Fill every required field. `last_reviewed` starts equal to `verified`.
   `review_interval_days` follows the grade default (ROBUST/REFUTED 540, CONTESTED 270,
   OPEN 180) unless you set an explicit shorter leash.
3. Add the matching row to `ledger/index.json` (`id`, `grade`, `domain`, `file`, `title`).
4. Run `make validate` — it checks the structure and that the file and `index.json` agree.

```markdown
---
id: SAA-NNN
title: One-sentence claim
grade: ROBUST | CONTESTED | REFUTED | OPEN
domain: <e.g. social-change>
verified: YYYY-MM-DD
last_reviewed: YYYY-MM-DD
review_interval_days: 540
sources:
  - "Author (Year). Title. Venue. — https://…"
falsification_trigger: "Downgrade/withdraw if …"
---

## Claim
## Evidence
## Caveats / scope
```

---

## 6. The second grader (breaking the bus-factor)

The R5 fix is not complete until **someone other than the author can grade**. The protocol makes
that possible; onboarding one person makes it real.

- **Onboarding:** a new grader reads this file, [`what-is-tested.md`](what-is-tested.md), and one
  existing entry of each grade, then runs `make verify` once to see the gates pass.
- **Independent grading:** for a contested or high-stakes entry, the second grader grades it
  **without first seeing the other's verdict** (prompt 3a), to keep the two judgments independent.
- **Reconciliation:** if the two grades agree, record it. **If they disagree, the more
  conservative grade wins** (ROBUST → CONTESTED → OPEN → REFUTED-of-the-strong-form), and the
  disagreement is noted in the entry — the project never resolves a tie by over-claiming.
- **Bus-factor check:** before the publication gate opens, at least one entry must have been
  graded end-to-end by someone who is not the author, as proof the substrate actually transfers.

---

## 7. What this does and does not guarantee

It guarantees the **mechanical** floor: required fields, a valid grade, a falsifier, sources, and
agreement with the index — all machine-checked. It does **not** guarantee good *judgment*; that is
what the second grader, the adversarial prompts, and the cited evidence are for. The protocol's
job is to make sure judgment is *applied, recorded, reproducible, and re-checkable by someone
else* — not locked in one person's head.

*This protocol is enforced by [`../src/ledger_validate.py`](../src/ledger_validate.py) and
[`../src/ledger_staleness.py`](../src/ledger_staleness.py). It implements Tier-0 ② of the
priority fixes in [`verifications/plan-for-peace.md`](verifications/plan-for-peace.md).*
