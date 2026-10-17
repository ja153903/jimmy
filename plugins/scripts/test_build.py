from __future__ import annotations

import hashlib
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest


BUILD = Path(__file__).with_name("build.py")


def write(root: Path, relative: str, content: str, mode: int = 0o644) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(mode)


def source_fixture(root: Path) -> None:
    write(root, ".cursor-plugin/plugin.json", '{"version":"0.15.25"}\n')
    write(root, "jimmy/LICENSE", "MIT\n")
    write(root, "jimmy/README.md", "Upstream README\n")
    write(root, "jimmy/docs/guide.md", "[Mode](../skills/jimmy-mode/SKILL.md)\n")
    write(root, "jimmy/agents/helper.md", "---\nname: helper\ndescription: Help.\nis_background: true\n---\n\nAgent.\n")
    write(root, "jimmy/skills/jimmy-mode/SKILL.md", "---\nname: Jimmy Mode\ndescription: Old mode.\ndisable-model-invocation: true\nicon: crown\n---\n\nOriginal mode.\n")
    write(root, "jimmy/skills/helper/SKILL.md", "---\nname: Helper\ndescription: Help.\ndisable-model-invocation: true\n---\n\nOriginal helper.\n")
    files = {}
    for path in root.rglob("*"):
        if path.is_file():
            files[path.relative_to(root).as_posix()] = {
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "mode": stat.S_IMODE(path.stat().st_mode),
            }
    lock = {
        "repository": "https://github.com/cursor/plugins.git",
        "path": "pstack",
        "commit": "a" * 40,
        "version": "0.15.25",
        "files": files,
    }
    write(root, "upstream.lock.json", json.dumps(lock))
    write(root, "adapters/common/docs/efficiency.md", "# Efficiency\n")
    write(root, "adapters/common/skills/jimmy/SKILL.md", "---\nname: jimmy\ndescription: Main mode.\n---\n\nMain mode.\n")
    write(root, "adapters/common/skills/jimmy-mode/SKILL.md", "---\nname: jimmy-mode\ndescription: Router.\n---\n\n[Jimmy](../jimmy/SKILL.md).\n")
    write(root, "adapters/common/skills/helper/SKILL.md", "---\nname: Helper\ndescription: Common.\n---\n\nCommon.\n")
    for host in ("codex", "claude"):
        write(root, f"adapters/{host}/docs/runtime.md", f"# {host} runtime\n")
    write(root, "adapters/codex/skills/helper/SKILL.md", "---\nname: Helper\ndescription: Codex.\n---\n\nCodex override.\n")


class BuildCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        source_fixture(self.root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_build(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(BUILD), "--root", str(self.root), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_builds_both_hosts_and_check_is_stable(self) -> None:
        first = self.run_build()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout.strip(), "PASS: codex and claude packages match pinned source and adapters")
        codex = self.root / "dist/codex"
        claude = self.root / "dist/claude"
        self.assertIn("Codex override.", (codex / "skills/helper/SKILL.md").read_text())
        self.assertIn("Common.", (claude / "skills/helper/SKILL.md").read_text())
        self.assertIn("name: helper", (codex / "skills/helper/SKILL.md").read_text())
        self.assertNotIn("disable-model-invocation", (codex / "skills/helper/SKILL.md").read_text())
        self.assertEqual((codex / "skills/helper/agents/openai.yaml").read_text(), "policy:\n  allow_implicit_invocation: false\n")
        self.assertFalse((codex / "skills/jimmy/agents/openai.yaml").exists())
        self.assertIn("disable-model-invocation: true", (claude / "skills/helper/SKILL.md").read_text())
        self.assertNotIn("disable-model-invocation", (claude / "skills/jimmy/SKILL.md").read_text())
        self.assertEqual((codex / "docs/upstream-mode.md").read_text(), (self.root / "jimmy/skills/jimmy-mode/SKILL.md").read_text())
        self.assertTrue((codex / ".codex-plugin/plugin.json").is_file())
        self.assertTrue((claude / ".claude-plugin/marketplace.json").is_file())
        before = {path.relative_to(self.root).as_posix(): path.read_bytes() for path in (self.root / "dist").rglob("*") if path.is_file()}
        checked = self.run_build("--check")
        self.assertEqual(checked.returncode, 0, checked.stderr)
        after = {path.relative_to(self.root).as_posix(): path.read_bytes() for path in (self.root / "dist").rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_check_detects_stale_bytes_and_modes_without_repairing(self) -> None:
        self.assertEqual(self.run_build().returncode, 0)
        stale = self.root / "dist/codex/stale.txt"
        stale.write_text("stale")
        changed = self.root / "dist/claude/skills/helper/SKILL.md"
        changed.write_text("changed")
        mode = self.root / "dist/codex/LICENSE"
        mode.chmod(0o755)
        result = self.run_build("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("stale: codex/stale.txt", result.stderr)
        self.assertIn("different bytes: claude/skills/helper/SKILL.md", result.stderr)
        self.assertIn("different mode: codex/LICENSE", result.stderr)
        self.assertEqual(stale.read_text(), "stale")
        self.assertEqual(changed.read_text(), "changed")
        self.assertEqual(stat.S_IMODE(mode.stat().st_mode), 0o755)
        self.assertEqual(self.run_build().returncode, 0)
        self.assertEqual(self.run_build("--check").returncode, 0)

    def test_source_drift_fails_before_dist_changes(self) -> None:
        self.assertEqual(self.run_build().returncode, 0)
        output = self.root / "dist/codex/build-info.json"
        before = output.read_bytes()
        write(self.root, "jimmy/skills/helper/SKILL.md", "changed upstream")
        result = self.run_build()
        self.assertEqual(result.returncode, 1)
        self.assertIn("source differs from upstream pin", result.stderr)
        self.assertEqual(before, output.read_bytes())

    def test_codex_policy_preserves_other_yaml_fields(self) -> None:
        write(
            self.root,
            "adapters/codex/skills/helper/agents/openai.yaml",
            "interface:\n  display_name: Helper\npolicy:\n  allow_implicit_invocation: true\n  may_be_disabled: false\n",
        )
        result = self.run_build()
        self.assertEqual(result.returncode, 0, result.stderr)
        policy = (self.root / "dist/codex/skills/helper/agents/openai.yaml").read_text()
        self.assertIn("display_name: Helper", policy)
        self.assertIn("allow_implicit_invocation: false", policy)
        self.assertIn("may_be_disabled: false", policy)

    def test_broken_local_link_prevents_publish(self) -> None:
        write(self.root, "adapters/common/docs/efficiency.md", "[Missing](missing.md)\n")
        result = self.run_build()
        self.assertEqual(result.returncode, 1)
        self.assertIn("docs/efficiency.md -> missing.md", result.stderr)
        self.assertFalse((self.root / "dist/codex").exists())


if __name__ == "__main__":
    unittest.main()
