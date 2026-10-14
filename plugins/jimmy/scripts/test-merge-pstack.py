#!/usr/bin/env python3
import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("merge", Path(__file__).with_name("merge-pstack.py"))
merge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(merge)


class MergeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base, self.source, self.plugin, self.output = [self.root / name for name in ("base", "source", "plugin", "output")]
        for root in (self.base, self.source):
            for directory in ("skills", "agents"):
                (root / directory).mkdir(parents=True)

    def write(self, root, relative, text):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def run_merge(self):
        args = ["merge-pstack.py", "--base", str(self.base), "--source", str(self.source), "--output", str(self.output)]
        with patch.object(sys, "argv", args), patch.object(merge.parity, "PLUGIN", self.plugin), contextlib.redirect_stdout(io.StringIO()) as output:
            result = merge.main()
        return result, output.getvalue()

    def test_preserves_local_adaptation_and_upstream_fix(self):
        path = "skills/example/SKILL.md"
        self.write(self.base, path, "Title\n\nRuntime: Cursor\n\nBehavior: old\n")
        self.write(self.source, path, "Title\n\nRuntime: Cursor\n\nBehavior: fixed\n")
        self.write(self.plugin, path, "Title\n\nRuntime: Codex\n\nBehavior: old\n")
        result, _ = self.run_merge()
        self.assertFalse(result)
        self.assertEqual((self.output / path).read_text(), "Title\n\nRuntime: Codex\n\nBehavior: fixed\n")

    def test_reports_conflict_without_writing_plugin(self):
        path = "skills/example/SKILL.md"
        for root, text in ((self.base, "old\n"), (self.source, "upstream\n"), (self.plugin, "local\n")):
            self.write(root, path, text)
        result, output = self.run_merge()
        self.assertTrue(result)
        self.assertIn("CONFLICT skills/example/SKILL.md", output)
        self.assertEqual((self.plugin / path).read_text(), "local\n")
        self.assertIn("<<<<<<<", (self.output / path).read_text())

    def test_maps_new_helper_to_jimmy_path(self):
        self.write(self.source, "skills/poteto-help/SKILL.md", "New helper\n")
        result, _ = self.run_merge()
        self.assertFalse(result)
        self.assertEqual((self.output / "skills/jimmy-help/SKILL.md").read_text(), "New helper\n")

    def test_reports_upstream_removal_without_deleting_local(self):
        path = "skills/example/SKILL.md"
        self.write(self.base, path, "old\n")
        self.write(self.plugin, path, "local\n")
        result, output = self.run_merge()
        self.assertTrue(result)
        self.assertIn("REMOVED skills/example/SKILL.md", output)
        self.assertEqual((self.plugin / path).read_text(), "local\n")

    def test_skips_unchanged_upstream_file(self):
        path = "skills/example/SKILL.md"
        self.write(self.base, path, "old\n")
        self.write(self.source, path, "old\n")
        self.write(self.plugin, path, "adaptation\n")
        result, output = self.run_merge()
        self.assertFalse(result)
        self.assertIn("0 updated resources", output)
        self.assertFalse((self.output / path).exists())


if __name__ == "__main__":
    unittest.main()
