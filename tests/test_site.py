# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Structural integrity checks for the static site — the markup half of "every public
surface machine-checked".

The counts/figure gates already pin the site's *numbers* to the data; these pin its
*structure*: every class used in the HTML has a CSS rule (a missing one shipped once — the
OPEN grade pill), in-page anchors resolve, external links are https-only, accessibility
attributes are present, and the pure-HTML disclosure controls stay balanced. Stdlib only.
"""
import os
import re
import unittest

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def _read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return f.read()


HTML = _read("site/index.html")
CSS = _read("site/style.css")


class TestSiteIntegrity(unittest.TestCase):
    def test_every_class_has_a_css_rule(self):
        # dead markup / typo'd class names render silently unstyled — catch them
        used = set()
        for blob in re.findall(r'class="([^"]+)"', HTML):
            used.update(blob.split())
        defined = set(re.findall(r"\.([A-Za-z][\w-]*)", CSS))
        self.assertEqual(sorted(used - defined), [],
                         "class used in index.html with no rule in style.css")

    def test_inpage_anchors_resolve(self):
        anchors = set(re.findall(r'href="#([^"]+)"', HTML))
        ids = set(re.findall(r'id="([^"]+)"', HTML))
        self.assertEqual(sorted(anchors - ids), [], "in-page anchor with no matching id")

    def test_external_links_are_https(self):
        self.assertEqual(re.findall(r'href="http://[^"]*"', HTML), [],
                         "external link over plain http")

    def test_role_img_has_aria_label(self):
        self.assertEqual(re.findall(r'role="img"(?![^>]*aria-label)', HTML), [],
                         "role=img without an aria-label")

    def test_disclosure_controls_balanced(self):
        self.assertEqual(HTML.count("<details"), HTML.count("</details>"))
        self.assertEqual(HTML.count("<summary"), HTML.count("</summary>"))
        self.assertEqual(HTML.count("<details"), HTML.count("<summary"),
                         "every <details> fold needs its <summary> control")

    def test_skip_link_outranks_sticky_chrome(self):
        """The focused skip link must paint above any top-edge sticky chrome, or the page's
        primary keyboard affordance could be hidden. CORRECTION: this test's original
        docstring claimed the sticky nav had actually covered the skip link; independent
        verification showed that regression was impossible (absolute-at-top vs sticky-below-
        hero never overlap). The invariant is kept as a forward guard — future sticky chrome
        pinned to the top edge WOULD collide — but no real regression ever shipped.
        The guard discovers sticky rules from the stylesheet itself, so chrome added later
        (a toolbar, a banner) is covered without editing this test."""
        def zvalue(body):
            m = re.search(r"z-index:\s*(\d+)", body)
            return int(m.group(1)) if m else 0
        skip = re.search(r"\.skip\s*\{([^{}]*)\}", CSS)
        self.assertIsNotNone(skip, "no rule for .skip")
        # leaf rule blocks only (bodies without braces), so rules inside @media are seen too
        sticky = [(sel.strip(), zvalue(body))
                  for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", CSS)
                  if re.search(r"position:\s*sticky", body)
                  for sel in selectors.split(",")]
        self.assertTrue(sticky, "expected at least one sticky rule (the section nav)")
        for sel, z in sticky:
            self.assertGreater(zvalue(skip.group(1)), z,
                               f".skip must stack above sticky {sel} or focusing it is invisible")

    def test_grade_pills_cover_the_vocabulary(self):
        # the legend must style all four grades (the OPEN pill was once missing)
        for g in ("g-robust", "g-contested", "g-refuted", "g-open"):
            self.assertIn(f".{g}", CSS, f"grade pill .{g} has no CSS rule")


if __name__ == "__main__":
    unittest.main()
