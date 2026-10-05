#!/usr/bin/env python3
"""Check coverage and reviewed file hashes for the pinned pstack port."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote


PLUGIN = Path(__file__).resolve().parents[1]
MANIFEST = PLUGIN / "pstack-upstream.json"
RENAMES = {
    "poteto-mode": "jimmy",
    "setup-pstack": "setup-jimmy",
    "bugbot-triage.md": "review-bot-triage.md",
    "poteto-agent.md": "jimmy-agent.md",
}
IGNORED_DIRECTORIES = {"node_modules", "__pycache__", ".git"}


def resource_files(root):
    for directory, children, names in os.walk(root):
        children[:] = sorted(set(children) - IGNORED_DIRECTORIES)
        for name in sorted(names):
            yield Path(directory) / name


def local_path(relative):
    return Path(*(RENAMES.get(part, part) for part in relative.parts))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(source, version, commit):
    files = []
    paths = [path for directory in ("skills", "agents") for path in resource_files(source / directory)]
    for path in sorted(paths):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        target = local_path(relative)
        if not (PLUGIN / target).is_file():
            raise ValueError(f"Missing ported resource: {target}")
        files.append({
            "upstream": relative.as_posix(),
            "jimmy": target.as_posix(),
            "upstream_sha256": digest(path),
            "jimmy_sha256": digest(PLUGIN / target),
        })
    if not files:
        raise ValueError(f"No upstream skill resources in {source}")
    manifest = {
        "repository": "https://github.com/cursor/plugins",
        "path": "pstack",
        "version": version,
        "commit": commit,
        "scope": "All upstream skills, supporting resources, and agent definitions; Jimmy-only skills and roles are preserved.",
        "adaptations": [
            "Jimmy names, Codex role agents, and capability-aware runtime tools.",
            "Codex preferences, chat history, and hourly thread heartbeats.",
            "Generic configurable review bots and existing Jimmy tooling improvements.",
            "Portable benchmark commands and corrected behavioral-test examples.",
        ],
        "files": files,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")


def check_references():
    problems = []
    for path in sorted(path for path in resource_files(PLUGIN / "skills") if path.suffix == ".md"):
        text = path.read_text()
        if path.name == "SKILL.md":
            frontmatter = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)", text, re.S)
            if not frontmatter or not all(re.search(rf"^{key}:\s*\S", frontmatter[1], re.M) for key in ("name", "description")):
                problems.append(f"Invalid skill frontmatter: {path.relative_to(PLUGIN)}")
        prose = re.sub(r"^(`{3,}|~{3,}).*?^\1.*?$", "", text, flags=re.M | re.S)
        for target in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", prose):
            target = unquote(target.split("#", 1)[0].strip("<>"))
            if target.startswith(("./", "../", "references/", "scripts/")) and not (path.parent / target).exists():
                problems.append(f"Broken reference: {path.relative_to(PLUGIN)} -> {target}")
    return problems


def check(source):
    manifest = json.loads(MANIFEST.read_text())
    problems = check_references()
    expected = {item["upstream"] for item in manifest["files"]}
    if source:
        actual = {path.relative_to(source).as_posix() for directory in ("skills", "agents") for path in resource_files(source / directory)}
        for path in sorted(expected - actual):
            problems.append(f"Missing upstream resource: {path}")
        for path in sorted(actual - expected):
            problems.append(f"Unported upstream resource: {path}")
    skills = 0
    for item in manifest["files"]:
        target = PLUGIN / item["jimmy"]
        if not target.is_file():
            problems.append(f"Missing Jimmy resource: {item['jimmy']}")
        elif digest(target) != item["jimmy_sha256"]:
            problems.append(f"Changed since parity review: {item['jimmy']}")
        if source:
            path = source / item["upstream"]
            if path.is_file() and digest(path) != item["upstream_sha256"]:
                problems.append(f"Changed upstream resource: {item['upstream']}")
        skills += Path(item["upstream"]).name == "SKILL.md"
    print(f"pstack {manifest['version']} at {manifest['commit'][:12]}: {skills} skills, {len(expected)} resources, {len(problems)} problems")
    for problem in problems:
        print(problem, file=sys.stderr)
    return bool(problems)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Extracted pstack directory for upstream coverage and hash checks")
    parser.add_argument("--record", action="store_true", help="Record reviewed files after inspecting the port")
    parser.add_argument("--version")
    parser.add_argument("--commit")
    args = parser.parse_args()
    if args.record:
        if not args.source or not args.version or not args.commit:
            parser.error("--record requires --source, --version, and --commit")
        if not re.fullmatch(r"[0-9a-f]{40}", args.commit):
            parser.error("--commit must be a full Git commit hash")
        record(args.source, args.version, args.commit)
    return check(args.source)


if __name__ == "__main__":
    raise SystemExit(main())
