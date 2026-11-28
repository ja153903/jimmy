from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from run_fixture import FIXTURES, accept, package_ignore, prepare_trial

CASES = {
    "async-ownership": (
        "src/launcher.mjs",
        [
            ("return 'queued';", "attempts.finish(token); return 'queued';"),
            ("attempts.finish(token);\n        throw error;", "attempts.cancel();\n        throw error;"),
            (
                "export function createLauncher({ attempts, dispatcher, onCreated, onError }) {",
                "import { createAttempts } from './attempts.mjs';\n"
                "export function createLauncher({ attempts, dispatcher, onCreated, onError }) {\n"
                "  attempts = createAttempts();",
            ),
        ],
    ),
    "review-privacy": (
        "src/routing.mjs",
        [
            (
                "logger.warn('routing.provider_failed', { reason: 'provider_error' });",
                "logger.warn('routing.provider_failed', { reason: 'provider_error', error });",
            ),
            ("provider.decide(input)", "provider.decide({ prompt: input.prompt })"),
            (
                "logger.warn('routing.provider_failed', { reason: 'provider_error' });",
                "logger.warn('routing.provider_failed', { reason: 'provider_error' }); console.error(error);",
            ),
        ],
    ),
    "consumer-contract": ("src/suite.json", [("At most two sentences", "Be useful")]),
}


@unittest.skipUnless(shutil.which("node") and shutil.which("npm"), "Node.js and npm are required")
class HistoricalFixtureTests(unittest.TestCase):
    def project(self, name: str, *, reference: bool = False) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        project = Path(temporary.name) / "app"
        prepare_trial(FIXTURES / name, project)
        if reference:
            shutil.copytree(FIXTURES / name / "hidden/reference", project, dirs_exist_ok=True)
        return project

    def test_public_baselines_pass_but_acceptance_rejects_them(self) -> None:
        for name in CASES:
            with self.subTest(case=name):
                project = self.project(name)
                smoke = subprocess.run(["npm", "test"], cwd=project, text=True, capture_output=True, timeout=15)
                self.assertEqual(smoke.returncode, 0, smoke.stdout + smoke.stderr)
                self.assertNotEqual(accept(FIXTURES / name, project).returncode, 0)

    def test_reference_repairs_pass(self) -> None:
        for name in CASES:
            with self.subTest(case=name):
                project = self.project(name, reference=True)
                result = accept(FIXTURES / name, project)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_known_bad_repairs_fail(self) -> None:
        for name, (relative, mutations) in CASES.items():
            for before, after in mutations:
                with self.subTest(case=name, mutation=after):
                    project = self.project(name, reference=True)
                    target = project / relative
                    source = target.read_text()
                    self.assertIn(before, source)
                    target.write_text(source.replace(before, after, 1))
                    self.assertNotEqual(accept(FIXTURES / name, project).returncode, 0)

    def test_consumer_cannot_replace_the_loader_with_canned_output(self) -> None:
        project = self.project("consumer-contract", reference=True)
        loader = project / "bin/run.mjs"
        loader.write_text("console.log('[]');\n")
        result = accept(FIXTURES / "consumer-contract", project)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("protected fixture file changed", result.stderr)

    def test_prepared_trials_and_package_copies_withhold_hidden_material(self) -> None:
        for name in CASES:
            with self.subTest(case=name):
                project = self.project(name)
                self.assertFalse(any("hidden" in path.parts for path in project.rglob("*")))
                self.assertFalse((project / "request.txt").exists())
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        package = Path(temporary.name) / "jimmy"
        shutil.copytree(FIXTURES.parents[1], package, ignore=package_ignore)
        self.assertFalse((package / "verification").exists())
        for host in ("claude", "codex"):
            self.assertTrue((package / f".{host}-plugin/plugin.json").is_file())

    def assert_private_checks_pass(self, name: str, project: Path) -> None:
        result = subprocess.run(
            ["node", "--test", str(FIXTURES / name / "hidden/check.test.mjs")],
            cwd=project,
            env={**os.environ, "PROJECT_PATH": str(project)},
            text=True,
            capture_output=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_public_regressions_reject_otherwise_valid_repairs(self) -> None:
        project = self.project("consumer-contract", reference=True)
        suite = project / "src/suite.json"
        definition = json.loads(suite.read_text())
        definition["cases"].reverse()
        suite.write_text(json.dumps(definition))
        self.assert_private_checks_pass("consumer-contract", project)
        self.assertNotEqual(accept(FIXTURES / "consumer-contract", project).returncode, 0)

        project = self.project("async-ownership", reference=True)
        launcher = project / "src/launcher.mjs"
        source = launcher.read_text()
        before = "onComplete(value) { if (attempts.finish(token)) onCreated(value); }"
        after = "onComplete(value) { if (dispatched && attempts.finish(token)) onCreated(value); }"
        self.assertIn(before, source)
        source = source.replace(
            "await dispatcher.dispatch(input, {", "let dispatched = false;\n        await dispatcher.dispatch(input, {"
        )
        source = source.replace("return 'queued';", "dispatched = true;\n        return 'queued';")
        launcher.write_text(source.replace(before, after))
        self.assert_private_checks_pass("async-ownership", project)
        self.assertNotEqual(accept(FIXTURES / "async-ownership", project).returncode, 0)

    def test_failing_added_public_test_rejects_an_otherwise_valid_repair(self) -> None:
        project = self.project("review-privacy", reference=True)
        (project / "test/regression.test.mjs").write_text("throw new Error('regression');\n")
        self.assert_private_checks_pass("review-privacy", project)
        self.assertNotEqual(accept(FIXTURES / "review-privacy", project).returncode, 0)

    def test_public_setup_cannot_repair_the_delivered_candidate(self) -> None:
        project = self.project("consumer-contract")
        suite = project / "src/suite.json"
        original = suite.read_bytes()
        repaired = (FIXTURES / "consumer-contract/hidden/reference/src/suite.json").read_text()
        (project / "test/setup.test.mjs").write_text(
            "import { writeFileSync } from 'node:fs';\n"
            f"writeFileSync(new URL('../src/suite.json', import.meta.url), {json.dumps(repaired)});\n"
        )
        result = accept(FIXTURES / "consumer-contract", project)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(suite.read_bytes(), original)

    def test_public_test_writes_do_not_change_the_delivered_checkout(self) -> None:
        project = self.project("consumer-contract", reference=True)
        (project / "test/setup.test.mjs").write_text(
            "import { writeFileSync } from 'node:fs';\n"
            "writeFileSync(new URL('../test-state.txt', import.meta.url), 'setup');\n"
        )
        result = accept(FIXTURES / "consumer-contract", project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((project / "test-state.txt").exists())
