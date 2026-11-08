## What & why

<!-- One paragraph: what this changes, and which law / roadmap item / falsification trigger it serves. -->

## Verified

- [ ] `make dashboard` is GREEN (all seven audits)
- [ ] `make verify-offline` passes — the real gate; the pre-push hook runs it
- [ ] If any count or computed figure changed: re-pinned via `python3 src/audit_counts.py --update`
- [ ] New evidence citations are web-verified — *cite only what is measured*
- [ ] New files carry an SPDX header or are covered by `REUSE.toml`
- [ ] *Watch power, not people*: no published data below country / institution level

## Notes

<!-- Test counts, the doc/RFC this ticks, anything a reviewer should know. Keep the history linear (rebase). -->
