# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline tests for the vendorable data client (docs/IMPACT.md lever L5).

Pins the contract's reuser-facing promises: every surface loads, the typed tables agree with
the pinned headline figures, the file is genuinely vendorable (single file, stdlib-only,
importable from anywhere), and it is read-only.
"""
import ast
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pharos_client as px  # noqa: E402

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
CLIENT = os.path.join(REPO, "src", "pharos_client.py")


class TestSurfacesLoad(unittest.TestCase):
    def test_tables_match_pinned_figures(self):
        gov = px.governance_table(REPO)
        self.assertEqual(len(gov), px.governance(REPO)["overall"]["dimension_country_cells"])
        noise = sum(1 for r in gov if r["verdict"] == "NO_SIG_CHANGE")
        self.assertEqual(noise, px.governance(REPO)["overall"]["within_noise"])
        div = px.divergence_table(REPO)
        concur = sum(1 for r in div if r["label"] == "CONCUR-DECLINE")
        self.assertEqual(concur, px.divergence(REPO)["counts"]["CONCUR-DECLINE"])
        self.assertEqual(len(px.forecast_table(REPO)),
                         len(px.forecast(REPO)["result"]["per_model"]))

    def test_ledger_and_entry_text(self):
        entries = px.ledger(REPO)
        self.assertTrue(all({"id", "grade", "domain", "file", "title"} <= set(e) for e in entries))
        text = px.entry_text(entries[0]["id"], REPO)
        self.assertIn("falsification_trigger", text)
        with self.assertRaises(KeyError):
            px.entry_text("SAA-999", REPO)

    def test_csv_typing(self):
        row = px.governance_table(REPO)[0]
        self.assertIsInstance(row["year_base"], int)
        self.assertIsInstance(row["change"], float)
        div = px.divergence_table(REPO)
        aruba = next(r for r in div if r["iso3"] == "ABW")
        self.assertIs(aruba["wgi_available"], True)     # 'True' -> bool
        self.assertIsNone(aruba["vdem_v_start"])        # '' -> None

    def test_coerce_never_yields_nonfinite_floats(self):
        # 'nan'/'inf' cells would silently poison a reuser's comparisons and sums (NaN != NaN);
        # the honest coercion leaves them as text
        for cell in ("nan", "NaN", "inf", "-inf", "Infinity"):
            self.assertIsInstance(px._coerce(cell), str, cell)
        self.assertEqual(px._coerce("-4.25"), -4.25)    # ordinary floats still coerce


class TestVendorable(unittest.TestCase):
    def test_single_file_stdlib_only(self):
        # the vendoring promise: no import outside the standard library, no local imports
        stdlib = getattr(sys, "stdlib_module_names", None)
        if stdlib is None:
            # the AUTHORITATIVE list needs Python 3.10+; on older Pythons (macOS ships 3.9)
            # fall back to asserting against the exact imports the client is allowed to have,
            # so the property is still enforced everywhere the suite runs
            stdlib = {"csv", "json", "math", "os"}
        with open(CLIENT, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        mods = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                mods.add((node.module or "").split(".")[0])
        self.assertTrue(mods <= set(stdlib), f"non-stdlib imports: {mods}")

    def test_copied_file_works_from_elsewhere(self):
        # copy the one file to a temp dir, import THAT copy, point it at the repo — must work
        with tempfile.TemporaryDirectory() as td:
            shutil.copy(CLIENT, os.path.join(td, "vendored_client.py"))
            sys.path.insert(0, td)
            try:
                import vendored_client  # noqa: F401
                self.assertEqual(len(vendored_client.ledger(REPO)), len(px.ledger(REPO)))
            finally:
                sys.path.remove(td)
                sys.modules.pop("vendored_client", None)

    def test_read_only(self):
        # the client must never open anything for writing
        with open(CLIENT, encoding="utf-8") as f:
            src = f.read()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "open":
                modes = [a for a in node.args[1:2]] + [k.value for k in node.keywords if k.arg == "mode"]
                for m in modes:
                    if isinstance(m, ast.Constant):
                        self.assertNotRegex(str(m.value), r"[wax+]", "client must be read-only")


class TestContractCompleteness(unittest.TestCase):
    """The machine teeth for DATA_CONTRACT.md's additive-only guarantee: a column added to a
    published CSV without documenting it fails the build. (An inline review found two
    undocumented columns — wgi_z, flag_basis_mix — the day the contract shipped; this gate
    keeps the schema and its promise from drifting apart again.)"""

    def test_every_published_column_is_documented(self):
        import csv
        import re
        with open(os.path.join(REPO, "docs", "DATA_CONTRACT.md"), encoding="utf-8") as f:
            contract = f.read()
        for name in ("wgi_governance.csv", "voice_divergence.csv", "forecast_backtest.csv"):
            with open(os.path.join(REPO, "data", "derived", name), newline="", encoding="utf-8") as f:
                cols = next(csv.reader(f))
            for c in cols:
                # instrument-block columns are documented once as their `*_suffix` pattern;
                # match the BACKTICKED token exactly — a bare substring check passes `wgi_z`
                # against `wgi_zz` and the gate silently stops biting
                pattern = re.sub(r"^(wgi|vdem|fh)_", "*_", c)
                self.assertTrue(f"`{c}`" in contract or f"`{pattern}`" in contract,
                                f"{name} column `{c}` is not documented in DATA_CONTRACT.md")


class TestRootDiscovery(unittest.TestCase):
    def test_explicit_bad_root_is_clear(self):
        with self.assertRaises(FileNotFoundError):
            px.find_root("/no/such/checkout")

    def test_walk_up_from_subdir(self):
        old = os.getcwd()
        try:
            os.chdir(os.path.join(REPO, "docs"))
            self.assertEqual(os.path.realpath(px.find_root()), os.path.realpath(REPO))
        finally:
            os.chdir(old)


if __name__ == "__main__":
    unittest.main()
