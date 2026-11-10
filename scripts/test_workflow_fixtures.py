from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "verification/workflow"
NODE = shutil.which("node") or ""


@unittest.skipUnless(NODE, "node is required for workflow fixture checkers")
class SessionIdentityFixtureTests(unittest.TestCase):
    root = FIXTURES / "session-identity"

    def accept(self, candidate: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [NODE, str(self.root / "hidden/acceptance.mjs"), str(candidate)], text=True, capture_output=True
        )

    def test_rejects_original_and_identity_removed(self) -> None:
        for candidate in (self.root / "given", self.root / "hidden/variants/identity-removed.js"):
            with self.subTest(candidate=candidate.name):
                result = self.accept(candidate)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("REJECTED", result.stdout)

    def test_accepts_reference(self) -> None:
        result = self.accept(self.root / "hidden/variants/reference.js")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_hidden_material_is_not_given(self) -> None:
        given = {p.name for p in (self.root / "given").rglob("*")}
        self.assertFalse(given & {"acceptance.mjs", "rubric.md", "reference.js", "identity-removed.js"})


@unittest.skipUnless(NODE, "node is required for workflow fixture checkers")
class ExistingAppFixtureTests(unittest.TestCase):
    root = FIXTURES / "existing-app"

    def accept(self, candidate: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [NODE, str(self.root / "hidden/acceptance.mjs"), str(candidate)], text=True, capture_output=True
        )

    def trial(self, with_skill: bool) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        trial = Path(temporary.name)
        shutil.copy(self.root / "hidden/variants/reference.js", trial / "notebook.js")
        if with_skill:
            skill = trial / ".claude/skills/verify-notebook"
            (skill / "features").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: verify-notebook\ndescription: Drive the notebook CLI.\n---\n\nBody.\n"
            )
            (skill / "features/README.md").write_text("# Features\n")
            (skill / "features/list.md").write_text("Run `notebook list`.\n")
        return trial

    def test_rejects_original_and_known_bad_variants(self) -> None:
        for candidate in ("given/notebook.js", "hidden/variants/reversed.js", "hidden/variants/mutating.js"):
            with self.subTest(candidate=candidate):
                result = self.accept(self.root / candidate)
                self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_accepts_reference_code(self) -> None:
        result = self.accept(self.root / "hidden/variants/reference.js")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_trial_requires_verification_skill(self) -> None:
        self.assertNotEqual(self.accept(self.trial(with_skill=False)).returncode, 0)
        result = self.accept(self.trial(with_skill=True))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
