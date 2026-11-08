# The Pharos Ledger

*An open, versioned, adversarially-verified record of what science actually
shows about containing authoritarianism and how societies change — each claim
**graded** and carrying a **falsification trigger**.*

> **Why this exists.** Social change cascades on *trusted, reinforcing* signal
> (complex contagion — see [`SAA-010`](SAA-010-energy-is-complex-contagion.md)).
> Disinformation destroys exactly that. The Ledger is a small piece of the
> antidote: a public good anyone can read, cite, fork, and check — built to the
> standard *cite only what is measured*. It is the **first node** — something
> true and reusable that aligned people can gather around.

## How an entry works

Every entry is one file with machine-readable frontmatter + a short body:

- **`grade`** — the current evidentiary status (below).
- **`falsification_trigger`** — the *pre-registered* condition under which the
  entry would be downgraded. This is the point: the Ledger can be proven wrong,
  in public, on the record. That is what separates it from propaganda *and* from
  well-meaning-but-unreplicated advocacy.
- **`sources`** — primary, with links. No claim without a measured source.

## Grading scheme

| Grade | Meaning |
|---|---|
| ✅ **ROBUST** | Verified against primary sources; uncontested or convergent across independent lines |
| ⚠️ **CONTESTED** | Real evidence on both sides; replication failures or unresolved expert dispute |
| ❌ **REFUTED** | Fails verification — *do not build on it* |
| ❓ **OPEN** | The evidence does not yet answer the question |

## Browse the entries

The **full, always-current index** — every entry grouped by grade, plus the
**falsification watch** (each entry's "what would change our minds" trigger in one place)
and a coverage-by-domain map — is **[`INDEX.md`](INDEX.md)**. It is regenerated from each
entry's frontmatter by `make index` and drift-gated, so it can never silently diverge from
the source of truth. (This file deliberately does *not* duplicate the table: a hand-kept
copy here once drifted to 15 rows while the ledger held 38.)

- **Read it:** [`INDEX.md`](INDEX.md) — by grade + falsification watch + coverage
- **Search it from the CLI:** `./pharos ledger` · `./pharos ledger --grade ROBUST` · `./pharos watch` · `./pharos coverage`
- **Parse it:** [`index.json`](index.json) — machine-readable

## Use · cite · fork · contribute

- **Use/cite:** entries are CC BY-SA 4.0 (see repo `LICENSE`); cite the entry ID
  and the underlying primary sources.
- **Fork/build on it:** the structured frontmatter is meant to be parsed and
  reused. Build on it — that is how the bridges between clusters form.
- **Contribute / challenge:** the strongest contribution is meeting an entry's
  **falsification trigger** with evidence. Bring the measured source; if it
  meets the trigger, the entry is downgraded, dated, and credited.

## Provenance

Entries SAA-001–007 derive from [`../REPORT.md`](../REPORT.md) (an adversarial
deep-research run: 25 claims verified, 21 confirmed / 4 refuted). Entries
SAA-008–011 derive from a verification of the critical-mass / social-cascade
theory (2026-06-02); SAA-012–015 from a replication-graded cross-disciplinary
survey (2026-06-03). Entries SAA-016–035 were added in four **verify-first
batches** (psychology, sociology, recent-empirical, political-economy;
2026-06-18) — every citation web-confirmed before writing — and SAA-036–038
(2026-06-28) fill the thinnest coverage lenses under the same discipline, each
independently reviewed after writing. All grades are **adversarially re-checked**
before entry. Bound by the ethical covenant in [`../NOTICE`](../NOTICE) §7:
*watch power, not people.*
