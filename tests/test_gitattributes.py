# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guards the cross-platform reproducibility invariant that .gitattributes protects.

The byte-exact offline gate (`make verify-offline`) only holds if every committed generated file is
checked out with the SAME bytes the deterministic recompute writes — on every platform, regardless of
core.autocrlf. That requires (a) .gitattributes to pin the load-bearing files, and (b) the committed
bytes to actually match their generator's line endings (csv module → CRLF, json.dump / digest → LF).
This test fails if either the policy or the reality regresses — an invisible property no other test
covers, since it only bites on a Windows/autocrlf clone none of the offline tests run on.
"""
import os
import unittest

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def _attr_lines():
    with open(os.path.join(REPO, ".gitattributes"), encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.lstrip().startswith("#")]


class TestPolicyPresent(unittest.TestCase):
    def test_gitattributes_pins_the_load_bearing_files(self):
        lines = _attr_lines()
        # CSVs must be binary (exact bytes, no EOL conversion); JSON + the ledger index pinned to LF.
        self.assertTrue(any("*.csv" in ln and "-text" in ln for ln in lines), "CSVs must be -text")
        self.assertTrue(any("*.json" in ln and "eol=lf" in ln for ln in lines), "JSON must be eol=lf")
        self.assertTrue(any("INDEX.md" in ln and "eol=lf" in ln for ln in lines), "INDEX.md must be eol=lf")


class TestBytesMatchGenerators(unittest.TestCase):
    def test_committed_csvs_are_crlf(self):
        # the csv module writes CRLF; the committed bytes must carry it or the pin is a lie
        for root in ("data/derived", "data/snapshots"):
            for name in sorted(os.listdir(os.path.join(REPO, root))):
                if not name.endswith(".csv"):
                    continue
                with open(os.path.join(REPO, root, name), "rb") as f:
                    raw = f.read()
                if b"\n" not in raw:
                    continue  # a single-line / header-only file has no ending to check
                self.assertIn(b"\r\n", raw, f"{root}/{name} lost its CRLF endings")

    def test_committed_lf_files_have_no_carriage_returns(self):
        # json.dump and the digest write LF; a stray \r would break the byte-exact compare after checkout
        targets = [os.path.join("ledger", "INDEX.md")]
        for root in ("data/derived", "data/snapshots"):
            targets += [os.path.join(root, n) for n in os.listdir(os.path.join(REPO, root)) if n.endswith(".json")]
        for rel in targets:
            with open(os.path.join(REPO, rel), "rb") as f:
                raw = f.read()
            self.assertNotIn(b"\r", raw, f"{rel} contains a carriage return; must be LF-only")


if __name__ == "__main__":
    unittest.main()
