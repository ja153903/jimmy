#!/usr/bin/env python3
"""Run one workflow fixture trial against any agent host and grade what it leaves behind.

The host is a command template, so any provider's CLI works. Placeholders: {prompt} (request.txt),
{trial} (the project checkout, also the working directory), {package} (a copy of the Jimmy package
without fixture answers). Grading uses artifacts only: acceptance output, changed files, and the
evidence records the workflow left in <trial>/.git/jimmy/ (see skills/jimmy/scripts/evidence.py), and
raw host output for the remaining tool-record rubric rows.
"""

from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/jimmy/scripts"))
import evidence  # noqa: E402

FIXTURES = ROOT / "verification/workflow"
IGNORE_ANYWHERE = {".git", ".venv", ".ruff_cache", ".pytest_cache", "__pycache__"}
IGNORE_AT_ROOT = {"verification", "scripts"}
RERUN_TIMEOUT_S = 300
LEAK_MARKERS = ("acceptance.mjs", "rubric.md", "/hidden/")
GIT_IDENTITY = ["-c", "user.name=dev", "-c", "user.email=dev@example.invalid"]

HOSTS = {
    "claude": "claude -p --output-format stream-json --verbose --permission-mode bypassPermissions"
    " --plugin-dir {package} {prompt}",
    # ponytail: Codex uses the Jimmy it has installed; point it at {package} once Codex takes a plugin flag.
    "codex": "codex exec --json --sandbox workspace-write --skip-git-repo-check -C {trial} {prompt}",
}


def host_argv(template: str, values: dict[str, str]) -> list[str]:
    """Split the template first so a substituted prompt stays one argument."""
    return [token.format_map(values) for token in shlex.split(template)]


def parse_name_status(output: str) -> list[str]:
    return [" ".join(line.split("\t")) for line in output.splitlines() if line]


def leak_suspected(host_output: str) -> bool:
    return any(marker in host_output for marker in LEAK_MARKERS)


def package_ignore(directory: str, names: list[str]) -> set[str]:
    skip = IGNORE_ANYWHERE | (IGNORE_AT_ROOT if Path(directory) == ROOT else set())
    return {name for name in names if name in skip}


def grade_records(
    records: list[dict], base_tree: str, final_tree: str, reruns: list[int], review_check: evidence.ReviewCheck
) -> dict[str, object]:
    """Use the same coverage verdict as the delivery gate."""
    contracts = [r for r in records if r.get("kind") == "contract" and r["tree"] == base_tree]
    passing = [r for r in evidence.for_tree(records, "receipt", final_tree) if r["exit_code"] == 0]
    review = (
        "not-required"
        if not review_check.required
        else "covered"
        if review_check.ok
        else "reported-missing"
        if evidence.latest(records, "review_missing")
        else "missing"
    )
    return {
        "contract_before_edit": bool(contracts),
        "contract_paired_before_edit": any(c["keep"] and c["reject"] for c in contracts),
        "receipt_passes_final": bool(passing),
        "receipts_reproduced": bool(passing) and all(code == 0 for code in reruns),
        "review": review,
        "review_source": review_check.source,
    }


def grade(acceptance: subprocess.CompletedProcess[str], changed: list[str], host_output: str) -> dict[str, object]:
    return {
        "acceptance_passed": acceptance.returncode == 0,
        "acceptance_output": acceptance.stdout + acceptance.stderr,
        "changed_files": changed,
        "leak_suspected": leak_suspected(host_output),
    }


def git(trial: Path, *args: str) -> str:
    return subprocess.run(["git", *GIT_IDENTITY, *args], cwd=trial, check=True, text=True, capture_output=True).stdout


def prepare_trial(fixture: Path, trial: Path) -> str:
    """Returns the initial commit; hosts may commit on top of it."""
    shutil.copytree(fixture / "given", trial)
    git(trial, "init", "-q")
    git(trial, "add", "-A")
    git(trial, "commit", "-qm", "initial")
    return git(trial, "rev-parse", "HEAD").strip()


def rerun_passing(records: list[dict], final_tree: str, trial: Path) -> list[int]:
    """Receipts are claims: rerun each passing one at the delivered tree."""
    passing = [r for r in evidence.for_tree(records, "receipt", final_tree) if r["exit_code"] == 0]
    return [evidence.run_captured(r["cmd"], trial / r["cwd"], timeout=RERUN_TIMEOUT_S)[0] for r in passing]


def run_host(argv: list[str], trial: Path, out: Path, timeout: int) -> dict[str, object]:
    started = time.monotonic()
    with (out / "host-stdout.log").open("w") as stdout, (out / "host-stderr.log").open("w") as stderr:
        try:
            code: int | None = subprocess.run(argv, cwd=trial, stdout=stdout, stderr=stderr, timeout=timeout).returncode
        except subprocess.TimeoutExpired:
            code = None
    return {"argv": argv, "exit_code": code, "timed_out": code is None, "elapsed_s": round(time.monotonic() - started)}


def collect_changes(trial: Path, out: Path, initial: str) -> list[str]:
    git(trial, "add", "-A")
    (out / "diff.patch").write_text(git(trial, "diff", "--cached", initial))
    return parse_name_status(git(trial, "diff", "--cached", "--name-status", initial))


def accept(fixture: Path, trial: Path) -> subprocess.CompletedProcess[str]:
    node = shutil.which("node") or "node"
    return subprocess.run([node, str(fixture / "hidden/acceptance.mjs"), str(trial)], text=True, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("fixture", choices=sorted(p.name for p in FIXTURES.iterdir() if (p / "given").is_dir()))
    host = parser.add_mutually_exclusive_group(required=True)
    host.add_argument("--host", choices=sorted(HOSTS), help="built-in host template")
    host.add_argument("--cmd", help="custom host template, e.g. 'opencode run {prompt}'")
    parser.add_argument("--out", type=Path, help="results directory (default: new temp dir)")
    parser.add_argument("--timeout", type=int, default=1800, help="host timeout in seconds")
    args = parser.parse_args()

    fixture = FIXTURES / args.fixture
    out = (args.out or Path(tempfile.mkdtemp(prefix="work-"))).resolve()
    out.mkdir(parents=True, exist_ok=True)
    trial, package = out / "app", out / "jimmy"
    initial = prepare_trial(fixture, trial)
    base_tree = evidence.tree_of(trial, initial)
    shutil.copytree(ROOT, package, ignore=package_ignore)

    values = {"prompt": (fixture / "request.txt").read_text().strip(), "trial": str(trial), "package": str(package)}
    run = run_host(host_argv(args.cmd or HOSTS[args.host], values), trial, out, args.timeout)
    host_output = (out / "host-stdout.log").read_text() + (out / "host-stderr.log").read_text()
    final_tree = evidence.working_tree(trial)
    records_path = evidence.records_file(trial)
    records = [r for r in evidence.read_records(records_path) if r.get("kind") != "contract"]
    records.extend(evidence.contracts_for_worktree(trial))
    if records_path.exists():
        shutil.copyfile(records_path, out / "records.jsonl")
    # Grade the delivered tree before rerunning receipts: a rerun may write to the checkout.
    changed = collect_changes(trial, out, initial)
    result = {"fixture": args.fixture, **run, **grade(accept(fixture, trial), changed, host_output)}
    review = evidence.review_check(trial, records, base_tree, final_tree)
    reruns = rerun_passing(records, final_tree, trial)
    artifacts = grade_records(records, base_tree, final_tree, reruns, review)
    result |= {"artifacts": artifacts, "manual_rubric": str(fixture / "hidden/rubric.md")}
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")

    print(result["acceptance_output"], end="")
    print(f"changed: {', '.join(changed) or 'nothing'}")
    print("\n".join(f"{row}: {value}" for row, value in artifacts.items()))
    if result["leak_suspected"]:
        print("WARNING: host output mentions hidden fixture material")
    print(f"results: {out}\nremaining tool-record rows: grade from host-stdout.log per {result['manual_rubric']}")
    return 0 if result["acceptance_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
