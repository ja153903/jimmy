#!/usr/bin/env python3
"""Record workflow evidence against the exact working tree. Works with any agent host or model.

Receipts and reviews append to <git common dir>/jimmy/records.jsonl. Contracts use the worktree's own Git directory.
Each carries `tree`: the git tree hash of the working tree, including unstaged edits and untracked
files that are not ignored.

  evidence.py receipt -- <cmd...>       run a check; record exit code and output hash
                                        (shell syntax: evidence.py receipt -- sh -c 'a && b')
  evidence.py contract --interpretation TEXT --keep CASE [--keep CASE] [--reject CASE]...
  evidence.py brief --request TEXT [--context TEXT]... [--base REV] > brief.md
                                        print and record the independent-review brief
  evidence.py review --request TEXT [--context TEXT]... [--base REV] [--cmd 'reviewer CLI reading stdin']
                                        run the reviewer in an isolated worktree of this tree;
                                        --cmd defaults to $JIMMY_REVIEWER; with neither, the
                                        missing review is recorded and the exit code is 2
  evidence.py review --findings FILE --by NAME --brief brief.md
                                        record a host-agent review of that exact brief
  evidence.py status                    summarize records for the current tree
  evidence.py gate [--base REV] [--no-rerun]
                                        fail unless HEAD has a passing receipt that reruns green
                                        and, when the diff trips a review trigger, a VERDICT: PASS
                                        review that saw it (--base: upstream merge-base)

In CI, create the records there (receipt your checks, review with a reviewer CLI) and then gate:
use a fresh checkout and a trusted gate for the tested commit.

Stdlib only; runs on Python 3.9+.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from itertools import groupby
from pathlib import Path

TAIL_CHARS = 2000
BRIEF_DIFF_CHARS = 200_000
GIT_IDENTITY = ("-c", "user.name=jimmy", "-c", "user.email=jimmy@localhost")
REVIEW_TIMEOUT_S = 1800
RERUN_TIMEOUT_S = 1800
VERDICTS = {"VERDICT: PASS": "PASS", "VERDICT: ISSUES": "ISSUES"}
# Plumbing-stable diff: attributes, textconv, external tools, and prefix config cannot hide changed lines.
DIFF = ("-c", "core.quotepath=off", "diff", "--no-ext-diff", "--no-textconv", "--text", "--no-color", "--no-renames",
        "--src-prefix=a/", "--dst-prefix=b/")  # fmt: skip
DOC_FILE = re.compile(r"\.(md|mdx|rst|txt|adoc)$", re.IGNORECASE)
TEST_FILE = re.compile(
    r"(^|/)(tests?|__tests__|specs?)/|(^|/)[^/]*\.Tests?/|[._-](test|spec)s?\.[^/]+$|(^|/)test_[^/]+$", re.IGNORECASE
)
TEST_FILE_CAMEL = re.compile(r"[a-z0-9]Tests?\.[^/]+$")
TEST_ASSERTION = re.compile(
    r"\bassert|\bAssert\.|\bexpect\s*\(|\.should\b|\bto(Be|Equal|Throw|Match|Have)|\braises\("
    r"|\bt\.(is|not|equal|deepEqual|true|false|ok|throws)\b|\bt\.(Fatal|Error|Fail)|\b(XCTAssert|EXPECT_|ASSERT_)"
    r"|\brequire\.\w+\("
)
TEST_SKIP = re.compile(
    r"\.(skip|only)\s*\(|\bx(it|describe|test)\s*\(|@skip|mark\.skip|\bt\.Skip|@Disabled|@Ignore|skipTest|unittest\.skip"
)
PATH_TRIGGERS = {"migrations": re.compile(r"(^|/)migrations?/|\.sql$", re.IGNORECASE)}
# ponytail: fixed keyword floor from docs/review.md, noisy by design; add a per-repo pattern file when it over-fires.
LINE_TRIGGERS = {
    topic: re.compile(pattern, re.IGNORECASE)
    for topic, pattern in {
        "retries": r"retr(y|ies|ied|ying)|backoff|idempoten",
        "identity": r"session|operation.?id|request.?id|idempotency.?key",
        "ownership": r"\bowner|\blease\b|\bclaim",
        "cancellation": r"cancel|abort",
        "permissions": r"permission|authori[sz]|\bauthz\b|\bacl\b|\broles?\b",
        "migrations": r"migrat|alter\s+table|create\s+table|drop\s+(table|column)",
        "shared mutable state": r"mutex|\block|semaphore|\batomic|\bglobal\b|\bvolatile\b",
    }.items()
}
REVIEW_INSTRUCTIONS = """\
You are an independent reviewer. You did not write this change. Your working directory is an
isolated checkout of the exact tree under review; run anything you need there.

Check the author's interpretation against the request as well as the implementation: a faithful
implementation of a wrong interpretation is a defect. Try to break the intended behavior with the
real code. Report each defect with its location, failure mechanism, the exact reproduction command,
observed output, and expected behavior. Style preferences and speculative future failures are not
defects. If nothing breaks, say "no verified findings" and state what you covered.

End with a final line that is exactly "VERDICT: PASS" (no verified findings) or "VERDICT: ISSUES".
"""


# --- pure -----------------------------------------------------------------------------------


def for_tree(records: list[dict], kind: str, tree: str) -> list[dict]:
    return [r for r in records if r.get("kind") == kind and r.get("tree") == tree]


def latest(records: list[dict], kind: str) -> dict | None:
    matches = [r for r in records if r.get("kind") == kind]
    return matches[-1] if matches else None


def format_contract(contract: dict | None) -> str:
    if contract is None:
        return "(no contract recorded)"
    keep = "\n".join(f"- must hold: {case}" for case in contract["keep"])
    reject = "\n".join(f"- must be rejected: {case}" for case in contract["reject"])
    return "\n".join(part for part in (contract["interpretation"], keep, reject) if part)


@dataclass
class FileChange:
    path: str
    versions: str  # Git's raw entry includes both full blob IDs and modes.
    patch: str
    triggers: list[str]


def compose_diff(changes: list[FileChange]) -> tuple[str, dict[str, str | None]]:
    remaining = BRIEF_DIFF_CHARS - sum(len(c.patch) for c in changes if c.triggers)
    shown = []
    omitted = []
    files: dict[str, str | None] = {}
    for change in changes:
        if change.triggers or len(change.patch) <= remaining:
            shown.append(change.patch)
            files[change.path] = change.versions
            if not change.triggers:
                remaining -= len(change.patch)
        else:
            omitted.append(change.path)
            files[change.path] = None
    body = "".join(shown) or "(empty diff)"
    if omitted:
        body += "\n(omitted to fit, no review triggers: " + ", ".join(omitted) + ")"
    return body, files


def build_brief(request: str, contract: dict | None, context: list[str], diff: str, base: str, tree: str) -> str:
    sections = [
        REVIEW_INSTRUCTIONS,
        f"## User request\n\n{request}",
        f"## Author's interpretation (behavioral contract)\n\n{format_contract(contract)}",
        *(f"## Context\n\n{item}" for item in context),
        f"## Diff under review\n\nBase tree {base}\nReviewed tree {tree}\n\n```diff\n{diff}\n```",
    ]
    return "\n\n".join(sections) + "\n"


def status_lines(records: list[dict], tree: str, contract: dict | None) -> list[str]:
    receipts = for_tree(records, "receipt", tree)
    reviews = for_tree(records, "review", tree)
    lines = [f"tree {tree}"]
    lines.append(f"contract: {'recorded at tree ' + contract['tree'] if contract else 'none'}")
    lines += [f"receipt: exit {r['exit_code']} {shlex.join(r['cmd'])}" for r in receipts] or ["receipt: none"]
    lines += [f"review: {r['source']} by {r['by']}, verdict {review_verdict(r)}" for r in reviews] or [
        "review: none for this tree"
    ]
    lines += [f"review missing: {r['reason']}" for r in for_tree(records, "review_missing", tree)]
    return lines


def verdict(output: str) -> str | None:
    """Only an exact final line counts, so echoed prompts and diff context are never verdicts."""
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return VERDICTS.get(lines[-1]) if lines else None


def review_verdict(review: dict) -> str | None:
    """ISSUES always counts; PASS from a reviewer command that exited non-zero does not."""
    found = verdict(review["output"])
    failed = review.get("source") == "command" and review.get("exit_code") != 0
    return None if failed and found == "PASS" else found


def is_test_file(path: str) -> bool:
    if "/src/main/" in "/" + path:  # Maven/Gradle production sources, whatever the file name
        return False
    if path.endswith(".swift") and any(part.endswith("Tests") for part in path.split("/")[:-1]):
        return True
    return bool(TEST_FILE.search(path) or TEST_FILE_CAMEL.search(path))


def classify(path: str, deleted: bool, patch: str) -> list[str]:
    """Review-trigger reasons from changed lines only."""
    if not is_test_file(path) and DOC_FILE.search(path):
        return []
    added, removed = [], []
    in_hunk = False
    for line in patch.split("\n"):
        if line.startswith("diff --git "):
            in_hunk = False
        elif line.startswith("@@"):
            in_hunk = True
        elif in_hunk and line.startswith("+"):
            added.append(line[1:])
        elif in_hunk and line.startswith("-"):
            removed.append(line[1:])

    reasons = []
    if is_test_file(path):
        if deleted:
            reasons.append(f"{path}: test file deleted")
        if any(TEST_ASSERTION.search(line) for line in removed):
            reasons.append(f"{path}: test assertion removed or changed")
        if any(TEST_SKIP.search(line) for line in added):
            reasons.append(f"{path}: test skipped or focused")
        return reasons
    lines = added + removed
    reasons += [f"{path}: {topic} path" for topic, pattern in PATH_TRIGGERS.items() if pattern.search(path)]
    reasons += [f"{path}: {topic}" for topic, pattern in LINE_TRIGGERS.items() if any(map(pattern.search, lines))]
    return reasons


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


# --- effects --------------------------------------------------------------------------------


def git(root: Path, *args: str, env: dict[str, str] | None = None, stdin: str | None = None) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, env=env, input=stdin, text=True, errors="replace", capture_output=True
    )
    if result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def git_ok(root: Path, *args: str) -> str | None:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else None


def repo_root(start: Path) -> Path:
    return Path(git(start, "rev-parse", "--show-toplevel"))


def records_file(root: Path) -> Path:
    common = Path(git(root, "rev-parse", "--git-common-dir"))
    return (common if common.is_absolute() else root / common) / "jimmy" / "records.jsonl"


def contract_file(root: Path) -> Path:
    # Git removes this administrative directory when it removes a linked worktree.
    return Path(git(root, "rev-parse", "--absolute-git-dir")) / "jimmy" / "records.jsonl"


def contracts_for_worktree(root: Path) -> list[dict]:
    path = contract_file(root)
    # Earlier versions stored contracts from multiple worktrees in the common records file.
    return [r for r in read_records(path) if r.get("kind") == "contract" and r.get("worktree") == str(path.parents[1])]


def working_tree(root: Path) -> str:
    """Tree hash of the whole working tree, built in a scratch index so the real index is untouched."""
    real_index = Path(git(root, "rev-parse", "--absolute-git-dir")) / "index"
    with tempfile.TemporaryDirectory() as scratch:
        index = Path(scratch) / "index"
        if real_index.exists():
            shutil.copy2(real_index, index)  # keep mtime: git's racy-entry check depends on it
        env = {**os.environ, "GIT_INDEX_FILE": str(index)}
        entries = [e.split(" ", 1) for e in git(root, "ls-files", "-v", "-z", env=env).split("\0") if e]
        sparse = git_ok(root, "config", "--bool", "core.sparseCheckout") == "true"
        assumed = [path for tag, path in entries if tag.islower()]
        # Sparse checkouts mark absent files skip-worktree; elsewhere an absent flagged file was deleted.
        skipped = [path for tag, path in entries if tag.upper() == "S" and (not sparse or (root / path).exists())]
        for flag, paths in (("--no-assume-unchanged", assumed), ("--no-skip-worktree", skipped)):
            if paths:  # one flag per call: with --stdin, update-index applies only the last flag
                git(root, "update-index", flag, "-z", "--stdin", env=env, stdin="\0".join(paths))
        git(root, "add", "-A", env=env)
        return git(root, "write-tree", env=env)


def tree_of(root: Path, rev: str) -> str:
    found = git_ok(root, "rev-parse", "--verify", "-q", f"{rev}^{{tree}}")
    if found:
        return found
    if rev != "HEAD":
        raise SystemExit(f"unknown base revision: {rev}")
    return git(root, "hash-object", "-t", "tree", "--stdin", stdin="")


def commit_of(root: Path, rev: str) -> str | None:
    return git_ok(root, "rev-parse", "--verify", "-q", f"{rev}^{{commit}}")


def read_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def append(root: Path, record: dict) -> dict:
    stamped = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **record}
    path = contract_file(root) if record["kind"] == "contract" else records_file(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        handle.write(json.dumps(stamped) + "\n")
    return stamped


def child_env() -> dict[str, str]:
    """Drop repo-locating GIT_* variables (as set inside git hooks), so checks never act on this repo by accident."""
    local = set(subprocess.run(["git", "rev-parse", "--local-env-vars"], text=True, capture_output=True).stdout.split())
    return {key: value for key, value in os.environ.items() if key not in local}


def run_captured(argv: list[str], cwd: Path, stdin: str | None = None, timeout: int | None = None) -> tuple[int, str]:
    try:
        result = subprocess.run(
            argv,
            cwd=cwd,
            env=child_env(),
            input=stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError as error:
        return 127, f"{error}\n"
    except subprocess.TimeoutExpired as error:
        output = error.output if isinstance(error.output, str) else ""
        return 124, output + f"\ntimed out after {timeout}s\n"
    return result.returncode, result.stdout


def changed_files(root: Path, old: str, new: str) -> list[FileChange]:
    # NUL-delimited metadata is authoritative even for quoted paths or filenames containing " b/".
    output = subprocess.check_output(
        [
            "git",
            *DIFF,
            "--ignore-submodules=none",
            "--submodule=short",
            "--raw",
            "-z",
            "--no-abbrev",
            "--patch",
            "--unified=3",
            old,
            new,
            "--",
        ],
        cwd=root,
    )
    if not output:
        return []
    raw, patches = output.split(b"\0\0", 1)
    entries = raw.split(b"\0")
    blocks = re.split(rb"(?m)(?=^diff --git )", patches)[1:]
    # Git emits a deletion and an addition with the same header for a file type change.
    chunks = [b"".join(group) for _, group in groupby(blocks, key=lambda block: block.partition(b"\n")[0])]
    if len(entries) != 2 * len(chunks):
        raise SystemExit("could not match Git patch data to file metadata")
    changes = []
    for i, chunk in enumerate(chunks):
        versions = entries[2 * i].decode("ascii")
        path = os.fsdecode(entries[2 * i + 1])
        patch = chunk.decode("utf-8", errors="backslashreplace")
        triggers = classify(path, versions.endswith((" D", " T")), patch)
        if b"\0" in chunk and not triggers:
            patch = f"Binary change in {path!r} ({versions})\n"
        else:
            patch = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", lambda m: f"\\x{ord(m[0]):02x}", patch)
        changes.append(FileChange(path, versions, patch, triggers))
    return changes


def receipt_checks(root: Path, records: list[dict], head: str, head_tree: str, rerun: bool) -> list[tuple[bool, str]]:
    passing = [r for r in for_tree(records, "receipt", head_tree) if r["exit_code"] == 0]
    if not passing:
        return [(False, f"receipt: no passing receipt for HEAD (tree {head_tree[:12]})")]
    unique = list({(tuple(r["cmd"]), r["cwd"]): r for r in passing}.values())
    if not rerun:
        return [(True, f"receipt: exit 0 {shlex.join(r['cmd'])} (not rerun)") for r in unique]
    checks = []
    for record in unique:
        with detached_checkout(root, head) as checkout:
            code, _ = run_captured(record["cmd"], checkout / record["cwd"], timeout=RERUN_TIMEOUT_S)
        checks.append((code == 0, f"receipt: {shlex.join(record['cmd'])} reran with exit {code}"))
    return checks


@dataclass
class ReviewCheck:
    required: bool
    ok: bool
    message: str
    source: str | None = None


def review_check(root: Path, records: list[dict], base_tree: str, head_tree: str) -> ReviewCheck:
    changes = [c for c in changed_files(root, base_tree, head_tree) if c.triggers]
    if not changes:
        return ReviewCheck(False, True, "review: not required (no trigger in the diff)")
    triggers = [reason for change in changes for reason in change.triggers]
    paths = {c.path for c in changes}
    state: dict[str, str] = {}
    source = None
    for review in records:
        if review.get("kind") != "review":
            continue
        found = review_verdict(review)
        files = review.get("files")
        if found == "ISSUES":
            # Older records have no manifest. If Git pruned the snapshot, retain the objection.
            if files is None and all(
                review.get(k) and git_ok(root, "cat-file", "-e", review[k]) is not None for k in ("base", "tree")
            ):
                files = {c.path for c in changed_files(root, review["base"], review["tree"])}
            if files is None or paths.intersection(files):
                state[review["by"]] = "ISSUES"
        elif found == "PASS" and files and all(files.get(c.path) == c.versions for c in changes):
            state[review["by"]] = "PASS"
            source = review["source"]
    issues = sorted(by for by, verdict_ in state.items() if verdict_ == "ISSUES")
    saw = sorted(by for by, verdict_ in state.items() if verdict_ == "PASS")
    if saw and not issues:
        return ReviewCheck(True, True, f"review: VERDICT: PASS by {', '.join(saw)} saw the triggered changes", source)
    reasons = "\n    ".join(triggers)
    found = f"latest verdict ISSUES from {', '.join(issues)}" if issues else "no passing review saw them"
    return ReviewCheck(True, False, f"review: required, {found}; triggers:\n    {reasons}")


def gate(root: Path, base: str, rerun: bool) -> int:
    records = read_records(records_file(root))
    head = commit_of(root, "HEAD")
    if head is None:
        print("FAIL gate needs a commit at HEAD")
        return 1
    head_tree = tree_of(root, head)
    checks = receipt_checks(root, records, head, head_tree, rerun)
    review = review_check(root, records, tree_of(root, base), head_tree)
    checks.append((review.ok, review.message))
    print("\n".join(f"{'PASS' if ok else 'FAIL'} {message}" for ok, message in checks))
    return 0 if all(ok for ok, _ in checks) else 1


def default_base(root: Path) -> str:
    if git_ok(root, "rev-parse", "--verify", "-q", "@{upstream}") is None:
        raise SystemExit("no upstream branch; pass --base REV")
    return git(root, "merge-base", "HEAD", "@{upstream}")


def review_commit(root: Path, tree: str) -> str:
    parent = commit_of(root, "HEAD")
    return git(root, *GIT_IDENTITY, "commit-tree", tree, *(["-p", parent] if parent else []), "-m", "review snapshot")


@contextmanager
def detached_checkout(root: Path, commit: str) -> Generator[Path]:
    with tempfile.TemporaryDirectory() as scratch:
        checkout = Path(scratch) / "checkout"
        git(root, "-c", "core.hooksPath=/dev/null", "worktree", "add", "--detach", "-q", str(checkout), commit)
        try:
            yield checkout
        finally:
            git(root, "-c", "core.hooksPath=/dev/null", "worktree", "remove", "--force", str(checkout))


# --- commands -------------------------------------------------------------------------------


def cmd_receipt(root: Path, args: argparse.Namespace) -> int:
    argv = args.cmd[1:] if args.cmd[:1] == ["--"] else args.cmd
    if not argv:
        raise SystemExit("receipt needs a command after --")
    tree = working_tree(root)
    code, output = run_captured(argv, Path.cwd())
    sys.stdout.write(output)
    append(
        root,
        {
            "kind": "receipt",
            "tree": tree,
            "cmd": argv,
            "cwd": os.path.relpath(Path.cwd(), root),
            "exit_code": code,
            "output_sha256": sha256(output),
            "output_tail": output[-TAIL_CHARS:],
        },
    )
    return code


def cmd_contract(root: Path, args: argparse.Namespace) -> int:
    record = append(
        root,
        {
            "kind": "contract",
            "tree": working_tree(root),
            "worktree": git(root, "rev-parse", "--absolute-git-dir"),
            "interpretation": args.interpretation,
            "keep": args.keep,
            "reject": args.reject or [],
        },
    )
    print(f"contract recorded at tree {record['tree']}")
    return 0


def current_brief(root: Path, args: argparse.Namespace, tree: str) -> tuple[str, dict]:
    base = tree_of(root, args.base)
    diff, files = compose_diff(changed_files(root, base, tree))
    contract = latest(contracts_for_worktree(root), "contract")
    brief = build_brief(args.request, contract, args.context or [], diff, base, tree)
    return brief, {"tree": tree, "base": base, "files": files, "brief_sha256": sha256(brief)}


def cmd_brief(root: Path, args: argparse.Namespace) -> int:
    brief, seen = current_brief(root, args, working_tree(root))
    append(root, {"kind": "brief", **seen})
    sys.stdout.buffer.write(brief.encode())
    return 0


def record_findings(root: Path, args: argparse.Namespace) -> int:
    if not args.by or not args.brief:
        raise SystemExit("review --findings needs --by NAME and --brief FILE (the brief that reviewer was given)")
    shown = hashlib.sha256(Path(args.brief).read_bytes()).hexdigest()
    briefs = [r for r in read_records(records_file(root)) if r.get("kind") == "brief" and r["brief_sha256"] == shown]
    if not briefs:
        raise SystemExit(f"{args.brief} does not match a recorded brief; produce it with `evidence.py brief`")
    brief = briefs[-1]
    seen = {key: brief[key] for key in ("tree", "base", "brief_sha256", "files") if key in brief}
    append(
        root,
        {"kind": "review", **seen, "source": "host-agent", "by": args.by, "output": Path(args.findings).read_text()},
    )
    print(f"review by {args.by} recorded for the brief of tree {brief['tree']}")
    return 0


def cmd_review(root: Path, args: argparse.Namespace) -> int:
    if args.findings:
        return record_findings(root, args)
    tree = working_tree(root)
    reviewer = args.cmd or os.environ.get("JIMMY_REVIEWER")
    if not args.request:
        raise SystemExit("review needs --request, or --findings FILE --by NAME --brief FILE")
    if not reviewer:
        reason = "no reviewer command (--cmd or JIMMY_REVIEWER)"
        append(root, {"kind": "review_missing", "tree": tree, "reason": reason})
        print(f"independent review unavailable: {reason}; report it as missing", file=sys.stderr)
        return 2
    brief, seen = current_brief(root, args, tree)
    with detached_checkout(root, review_commit(root, tree)) as checkout:
        code, output = run_captured(shlex.split(reviewer), checkout, stdin=brief, timeout=REVIEW_TIMEOUT_S)
    sys.stdout.write(output)
    append(
        root,
        {
            "kind": "review",
            **seen,
            "source": "command",
            "by": args.by or reviewer,
            "exit_code": code,
            "output": output,
        },
    )
    return code


def cmd_gate(root: Path, args: argparse.Namespace) -> int:
    return gate(root, args.base or default_base(root), not args.no_rerun)


def cmd_status(root: Path, _: argparse.Namespace) -> int:
    contract = latest(contracts_for_worktree(root), "contract")
    print("\n".join(status_lines(read_records(records_file(root)), working_tree(root), contract)))
    return 0


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = top.add_subparsers(dest="command", required=True)
    receipt = sub.add_parser("receipt", help="run and record a check")
    receipt.add_argument("cmd", nargs=argparse.REMAINDER)
    contract = sub.add_parser("contract", help="record the behavioral contract")
    contract.add_argument("--interpretation", required=True)
    contract.add_argument("--keep", action="append", required=True, help="case that must hold")
    contract.add_argument("--reject", action="append", help="case that must be rejected")
    for name in ("brief", "review"):
        command = sub.add_parser(name, help=f"{name} independent review")
        command.add_argument("--request", required=name == "brief")
        command.add_argument("--context", action="append")
        command.add_argument("--base", default="HEAD", help="revision the reviewed diff starts from (default HEAD)")
    review = sub.choices["review"]
    review.add_argument("--cmd", help="reviewer CLI that reads the brief on stdin")
    review.add_argument("--findings", help="file with findings from a host-agent reviewer")
    review.add_argument("--by", help="reviewer name, required with --findings")
    review.add_argument("--brief", help="the brief file that reviewer was given, required with --findings")
    sub.add_parser("status", help="records for the current tree")
    gate_parser = sub.add_parser("gate", help="check HEAD's evidence before delivery")
    gate_parser.add_argument("--base", help="revision the delivered diff starts from (default: upstream merge-base)")
    gate_parser.add_argument("--no-rerun", action="store_true", help="trust receipts without rerunning them")
    return top


COMMANDS = {
    "gate": cmd_gate,
    "receipt": cmd_receipt,
    "contract": cmd_contract,
    "brief": cmd_brief,
    "review": cmd_review,
    "status": cmd_status,
}


def main() -> int:
    args = parser().parse_args()
    return COMMANDS[args.command](repo_root(Path.cwd()), args)


if __name__ == "__main__":
    sys.exit(main())
