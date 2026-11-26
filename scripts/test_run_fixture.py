from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from run_fixture import FIXTURES, host_argv

SCRIPT = Path(__file__).resolve().parent / "run_fixture.py"
REFERENCE = FIXTURES / "session-identity/hidden/variants/reference.js"
EVIDENCE = FIXTURES.parents[1] / "skills/jimmy/scripts/evidence.py"
ENV = {k: v for k, v in os.environ.items() if k != "JIMMY_REVIEWER"}


def artifacts(result: dict[str, object]) -> dict[str, object]:
    rows = result["artifacts"]
    assert isinstance(rows, dict)
    return rows


@unittest.skipUnless(shutil.which("node"), "node is required for workflow fixture checkers")
class RunFixtureTests(unittest.TestCase):
    def trial(self, cmd: str) -> tuple[subprocess.CompletedProcess[str], dict[str, object], Path]:
        out = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, out)
        run = subprocess.run(
            [sys.executable, str(SCRIPT), "session-identity", "--cmd", cmd, "--out", str(out)],
            env=ENV,
            text=True,
            capture_output=True,
        )
        return run, json.loads((out / "result.json").read_text()), out

    def test_stub_host_applying_reference_passes(self) -> None:
        run, result, _ = self.trial(f"cp {REFERENCE} retry.js")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertTrue(result["acceptance_passed"])
        self.assertEqual(result["changed_files"], ["M retry.js"])
        self.assertFalse(result["leak_suspected"])

    def test_stub_host_doing_nothing_fails(self) -> None:
        run, result, _ = self.trial("true")
        self.assertEqual(run.returncode, 1)
        self.assertFalse(result["acceptance_passed"])
        self.assertEqual(result["changed_files"], [])

    def test_hidden_material_never_reaches_trial_or_package(self) -> None:
        _, _, out = self.trial("true")
        exposed = [p for p in out.rglob("*") if "hidden" in p.parts or p.name in {"acceptance.mjs", "rubric.md"}]
        self.assertEqual(exposed, [])
        self.assertTrue((out / "jimmy/skills/jimmy/SKILL.md").is_file())
        self.assertTrue((out / "jimmy/skills/jimmy/scripts/evidence.py").is_file())
        self.assertTrue((out / "jimmy/skills/show-me-your-work/scripts/log.sh").is_file())

    def test_evidence_rows_graded_from_records(self) -> None:
        cli = f"{shlex.quote(sys.executable)} {shlex.quote(str(EVIDENCE))}"
        script = (
            f"{cli} contract --interpretation 'retry by operation' --keep 'session change' --reject 'skip'"
            f" && cp {REFERENCE} retry.js && {cli} receipt -- node -e 0 && {cli} review --request 'fix'; true"
        )
        _, result, out = self.trial(f"sh -c {shlex.quote(script)}")
        self.assertEqual(
            artifacts(result),
            {
                "contract_before_edit": True,
                "contract_paired_before_edit": True,
                "receipt_passes_final": True,
                "receipts_reproduced": True,
                "review": "reported-missing",
                "review_source": None,
            },
        )
        self.assertTrue((out / "records.jsonl").is_file())

    def test_linked_worktree_contract_is_not_credited_to_the_trial(self) -> None:
        script = (
            f"git worktree add --detach ../worker && cd ../worker && {shlex.quote(sys.executable)} "
            f"{shlex.quote(str(EVIDENCE))} contract --interpretation other --keep yes --reject no"
        )
        _, result, _ = self.trial(f"sh -c {shlex.quote(script)}")
        self.assertFalse(artifacts(result)["contract_before_edit"])
        self.assertFalse(artifacts(result)["contract_paired_before_edit"])

    def test_receipt_that_does_not_reproduce_is_caught(self) -> None:
        marker = Path(tempfile.mkdtemp()) / "ran"
        self.addCleanup(shutil.rmtree, marker.parent)
        flaky = f"test ! -e {marker} && touch {marker}"
        script = f"{shlex.quote(sys.executable)} {shlex.quote(str(EVIDENCE))} receipt -- sh -c {shlex.quote(flaky)}"
        _, result, _ = self.trial(f"sh -c {shlex.quote(script)}")
        self.assertTrue(artifacts(result)["receipt_passes_final"])
        self.assertFalse(artifacts(result)["receipts_reproduced"])

    def test_no_evidence_grades_every_row_false(self) -> None:
        _, result, _ = self.trial("true")
        self.assertEqual(set(artifacts(result).values()), {False, "not-required", None})

    def test_failed_reviewer_is_not_graded_as_review(self) -> None:
        cli = f"{shlex.quote(sys.executable)} {shlex.quote(str(EVIDENCE))}"
        script = f"cp {REFERENCE} retry.js && {cli} review --request fix --cmd no-such-reviewer-cli; true"
        _, result, _ = self.trial(f"sh -c {shlex.quote(script)}")
        self.assertEqual(artifacts(result)["review"], "missing")

    def test_committed_work_is_graded_and_empty_diff_review_does_not_count(self) -> None:
        cli = f"{shlex.quote(sys.executable)} {shlex.quote(str(EVIDENCE))}"
        reviewer = shlex.quote("sh -c 'cat >/dev/null; echo VERDICT: PASS'")
        script = (
            f"cp {REFERENCE} retry.js && git add -A && git -c user.name=a -c user.email=a@a commit -qm fix"
            f" && {cli} review --request fix --cmd {reviewer}"
        )
        _, result, _ = self.trial(f"sh -c {shlex.quote(script)}")
        self.assertTrue(result["acceptance_passed"])
        self.assertEqual(result["changed_files"], ["M retry.js"])
        self.assertEqual(artifacts(result)["review"], "missing", "the reviewer was shown an empty diff")

    def test_acceptance_is_graded_before_receipts_rerun(self) -> None:
        marker = Path(tempfile.mkdtemp()) / "ran"
        self.addCleanup(shutil.rmtree, marker.parent)
        edit_on_rerun = f"if [ -e {marker} ]; then cp {REFERENCE} retry.js; else touch {marker}; fi"
        cli = f"{shlex.quote(sys.executable)} {shlex.quote(str(EVIDENCE))}"
        run, result, _ = self.trial(f"sh -c {shlex.quote(f'{cli} receipt -- sh -c {shlex.quote(edit_on_rerun)}')}")
        self.assertFalse(result["acceptance_passed"], run.stdout)
        self.assertEqual(result["changed_files"], [])

    def test_host_output_mentioning_hidden_paths_is_flagged(self) -> None:
        _, result, _ = self.trial("echo cat ../hidden/acceptance.mjs")
        self.assertTrue(result["leak_suspected"])

    def test_prompt_with_spaces_stays_one_argument(self) -> None:
        argv = host_argv("agent -p {prompt} --cd {trial}", {"prompt": "fix it now", "trial": "/t"})
        self.assertEqual(argv, ["agent", "-p", "fix it now", "--cd", "/t"])


if __name__ == "__main__":
    unittest.main()
