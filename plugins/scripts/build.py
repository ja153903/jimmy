#!/usr/bin/env python3
"""Build reproducible Codex and Claude Code packages from the pinned pstack source."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True
from upstream import verify_source


VERSION = "0.5.0"
HOSTS = ("codex", "claude")
SKILL_PREAMBLE = (
    "Before following this skill, read [efficiency](../../docs/efficiency.md) and "
    "[the host runtime](../../docs/runtime.md) once per workflow context. "
    "Their host and routing rules supersede the inherited instructions below."
)
AGENT_PREAMBLE = (
    "Before following this agent, read [efficiency](../docs/efficiency.md) and "
    "[the host runtime](../docs/runtime.md) once per workflow context. "
    "Their host and routing rules supersede the inherited instructions below."
)
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
INLINE_LINK = re.compile(r"\[[^\]]+\]\((<[^>]+>|[^)]+)\)")
REFERENCE_LINK = re.compile(r"^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)", re.MULTILINE)


class BuildError(Exception):
    pass


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def write_generated(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    path.chmod(0o644)


def tree_files(root: Path) -> dict[str, Path]:
    if root.is_symlink():
        raise BuildError(f"symlink is not allowed: {root}")
    result = {}
    for directory, names, files in os.walk(root, followlinks=False):
        for name in names + files:
            path = Path(directory) / name
            if path.is_symlink():
                raise BuildError(f"symlink is not allowed: {path}")
        for name in files:
            path = Path(directory) / name
            if not path.is_file():
                raise BuildError(f"not a regular file: {path}")
            result[path.relative_to(root).as_posix()] = path
    return result


def copy_layer(layer: Path, package: Path) -> None:
    if not layer.is_dir():
        return
    for relative, source in sorted(tree_files(layer).items()):
        destination = package / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def split_frontmatter(path: Path) -> tuple[list[str], str]:
    contents = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(contents)
    if match is None:
        raise BuildError(f"missing frontmatter: {path}")
    lines = match.group(1).splitlines()
    if not any(line.startswith("description:") for line in lines):
        raise BuildError(f"missing description: {path}")
    return lines, contents[match.end():]


def source_explicit_skills(source_root: Path) -> set[str]:
    explicit = set()
    for skill in (source_root / "jimmy" / "skills").glob("*/SKILL.md"):
        lines, _ = split_frontmatter(skill)
        if "disable-model-invocation: true" in lines:
            explicit.add(skill.parent.name)
    return explicit


def codex_explicit_policy(skill_dir: Path) -> None:
    policy_file = skill_dir / "agents/openai.yaml"
    if not policy_file.exists():
        write_generated(policy_file, b"policy:\n  allow_implicit_invocation: false\n")
        return
    contents = policy_file.read_text(encoding="utf-8")
    top_policy = re.search(r"(?m)^policy:[ \t]*$", contents)
    if top_policy is None:
        contents = contents.rstrip("\n") + "\npolicy:\n  allow_implicit_invocation: false\n"
    else:
        rest = contents[top_policy.end():]
        next_field = re.search(r"(?m)^\S", rest)
        end = top_policy.end() + (next_field.start() if next_field else len(rest))
        block = contents[top_policy.end():end]
        existing = re.search(r"(?m)^  allow_implicit_invocation:.*$", block)
        if existing:
            block = block[:existing.start()] + "  allow_implicit_invocation: false" + block[existing.end():]
        else:
            block = "\n  allow_implicit_invocation: false\n" + block.lstrip("\n")
        contents = contents[:top_policy.end()] + block + contents[end:]
    policy_file.write_text(contents, encoding="utf-8")


def normalize_markdown(package: Path, host: str, explicit_skills: set[str]) -> None:
    for path in sorted((package / "skills").glob("*/SKILL.md")):
        lines, body = split_frontmatter(path)
        slug = path.parent.name
        fields = []
        for line in lines:
            key = line.split(":", 1)[0]
            if key in {"name", "icon", "color", "paths", "disable-model-invocation"}:
                continue
            fields.append(line)
        fields.insert(0, f"name: {slug}")
        if host == "claude" and slug in explicit_skills:
            fields.append("disable-model-invocation: true")
        path.write_text("---\n" + "\n".join(fields) + "\n---\n\n" + SKILL_PREAMBLE + "\n\n" + body.lstrip("\n"), encoding="utf-8")
        if host == "codex" and slug in explicit_skills:
            codex_explicit_policy(path.parent)
    for path in sorted((package / "agents").glob("*.md")):
        lines, body = split_frontmatter(path)
        fields = [line for line in lines if line.split(":", 1)[0] not in {"is_background", "icon", "color"}]
        path.write_text("---\n" + "\n".join(fields) + "\n---\n\n" + AGENT_PREAMBLE + "\n\n" + body.lstrip("\n"), encoding="utf-8")


def local_link_targets(markdown: str) -> list[str]:
    outside_fences = []
    fenced = False
    for line in markdown.splitlines():
        if re.match(r"^\s*(```|~~~)", line):
            fenced = not fenced
            continue
        if not fenced:
            outside_fences.append(line)
    text = "\n".join(outside_fences)
    return [match.group(1) for expression in (INLINE_LINK, REFERENCE_LINK) for match in expression.finditer(text)]


def check_links(package: Path) -> None:
    missing = []
    for relative, path in sorted(tree_files(package).items()):
        if not relative.endswith(".md") or relative == "docs/upstream-mode.md":
            continue
        for raw in local_link_targets(path.read_text(encoding="utf-8")):
            target = raw.strip("<>").split(" ", 1)[0]
            if not target or target == "url" or target.startswith(("#", "$", "{", "*")):
                continue
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or target.startswith("//"):
                continue
            if any(char in parsed.path for char in ("{", "}", "*", "`")):
                continue
            linked = (path.parent / unquote(parsed.path)).resolve()
            if not linked.is_relative_to(package.resolve()) or not linked.exists():
                missing.append(f"{relative} -> {target}")
    if missing:
        raise BuildError("broken local Markdown links:\n" + "\n".join(missing))


def inventory(package: Path) -> dict[str, dict[str, object]]:
    return {
        relative: {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "mode": stat.S_IMODE(path.stat().st_mode),
        }
        for relative, path in sorted(tree_files(package).items())
        if relative != "build-info.json"
    }


def package_metadata(package: Path, host: str) -> None:
    description = "Jimmy workflows and principles for Claude Code and Codex."
    manifest = {
        "name": "jimmy",
        "version": VERSION,
        "description": description,
        "author": {"name": "Jaime Abbariao"},
        "skills": "./skills/",
    }
    if host == "codex":
        manifest["interface"] = {
            "displayName": "Jimmy",
            "shortDescription": "Focused workflows for coding agents.",
            "longDescription": description,
            "developerName": "Jaime Abbariao",
            "category": "Productivity",
            "capabilities": ["Write"],
            "defaultPrompt": ["Use jimmy for this task."],
        }
        write_generated(package / ".codex-plugin/plugin.json", json_bytes(manifest))
        market = {
            "name": "jimmy",
            "interface": {"displayName": "Jimmy"},
            "plugins": [{
                "name": "jimmy",
                "source": {"source": "local", "path": "./"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Productivity",
            }],
        }
        write_generated(package / ".agents/plugins/marketplace.json", json_bytes(market))
    else:
        write_generated(package / ".claude-plugin/plugin.json", json_bytes(manifest))
        market = {
            "name": "jimmy",
            "owner": {"name": "Jaime Abbariao"},
            "plugins": [{"name": "jimmy", "source": "./"}],
        }
        write_generated(package / ".claude-plugin/marketplace.json", json_bytes(market))


def readme(host: str, source_version: str) -> bytes:
    directory = ".agents/plugins" if host == "codex" else ".claude-plugin"
    return (
        f"# Jimmy for {'Codex' if host == 'codex' else 'Claude Code'}\n\n"
        f"This package adapts pinned pstack {source_version} for {host}. "
        "Its source pin and package checksums are in [build-info.json](build-info.json).\n\n"
        f"Install this package using [{directory}/marketplace.json]({directory}/marketplace.json), "
        "then invoke the [Jimmy skill](skills/jimmy/SKILL.md).\n\n"
        "[Host runtime](docs/runtime.md) describes the supported tools and roles. "
        "[Efficiency](docs/efficiency.md) describes how to keep workflows focused.\n\n"
        "The complete imported mode, with Jimmy naming, is preserved in [docs/upstream-mode.md](docs/upstream-mode.md) for audit.\n"
    ).encode()


def build_package(root: Path, package: Path, host: str, lock: dict) -> None:
    source = root / "jimmy"
    package.mkdir(parents=True)
    for relative in sorted(lock["files"]):
        if not relative.startswith("jimmy/") or relative == "jimmy/README.md":
            continue
        source_file = root / relative
        target = package / Path(relative).relative_to("jimmy")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target)
    original_mode = source / "skills/jimmy-mode/SKILL.md"
    write_generated(package / "docs/upstream-mode.md", original_mode.read_bytes())
    for layer in (root / "adapters/common", root / f"adapters/{host}"):
        copy_layer(layer, package)
    for required in ("docs/efficiency.md", "docs/runtime.md", "skills/jimmy/SKILL.md"):
        if not (package / required).is_file():
            raise BuildError(f"missing adapter file for {host}: {required}")
    normalize_markdown(package, host, source_explicit_skills(root))
    write_generated(package / "README.md", readme(host, lock["version"]))
    package_metadata(package, host)
    build_info = {
        "source": {key: lock[key] for key in ("repository", "path", "commit", "version", "transform") if key in lock},
        "package_version": VERSION,
        "host": host,
        "files": inventory(package),
    }
    write_generated(package / "build-info.json", json_bytes(build_info))
    check_links(package)
    for relative, path in tree_files(package).items():
        if stat.S_IMODE(path.stat().st_mode) & 0o111 and b".cursor/" in path.read_bytes():
            raise BuildError(f"Cursor filesystem dependency in executable: {host}/{relative}")


def compare_packages(expected: Path, actual: Path) -> list[str]:
    if not actual.is_dir():
        return [f"missing package: {actual}"]
    expected_files = tree_files(expected)
    actual_files = tree_files(actual)
    errors = []
    for relative in sorted(expected_files.keys() - actual_files.keys()):
        errors.append(f"missing: {actual.name}/{relative}")
    for relative in sorted(actual_files.keys() - expected_files.keys()):
        errors.append(f"stale: {actual.name}/{relative}")
    for relative in sorted(expected_files.keys() & actual_files.keys()):
        if expected_files[relative].read_bytes() != actual_files[relative].read_bytes():
            errors.append(f"different bytes: {actual.name}/{relative}")
        if stat.S_IMODE(expected_files[relative].stat().st_mode) != stat.S_IMODE(actual_files[relative].stat().st_mode):
            errors.append(f"different mode: {actual.name}/{relative}")
    return errors


def publish_packages(stage: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    changed = [host for host in HOSTS if compare_packages(stage / host, output / host)]
    if not changed:
        return
    backups = stage / "backups"
    backups.mkdir()
    installed = []
    try:
        for host in changed:
            destination = output / host
            if destination.exists():
                os.replace(destination, backups / host)
            os.replace(stage / host, destination)
            installed.append(host)
    except Exception:
        for host in reversed(changed):
            destination = output / host
            backup = backups / host
            if host in installed and destination.exists():
                shutil.rmtree(destination)
            if backup.exists():
                os.replace(backup, destination)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--check", action="store_true", help="compare all output bytes and modes without changing them")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    for name in ("jimmy", "adapters"):
        if (root / name).is_symlink():
            raise BuildError(f"symlink is not allowed: {root / name}")
    try:
        lock = verify_source(root)
    except (OSError, ValueError) as error:
        raise BuildError(str(error)) from error
    output = root / "dist"
    with tempfile.TemporaryDirectory(prefix=".jimmy-build-", dir=None if args.check else root) as temporary:
        stage = Path(temporary)
        for host in HOSTS:
            build_package(root, stage / host, host, lock)
        if args.check:
            errors = [error for host in HOSTS for error in compare_packages(stage / host, output / host)]
            if errors:
                raise BuildError("package drift:\n" + "\n".join(errors))
        else:
            publish_packages(stage, output)
    print("PASS: codex and claude packages match pinned source and adapters")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BuildError as error:
        print(f"ISSUES: {error}", file=sys.stderr)
        sys.exit(1)
