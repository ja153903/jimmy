from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import unittest

FIXTURES = Path(__file__).resolve().parents[1] / 'verification/workflow'
NODE = shutil.which('node')


@unittest.skipUnless(NODE, 'node is required for workflow fixture checkers')
class SessionIdentityFixtureTests(unittest.TestCase):
    root = FIXTURES / 'session-identity'

    def accept(self, candidate: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([NODE, str(self.root / 'hidden/acceptance.mjs'), str(candidate)], text=True, capture_output=True)

    def test_rejects_original_and_identity_removed(self) -> None:
        for candidate in (self.root / 'given', self.root / 'hidden/variants/identity-removed.js'):
            with self.subTest(candidate=candidate.name):
                result = self.accept(candidate)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn('REJECTED', result.stdout)

    def test_accepts_reference(self) -> None:
        result = self.accept(self.root / 'hidden/variants/reference.js')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_hidden_material_is_not_given(self) -> None:
        given = {p.name for p in (self.root / 'given').rglob('*')}
        self.assertFalse(given & {'acceptance.mjs', 'rubric.md', 'reference.js', 'identity-removed.js'})


if __name__ == '__main__':
    unittest.main()
