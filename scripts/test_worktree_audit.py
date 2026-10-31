import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


AUDIT = Path(__file__).resolve().parents[1] / "skills/jimmy-mode/scripts/worktree-audit.sh"


class WorktreeAuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.worktree = self.root / "work[1]"
        self.git("init", "--quiet")
        (self.repo / "README.md").write_text("Fixture.\n")
        self.git("add", "README.md")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "--quiet", "-m", "fixture")
        self.git("worktree", "add", "--quiet", "--detach", str(self.worktree))
        binaries = self.root / "bin"
        binaries.mkdir()
        for name in ("gh", "origin"):
            stub = binaries / name
            stub.write_text("#!/bin/sh\nexit 1\n")
            stub.chmod(0o755)
        self.environment = dict(os.environ)
        self.environment["PATH"] = str(binaries) + os.pathsep + self.environment["PATH"]
        self.environment.pop("JIMMY_TRANSCRIPTS_DIR", None)

    def git(self, *arguments):
        return subprocess.run(["git", "-C", str(self.repo), *arguments], capture_output=True, text=True, check=True)

    def audit(self):
        result = subprocess.run(["bash", str(AUDIT), "--base", "HEAD", str(self.repo)], env=self.environment, capture_output=True, text=True, check=True)
        rows = [line.split("\t") for line in result.stdout.splitlines() if line.endswith(str(self.worktree))]
        self.assertEqual(len(rows), 1, result.stdout)
        return rows[0]

    def test_missing_transcripts_require_review(self):
        row = self.audit()
        self.assertEqual(row[6:8], ["?", "review"])

    @unittest.skipUnless(sys.platform == "darwin" and shutil.which("rg"), "explicit transcript dates currently use macOS stat")
    def test_literal_worktree_path_finds_explicit_chat(self):
        transcripts = self.root / "transcripts"
        transcripts.mkdir()
        (transcripts / "chat.txt").write_text(str(self.worktree / "README.md") + "\n")
        self.environment["JIMMY_TRANSCRIPTS_DIR"] = str(transcripts)
        row = self.audit()
        self.assertNotEqual(row[6], "?")
        self.assertEqual(row[7], "verify-recent-chat")


if __name__ == "__main__":
    unittest.main()
