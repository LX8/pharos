---
id: SAA-010
title: The "energy" that drives cascades is complex contagion, not a mystical field
grade: ROBUST
domain: social-change
verified: 2026-06-02
last_reviewed: 2026-06-18
review_interval_days: 540
sources:
  - "Centola, D. & Macy, M. (2007). Complex Contagions and the Weakness of Long Ties. AJS. — https://www.journals.uchicago.edu/doi/10.1086/521848"
  - "Granovetter, M. (1978). Threshold Models of Collective Behavior. — https://sociology.stanford.edu/publications/threshold-models-collective-behavior"
  - "Shalizi, C. R. & Thomas, A. C. (2011). Homophily and Contagion Are Generically Confounded in Observational Social Network Studies. Sociological Methods & Research. — https://doi.org/10.1177/0049124111404820"
  - "\"Diffusion of complex contagions is shaped by a trade-off between reach and reinforcement\" (2024). arXiv:2411.07907. — https://arxiv.org/abs/2411.07907"
falsification_trigger: "Downgrade if simple-contagion (single-contact) models are shown to fully explain social-movement and norm spread without reinforcement effects. Demote the *network-structure* rider (clustering + wide bridges) separately — it is already contested: the reach-vs-reinforcement trade-off (arXiv:2411.07907, 2024) shows clustering helps only in a small region of parameter space and, in most cases, does not out-reach random networks."
---

## Claim
The "shared energy" of a movement is a structure, not a force. Unlike a virus
(simple contagion, one contact suffices), social and behavioral change is a
**complex contagion**: people adopt only after *multiple reinforcing contacts*
from different trusted sources. That **reinforcement core is robust.** A second,
weaker rider — that it therefore spreads best through tightly-clustered groups
joined by "wide bridges" — is **contested**: the clustering-vs-reach trade-off
(arXiv:2411.07907, 2024) shows clustered networks out-spread random ones only in a
small region of parameter space, and usually do not. So: reinforcement, yes;
a specific winning network geometry, not settled.

## Evidence
Centola & Macy 2007 establishes the reinforcement mechanism; the *network
geometry* it was thought to require (clustering + wide bridges) is the part now in
dispute (see falsification trigger). The classic model is reproduced in
[`sim_complex_contagion`](../src/sims/sim_complex_contagion.py): a complex contagion
sweeps a clustered ring lattice but stalls once randomly rewired — the *logic* is
sound; its real-world generality is the contested part.

## Why it matters
The operational read of "energy" is **reinforcement density** — measurable in
controlled settings, though hard to identify in the observational data a movement
actually generates (homophily and contagion are generically confounded there —
Shalizi & Thomas 2011), so "all measurable, all buildable" is too strong. The
robust, usable part stands: disinformation is corrosive precisely because it
destroys *trusted reinforcing* signal, which is why an open, trustworthy
information commons is a load-bearing input the cascade runs on.
