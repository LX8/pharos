# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Reproducible environment for the Pharos quantitative pillar. The project is
# stdlib-only, so there is nothing to pip-install — the image just pins Python and
# runs the deterministic, network-free gate. Same result on a laptop, in CI, or on
# any rented box:
#
#   docker build -t pharos . && docker run --rm pharos        # -> verify-offline
#   docker run --rm pharos make dashboard                     # -> GREEN/RED report
#
FROM python:3.12-slim

WORKDIR /pharos

# `make` runs the gate targets; `git` backs verify-offline's drift check.
RUN apt-get update \
    && apt-get install -y --no-install-recommends make git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Default: the deterministic gate — recompute indicators from the committed
# snapshots (no network), check for drift, run the tests + ledger + honesty audits.
CMD ["make", "verify-offline"]
