#!/usr/bin/env python3
"""Validate the maintained Jimmy package without generating or modifying files."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
INLINE_LINK = re.compile(r"\[[^\]]+\]\((<[^>]+>|[^)]+)\)")
REFERENCE_LINK = re.compile(r"^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)", re.MULTILINE)

class PackageError(Exception):
    pass

def tree_files(root: Path) -> dict[str, Path]:
    if root.is_symlink():
        raise PackageError(f"symlink is not allowed: {root}")
    result = {}
    for directory, names, files in os.walk(root, followlinks=False):
        names[:] = [name for name in names if name not in {"node_modules", "__pycache__", ".git"}]
        files = [name for name in files if name != ".DS_Store"]
        for name in names + files:
            path = Path(directory) / name
            if path.is_symlink():
                raise PackageError(f"symlink is not allowed: {path}")
        for name in files:
            path = Path(directory) / name
            if not path.is_file():
                raise PackageError(f"not a regular file: {path}")
            result[path.relative_to(root).as_posix()] = path
    return result


def split_frontmatter(path: Path) -> tuple[list[str], str]:
    contents = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(contents)
    if match is None:
        raise PackageError(f"missing frontmatter: {path}")
    lines = match.group(1).splitlines()
    if not any(line.startswith("description:") for line in lines):
        raise PackageError(f"missing description: {path}")
    return lines, contents[match.end():]


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
        if not relative.endswith(".md"):
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
        raise PackageError("broken local Markdown links:\n" + "\n".join(missing))



def check_package(package: Path) -> int:
    if not package.is_dir():
        raise PackageError(f"missing package: {package}")
    tree_files(package)
    manifests = []
    for host in ("claude", "codex"):
        path = package / f".{host}-plugin/plugin.json"
        try:
            manifest = json.loads(path.read_text())
        except (OSError, ValueError) as error:
            raise PackageError(f"invalid manifest: {path}") from error
        for field in ("name", "description", "version"):
            if not isinstance(manifest.get(field), str) or not manifest[field].strip():
                raise PackageError(f"missing {field}: {path}")
        if manifest.get("skills") != "./skills/":
            raise PackageError(f"manifest must use shared ./skills/: {path}")
        manifests.append(manifest)
    for field in ("name", "version", "description"):
        if manifests[0][field] != manifests[1][field]:
            raise PackageError(f"manifest {field} differs between hosts")
    skills = sorted((package / "skills").glob("*/SKILL.md"))
    if not skills:
        raise PackageError("package contains no skills")
    for skill in skills:
        lines, body = split_frontmatter(skill)
        if f"name: {skill.parent.name}" not in lines or not re.fullmatch(r"[a-z0-9-]{1,64}", skill.parent.name):
            raise PackageError(f"skill name must match directory: {skill}")
        if not body.strip():
            raise PackageError(f"empty skill: {skill}")
        # Preserve explicit-only invocation in both hosts in the same skill folder.
        if "disable-model-invocation: true" in lines:
            policy = skill.parent / "agents/openai.yaml"
            if not policy.is_file() or not re.search(r"(?m)^  allow_implicit_invocation: false\s*$", policy.read_text()):
                raise PackageError(f"explicit-only skill needs matching invocation policy: {skill}")
    check_links(package)
    return len(skills)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        count = check_package(args.package.absolute())
    except (OSError, ValueError, PackageError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {count} skills in one package; both manifests, invocation policies, and local links valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
