#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import upstream


SCRIPT = Path(upstream.__file__).resolve()


def git(root: Path, *arguments: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *arguments], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def write(path: Path, content: bytes | str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode() if isinstance(content, str) else content)
    path.chmod(mode)


class UpstreamTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="pstack-upstream-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "--quiet")
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "Upstream Test")
        write(self.repo / "pstack/.cursor-plugin/plugin.json", '{"version":"1.0.0"}\n')
        write(self.repo / "pstack/skills/alpha/SKILL.md", "---\nname: alpha\ndescription: Alpha.\n---\n\nFirst.\n")
        write(self.repo / "pstack/skills/remove/SKILL.md", "---\nname: remove\ndescription: Remove.\n---\n")
        write(self.repo / "pstack/agents/helper.md", "Helper one.\n")
        write(self.repo / "pstack/docs/guide.md", "Guide.\n")
        write(self.repo / "pstack/LICENSE", "License.\n")
        write(self.repo / "pstack/README.md", "Readme.\n")
        self.initial = self.commit("initial")
        self.source = self.base / "source"
        for path in (self.repo / "pstack").rglob("*"):
            if path.is_file():
                relative = path.relative_to(self.repo / "pstack")
                target = self.source / (".cursor-plugin/plugin.json" if relative.as_posix() == ".cursor-plugin/plugin.json" else f"jimmy/{relative}")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
        write(self.source / "adapters/marker.txt", "original adapter\n")
        write(self.source / "scripts/build.py", "from pathlib import Path\nroot = Path(__file__).resolve().parent.parent\nif (root / 'adapters/fail').exists():\n    raise SystemExit(7)\nout = root / 'dist' / 'adapter.txt'\nout.parent.mkdir(parents=True, exist_ok=True)\nout.write_bytes((root / 'adapters/marker.txt').read_bytes())\n")
        self.write_lock(self.initial)

    def commit(self, message: str) -> str:
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "--quiet", "-m", message)
        return git(self.repo, "rev-parse", "HEAD")

    def write_lock(self, commit: str) -> None:
        lock = {
            "repository": upstream.REPOSITORY,
            "path": "pstack",
            "commit": commit,
            "version": "1.0.0",
            "files": upstream.snapshot(self.source),
        }
        write(self.source / upstream.LOCK_FILE, json.dumps(lock, indent=2, sort_keys=True) + "\n")

    def cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *arguments], capture_output=True, text=True, check=False)

    def update(self, ref: str, output: Path) -> subprocess.CompletedProcess[str]:
        return self.cli("update", "--root", str(self.source), "--ref", ref, "--output", str(output), "--repository", str(self.repo))

    def test_update_normalizes_new_upstream_names(self) -> None:
        write(self.repo / "pstack/skills/sample-mode/SKILL.md", "---\nname: Sample Mode\ndescription: Use sample-agent.\n---\n")
        newest = self.commit("add named workflow")
        preview = self.base / "branded-preview"
        result = self.update(newest, preview)
        self.assertEqual(result.returncode, 0, result.stderr)
        normalized = preview / "jimmy/skills/jimmy-mode/SKILL.md"
        self.assertIn("Use jimmy-agent.", normalized.read_text())
        self.assertFalse((preview / "jimmy/skills/sample-mode").exists())
        self.assertEqual(upstream.verify_source(preview)["transform"], "jimmy-brand-v1")

    def test_check_detects_content_mode_addition_and_deletion(self) -> None:
        check = self.cli("check", "--root", str(self.source))
        self.assertEqual(check.returncode, 0, check.stderr)
        self.assertIn(self.initial, check.stdout)
        path = self.source / "jimmy/skills/alpha/SKILL.md"
        original = path.read_bytes()
        path.write_bytes(b"changed\n")
        self.assertIn("changed: jimmy/skills/alpha/SKILL.md", self.cli("check", "--root", str(self.source)).stderr)
        path.write_bytes(original)
        path.chmod(0o755)
        self.assertIn("changed: jimmy/skills/alpha/SKILL.md", self.cli("check", "--root", str(self.source)).stderr)
        path.chmod(0o644)
        extra = self.source / "jimmy/skills/extra/SKILL.md"
        write(extra, "Extra.\n")
        self.assertIn("extra: jimmy/skills/extra/SKILL.md", self.cli("check", "--root", str(self.source)).stderr)
        extra.unlink()
        path.unlink()
        self.assertIn("missing: jimmy/skills/alpha/SKILL.md", self.cli("check", "--root", str(self.source)).stderr)

    def test_rejects_malformed_digests_and_symlink_ancestors(self) -> None:
        lock_path = self.source / upstream.LOCK_FILE
        original = lock_path.read_bytes()
        for digest in ("a" * 40, 123, "g" * 64):
            with self.subTest(digest=digest):
                lock = json.loads(original)
                lock["files"]["jimmy/README.md"]["sha256"] = digest
                lock_path.write_text(json.dumps(lock))
                self.assertIn("invalid upstream.lock.json digest", self.cli("check", "--root", str(self.source)).stderr)
        lock_path.write_bytes(original)
        for relative in ("jimmy", ".cursor-plugin"):
            with self.subTest(relative=relative):
                path = self.source / relative
                actual = self.source / f"{relative}.real"
                path.rename(actual)
                path.symlink_to(actual, target_is_directory=True)
                self.assertIn("managed source parent is not a directory", self.cli("check", "--root", str(self.source)).stderr)
                path.unlink()
                actual.rename(path)

    def test_preview_reports_diff_preserves_binary_and_requires_review(self) -> None:
        write(self.repo / "pstack/.cursor-plugin/plugin.json", '{"version":"1.1.0"}\n')
        write(self.repo / "pstack/skills/alpha/SKILL.md", "---\nname: alpha\ndescription: Alpha.\n---\n\nSecond.\n", mode=0o755)
        (self.repo / "pstack/skills/remove/SKILL.md").unlink()
        write(self.repo / "pstack/skills/new/SKILL.md", "---\nname: new\ndescription: New.\n---\n")
        write(self.repo / "pstack/skills/new/assets/image.bin", b"\x00\xff\x81\x00")
        write(self.repo / "pstack/agents/helper.md", "Helper two.\n")
        newest = self.commit("update source")
        preview = self.base / "preview"
        result = self.update(newest, preview)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Changed (3)", result.stdout)
        self.assertIn("Added (2)", result.stdout)
        self.assertIn("Deleted (1)", result.stdout)
        self.assertIn("Semantic adapter review required (4)", result.stdout)
        self.assertEqual((preview / "jimmy/skills/new/assets/image.bin").read_bytes(), b"\x00\xff\x81\x00")
        self.assertEqual((preview / "jimmy/skills/alpha/SKILL.md").stat().st_mode & 0o777, 0o755)
        self.assertEqual((preview / "adapters/marker.txt").read_text(), "original adapter\n")
        self.assertEqual((preview / "dist/adapter.txt").read_text(), "original adapter\n")
        self.assertTrue((self.source / "jimmy/skills/remove/SKILL.md").exists())
        self.assertFalse((self.source / "jimmy/skills/new/SKILL.md").exists())
        lock = upstream.verify_source(preview)
        self.assertEqual(lock["commit"], git(self.repo, "rev-parse", "HEAD"))
        self.assertEqual(lock["version"], "1.1.0")
        self.assertEqual(lock["files"]["jimmy/skills/new/assets/image.bin"]["sha256"], "0793882e83d92ae7031e960921adda7851462c2bc1ac715186f225cb7c740637")

    def test_unchanged_preview_and_output_collision(self) -> None:
        preview = self.base / "preview"
        result = self.update(self.initial, preview)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Changed (0)", result.stdout)
        self.assertIn("Added (0)", result.stdout)
        self.assertIn("Deleted (0)", result.stdout)
        self.assertEqual(upstream.verify_source(preview)["commit"], self.initial)
        write(preview / "keep.txt", "keep\n")
        collision = self.update(self.initial, preview)
        self.assertEqual(collision.returncode, 1)
        self.assertEqual((preview / "keep.txt").read_text(), "keep\n")

    def test_local_drift_build_failure_and_unsafe_ref_leave_no_preview(self) -> None:
        preview = self.base / "preview"
        path = self.source / "jimmy/README.md"
        path.write_text("local change\n")
        result = self.update(self.initial, preview)
        self.assertEqual(result.returncode, 1)
        self.assertIn("source differs from upstream pin", result.stderr)
        self.assertFalse(preview.exists())
        path.write_text("Readme.\n")
        write(self.source / "adapters/fail", "fail\n")
        result = self.update(self.initial, preview)
        self.assertEqual(result.returncode, 1)
        self.assertIn("staged build failed (7)", result.stderr)
        self.assertFalse(preview.exists())
        (self.source / "adapters/fail").unlink()
        result = self.cli("update", "--root", str(self.source), "--ref=--upload-pack=sh", "--output", str(preview), "--repository", str(self.repo))
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsafe ref", result.stderr)
        self.assertFalse(preview.exists())

    def test_rejects_upstream_symlink_gitlink_and_unsafe_name(self) -> None:
        preview = self.base / "preview"
        (self.repo / "pstack/skills/leak").symlink_to("/tmp/secret")
        symlink_commit = self.commit("symlink")
        result = self.update(symlink_commit, preview)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported upstream entry", result.stderr)
        self.assertFalse(preview.exists())
        (self.repo / "pstack/skills/leak").unlink()
        git(self.repo, "rm", "--cached", "pstack/skills/leak")
        git(self.repo, "update-index", "--add", "--cacheinfo", f"160000,{self.initial},pstack/skills/submodule")
        git(self.repo, "commit", "--quiet", "-m", "gitlink")
        gitlink_commit = git(self.repo, "rev-parse", "HEAD")
        result = self.update(gitlink_commit, preview)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported upstream entry", result.stderr)
        self.assertFalse(preview.exists())
        git(self.repo, "rm", "--cached", "pstack/skills/submodule")
        write(self.repo / "pstack/skills/bad\\name.md", "bad\n")
        unsafe_commit = self.commit("unsafe name")
        result = self.update(unsafe_commit, preview)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsafe path", result.stderr)
        self.assertFalse(preview.exists())

    def test_excluded_root_entries_do_not_block_managed_update(self) -> None:
        (self.repo / "pstack/root-link").symlink_to("README.md")
        write(self.repo / "pstack/odd\\name", "outside scope\n")
        self.commit("excluded symlink and odd name")
        git(self.repo, "update-index", "--add", "--cacheinfo", f"160000,{self.initial},pstack/unrelated-submodule")
        git(self.repo, "commit", "--quiet", "-m", "excluded gitlink")
        commit = git(self.repo, "rev-parse", "HEAD")
        preview = self.base / "preview"
        result = self.update(commit, preview)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(upstream.verify_source(preview)["commit"], commit)
        self.assertFalse((preview / "jimmy/root-link").exists())
        self.assertFalse((preview / "jimmy/unrelated-submodule").exists())

    def test_report_flags_shadowed_upstream_changes(self) -> None:
        write(self.source / "adapters/common/skills/alpha/SKILL.md", "Override.\n")
        write(self.source / "adapters/claude/skills/remove/SKILL.md", "Override.\n")
        write(self.repo / "pstack/skills/alpha/SKILL.md", "---\nname: alpha\ndescription: Alpha.\n---\n\nSecond.\n")
        (self.repo / "pstack/skills/remove/SKILL.md").unlink()
        newest = self.commit("updated shadowed source")
        preview = self.base / "preview"
        result = self.update(newest, preview)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Adapter override review required (2)", result.stdout)
        self.assertIn("jimmy/skills/alpha/SKILL.md -> adapters/common/skills/alpha/SKILL.md", result.stdout)
        self.assertIn("jimmy/skills/remove/SKILL.md -> adapters/claude/skills/remove/SKILL.md", result.stdout)
        self.assertIn("No automatic semantic merge", result.stdout)

    def test_interrupted_accept_restores_originals(self) -> None:
        stage = self.base / "stage"
        shutil.copytree(self.source, stage)
        initial_manifest = (self.source / ".cursor-plugin/plugin.json").read_bytes()
        original_rename = Path.rename
        interrupted = False

        def rename_once(path: Path, target: Path) -> Path:
            nonlocal interrupted
            if path == stage / "jimmy/skills" and not interrupted:
                interrupted = True
                raise KeyboardInterrupt()
            return original_rename(path, target)

        with mock.patch.object(Path, "rename", rename_once):
            with self.assertRaises(KeyboardInterrupt):
                upstream._adopt(self.source, stage)
        self.assertEqual((self.source / ".cursor-plugin/plugin.json").read_bytes(), initial_manifest)
        self.assertEqual(upstream.verify_source(self.source)["commit"], self.initial)
        self.assertFalse(upstream._backup_path(self.source).exists())

    def test_recovers_interrupted_adoption_on_next_accept(self) -> None:
        preview = self.base / "preview"
        self.assertEqual(self.update(self.initial, preview).returncode, 0)
        backup = upstream._backup_path(self.source)
        backup.mkdir()
        write(backup / "journal.json", json.dumps({".cursor-plugin/plugin.json": True, "dist": False}))
        original_manifest = (self.source / ".cursor-plugin/plugin.json").read_bytes()
        (backup / ".cursor-plugin").mkdir()
        (self.source / ".cursor-plugin/plugin.json").rename(backup / ".cursor-plugin/plugin.json")
        write(self.source / ".cursor-plugin/plugin.json", '{"version":"corrupt"}\n')
        write(self.source / "dist/new.txt", "partial\n")
        accepted = self.cli("accept", "--root", str(self.source), "--preview", str(preview))
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertEqual((self.source / ".cursor-plugin/plugin.json").read_bytes(), original_manifest)
        self.assertFalse((self.source / "dist/new.txt").exists())
        self.assertFalse(backup.exists())

    def test_accept_uses_current_adapters_and_checks_preview_base(self) -> None:
        write(self.repo / "pstack/skills/alpha/SKILL.md", "---\nname: alpha\ndescription: Alpha.\n---\n\nSecond.\n")
        newest = self.commit("updated alpha")
        preview = self.base / "preview"
        result = self.update(newest, preview)
        self.assertEqual(result.returncode, 0, result.stderr)
        write(self.source / "adapters/marker.txt", "current adapter\n")
        accepted = self.cli("accept", "--root", str(self.source), "--preview", str(preview))
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertEqual((self.source / "adapters/marker.txt").read_text(), "current adapter\n")
        self.assertEqual((self.source / "dist/adapter.txt").read_text(), "current adapter\n")
        self.assertEqual(upstream.verify_source(self.source)["commit"], newest)
        repeated = self.cli("accept", "--root", str(self.source), "--preview", str(preview))
        self.assertEqual(repeated.returncode, 1)
        self.assertIn("different source pin", repeated.stderr)

    def test_accept_rejects_changed_pin_and_failed_build_without_mutating_source(self) -> None:
        preview = self.base / "preview"
        self.assertEqual(self.update(self.initial, preview).returncode, 0)
        lock_path = self.source / upstream.LOCK_FILE
        lock = json.loads(lock_path.read_text())
        lock["commit"] = "f" * 40
        lock_path.write_text(json.dumps(lock))
        self.assertEqual(upstream.verify_source(self.source)["commit"], "f" * 40)
        result = self.cli("accept", "--root", str(self.source), "--preview", str(preview))
        self.assertEqual(result.returncode, 1)
        self.assertIn("different source pin", result.stderr)
        self.write_lock(self.initial)
        write(self.source / "adapters/fail", "fail\n")
        result = self.cli("accept", "--root", str(self.source), "--preview", str(preview))
        self.assertEqual(result.returncode, 1)
        self.assertIn("staged build failed (7)", result.stderr)
        self.assertEqual(upstream.verify_source(self.source)["commit"], self.initial)
        self.assertFalse((self.source / "dist").exists())

    def test_missing_builder_blocks_preview_and_accept(self) -> None:
        builder = self.source / "scripts/build.py"
        preview = self.base / "preview"
        builder.unlink()
        result = self.update(self.initial, preview)
        self.assertEqual(result.returncode, 1)
        self.assertIn("staged build.py is missing", result.stderr)
        self.assertFalse(preview.exists())
        write(builder, "from pathlib import Path\nPath('dist').mkdir()\n")
        self.assertEqual(self.update(self.initial, preview).returncode, 0)
        builder.unlink()
        result = self.cli("accept", "--root", str(self.source), "--preview", str(preview))
        self.assertEqual(result.returncode, 1)
        self.assertIn("staged build.py is missing", result.stderr)
        self.assertEqual(upstream.verify_source(self.source)["commit"], self.initial)


if __name__ == "__main__":
    unittest.main()
