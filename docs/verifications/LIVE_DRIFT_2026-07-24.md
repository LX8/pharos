<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Live-drift measurement — 2026-07-24

*First execution of the live-drift test against upstream. A dated measurement, not an
adopted re-pin — the pin is unchanged. Recorded so "is the light still lit?" has an
answer on the record, not just in a terminal.*

## What was tested

`make drift` (live fetch of WGI + V-Dem + Freedom House via OWID, diffed against the
2026-06-18 pin, pin restored byte-for-byte). Run ~5 weeks after the pin.

## Result

**The published indicators are current.** `drift_check` flagged the WGI files as
changed, but the change is **6 country-name spelling revisions only** — zero score
changes, zero CI changes, zero verdict flips:

- 1,222 / 1,222 country-dimension cells: identical `sc_*`, `lb_*`, `ub_*`, `z`, `verdict`.
- Headline counts byte-identical: **88 declines, 54 improvements, 1.63 : 1**, every
  dimension unchanged (VA 33:6, PV 19:7, …).
- Per-country `latest`-score deltas: **max 0.000** (no movement at all in the values).
- V-Dem and Freedom House (via OWID): **no drift** — unchanged since the pin.

So the only upstream movement is minor WGI metadata (country name spellings). A
re-pin is *not* required for correctness; it would only refresh the name spellings.
The decision to re-pin is deferred to the next scheduled review.

## What this measures

That the project's headline numbers are not stale: as of 2026-07-24, recomputing
from the live world reproduces the committed figures exactly (substantive content;
name spellings aside). The honest-uncertainty indicators and the forecast input
panel are still current.

> **Correction (2026-10-31).** "The forecast input panel is still current" was wrong in one respect:
> the check could not see a newly published year, because both the pin and the recompute stop at 2024.
> The live file already held 2025 (the October 2026 download matches the June pin on every 1990-2024
> value, so it is the same release). `drift_check.py` now reports the newest upstream year.

## How to re-run

```bash
SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())") make drift
```

(`SSL_CERT_FILE` is needed only on Python installs that lack system CA certificates,
as some macOS builds do; it points TLS verification at certifi's bundle and does not touch
the project's stdlib-only guarantee. With system certificates, plain `make drift` suffices.)
