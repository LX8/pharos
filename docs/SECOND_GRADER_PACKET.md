<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# SECOND_GRADER_PACKET.md — onboarding a second pair of eyes

> **For the founder:** this is the ready-to-send packet for the person you recruit. §1 is a
> copy-paste invitation; §2–§5 are the brief they read; §6 is their path onward. Everything
> here is self-contained — your recruit does not need to know the repo to start.
>
> **One rule matters more than all others: do not show them the ledger before they code.**
> Their value in step one is exactly that they *haven't* seen our grades.

---

## 1. The invitation (copy, adapt, send)

> I run a small open-science project that keeps a graded, falsifiable evidence ledger about
> how democratic backsliding works — every claim carries sources and a pre-registered
> "what would change our minds" condition. I committed to testing my
> own instrument for directional bias, the way Bright Line Watch tested its own experts —
> and the test needs a coder who *hasn't* seen my grades. That's you, if you're willing.
>
> The task: read ~40 short claim texts (grades masked out) and tag each one with a single
> letter for its *direction* — about 90 minutes to two hours, once. The method was frozen
> before anyone looks at the answer, and the result gets published whichever way it comes
> out, with credit to you if you want it. If you enjoy it, there's a standing second role:
> being the independent second grader the project still needs. Interested?

## 2. What this project is (all your recruit needs to know now)

A public research commons asking what science can measurably do to
contain authoritarianism. Its core artifact is an evidence ledger: short, sourced,
**graded** claims (ROBUST / CONTESTED / REFUTED / OPEN), each with a pre-registered
falsification trigger. Because one person wrote and graded those entries, the project
pre-registered an audit of itself: *do claims that say "things are getting worse" get
graded more favorably than claims that are reassuring?* A fair test requires coders who
can't see the grades — hence this packet.

The full protocol (frozen before any coding) is
[`BIAS_AUDIT_PREREGISTRATION.md`](BIAS_AUDIT_PREREGISTRATION.md). Your recruit doesn't
need to read it to code; they only need §3 below.

## 3. The blind coding task

**You receive** one file, `blind_pack.md`: every ledger entry's title and claim text, in a
shuffled order, under opaque codes (`E01`, `E02`, …), with grade words masked as `▓▓▓`.

**You must not**, until your coding is handed in: browse the project repository, discuss
items with anyone (including the other coder), or open any file named `blind_key.json` —
it unblinds the codes.

**For each item, assign exactly one valence letter:**

| Letter | Meaning | Test |
|---|---|---|
| **D** | Decline-affirming | *If this claim is true, it supports "authoritarian dynamics are real, serious, or worsening."* |
| **R** | Reassuring / debunking | *If true, it is reassuring, cuts against an alarm, or debunks a decline-side belief.* |
| **N** | Neutral / mechanism | *A definition, method, or how-things-work claim with no direction about the current state of the world.* |

Also mark your **confidence** (high / low) per item. When torn between two letters, choose
**N** — the analysis excludes N by design, so "unsure" never contaminates the directional test.

**Worked examples** (invented for this packet — deliberately *not* real entries, so reading
them cannot pre-expose you):

- *"Two independent expert surveys agree that press freedom declined in dozens of countries
  over the last decade."* → **D** (if true, decline is real and measured).
- *"Surveys show people substantially overestimate how many of their political opponents
  support violence."* → **R** (if true, it debunks an alarming belief).
- *"Opinion cascades in models require a committed minority of roughly one-tenth of the
  population."* → **N** (a mechanism; says nothing about whether decline is happening now).
- *"A widely cited method for measuring backsliding has a disputed reliability record."*
  → **R** (if true, it cuts against confidence in decline measurements).

**What you hand back:** a JSON file mapping every code to its letter —

```json
{ "E01": "D", "E02": "N", "E03": "R", "...": "..." }
```

— plus a short note listing your low-confidence codes and anything that felt ambiguous.
Expect ~90–120 minutes for the full pack.

## 4. What happens with your coding

A second coder does the same independently. The two codings are reconciled once
(disagreements discussed; unresolved → N, the conservative rule), then scored by a
pre-registered statistic whose skew criterion was frozen in code *before* any coding
existed. The result — **including a null** — is published in the project's trust page with
the raw tables, and you are credited as a coder unless you prefer otherwise.

## 5. Mechanics (founder runs these; recruit never needs the repo)

```bash
make bias-pack                    # generates build/bias-audit/blind_pack.md + blind_key.json
# send the coder ONLY blind_pack.md; keep blind_key.json sealed
python3 src/bias_audit.py --score reconciled.json --key build/bias-audit/blind_key.json
```

## 6. The path onward: becoming the second grader

If the coding went well and your recruit is willing, the standing role is **independent
second grader** — the human step the project's launch checklist has been waiting on:

1. Read [`docs/GRADING_PROTOCOL.md`](GRADING_PROTOCOL.md) — the grade vocabulary, the
   rubric, and the adversarial prompts.
2. Pick any one ledger entry (after the blind coding is submitted, browsing is fine —
   `./pharos coverage` shows where a second look adds most).
3. Re-grade it end-to-end: verify each citation actually says what the entry uses it for,
   run the rubric, and state a grade with reasons.
4. Reconcile with the founder. On a genuine tie, **the more conservative grade wins** —
   that rule exists precisely so the second grader has real teeth.

One completed end-to-end grade closes the project's last human launch-gate and breaks its
bus factor. That is the entire ask — one afternoon of coding, one entry graded well.
