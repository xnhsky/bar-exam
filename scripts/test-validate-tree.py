#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight self-test for validate-tree.py."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("validate-tree.py")


class ValidateTreeTest(unittest.TestCase):
    def test_counts_class_tokens_with_single_quotes_and_extra_classes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "刑JX001_TREE.html"
            names = "\n".join(f"<div class='branch mm-name'>n{i}</div>" for i in range(13))
            leaves = "\n".join(f"<span class='mm-leaf leaf'>l{i}</span>" for i in range(40))
            questions = "\n".join(f"<button class=\"node mm-q\">q{i}</button>" for i in range(10))
            html = f"""<!doctype html>
<html>
<head><title>刑JX001 — 横向き樹形図 / ARBOR v5.0</title></head>
<body>
<div class='not-mm-name'>distractor</div>
{names}
{leaves}
{questions}
</body>
</html>
"""
            path.write_text(html, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("[ERROR]", result.stdout)
        self.assertIn("mm-name=13", result.stdout)
        self.assertIn("mm-leaf=40", result.stdout)
        self.assertIn("mm-q=10", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
