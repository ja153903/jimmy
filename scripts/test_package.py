from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_package import PackageError, check_package

REPOSITORY = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.package = Path(temporary.name)
        for host in ('codex', 'claude'):
            self.write(f'.{host}-plugin/plugin.json', json.dumps({
                'name': 'fixture', 'version': '1.0.0', 'description': 'Fixture skills.', 'skills': './skills/',
            }))
        self.write('skills/example/SKILL.md', '---\nname: example\ndescription: Example.\n---\n\n[Resource](value.txt).\n')
        self.write('skills/example/value.txt', 'Example resource.\n')

    def write(self, relative: str, content: str) -> None:
        path = self.package / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def test_validation_is_read_only(self) -> None:
        before = {p.relative_to(self.package): p.read_bytes() for p in self.package.rglob('*') if p.is_file()}
        self.assertEqual(check_package(self.package), 1)
        after = {p.relative_to(self.package): p.read_bytes() for p in self.package.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_both_manifests_must_use_same_directory_and_version(self) -> None:
        path = self.package / '.codex-plugin/plugin.json'
        original = json.loads(path.read_text())
        for field, value in [('skills', './different-skills/'), ('version', '2.0.0')]:
            with self.subTest(field=field):
                path.write_text(json.dumps({**original, field: value}))
                with self.assertRaises(PackageError):
                    check_package(self.package)

    def test_explicit_only_policy_must_cover_both_hosts(self) -> None:
        path = self.package / 'skills/example/SKILL.md'
        path.write_text(path.read_text().replace('description: Example.', 'description: Example.\ndisable-model-invocation: true'))
        with self.assertRaisesRegex(PackageError, 'matching invocation policy'):
            check_package(self.package)
        self.write('skills/example/agents/openai.yaml', 'policy:\n  allow_implicit_invocation: false\n')
        self.assertEqual(check_package(self.package), 1)

    def test_missing_links_and_package_escapes_are_rejected(self) -> None:
        for link in ('missing.md', '../../../outside.md'):
            with self.subTest(link=link):
                self.write('skills/example/SKILL.md', f'---\nname: example\ndescription: Example.\n---\n\n[Link]({link}).\n')
                with self.assertRaisesRegex(PackageError, 'broken local Markdown links'):
                    check_package(self.package)

    def test_symlink_resources_are_rejected(self) -> None:
        (self.package / 'skills/example/link.txt').symlink_to('value.txt')
        with self.assertRaisesRegex(PackageError, 'symlink'):
            check_package(self.package)

    def test_repository_marketplaces_install_the_same_valid_package(self) -> None:
        claude = json.loads((REPOSITORY / '.claude-plugin/marketplace.json').read_text())
        codex = json.loads((REPOSITORY / '.agents/plugins/marketplace.json').read_text())
        claude_path = (REPOSITORY / claude['plugins'][0]['source']).resolve()
        codex_path = (REPOSITORY / codex['plugins'][0]['source']['path']).resolve()
        self.assertEqual(claude_path, codex_path)
        self.assertGreater(check_package(claude_path), 0)
        self.assertEqual(claude_path, REPOSITORY)
        self.assertFalse((REPOSITORY / 'plugins').exists())
        self.assertFalse((REPOSITORY / 'jimmy').exists())

    def test_bundled_executable_runs_from_its_moved_location(self) -> None:
        script = REPOSITORY / 'skills/jimmy-mode/scripts/worktree-audit.sh'
        result = subprocess.run(['bash', str(script), '--help'], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Usage:', result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
