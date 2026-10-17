#!/usr/bin/env python3
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile

from branding import TRANSFORM, brand_source


REPOSITORY = "https://github.com/cursor/plugins.git"
UPSTREAM_PATH = "pstack"
LOCK_FILE = "upstream.lock.json"
PREVIEW_FILE = "upstream.preview.json"
SOURCE_DIRS = ("skills", "agents", "docs")
SOURCE_FILES = ("LICENSE", "README.md")
ADOPT_TARGETS = (
    ".cursor-plugin/plugin.json",
    *(f"jimmy/{name}" for name in SOURCE_DIRS),
    *(f"jimmy/{name}" for name in SOURCE_FILES),
    LOCK_FILE,
)
IGNORED = frozenset({".DS_Store", "__pycache__", "node_modules", ".git"})
COPY_IGNORED = IGNORED | {"dist", "cache"}
SHA_PATTERN = re.compile(r"[0-9a-f]{40}\Z")
REF_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]*\Z")


def _safe_path(path: str) -> None:
    if (
        not path
        or path.startswith("/")
        or "\\" in path
        or any(ord(char) < 32 for char in path)
        or any(part in ("", ".", "..") for part in path.split("/"))
    ):
        raise ValueError(f"unsafe path: {path!r}")


def _managed_path(path: str) -> str | None:
    if path == f"{UPSTREAM_PATH}/.cursor-plugin/plugin.json":
        return ".cursor-plugin/plugin.json"
    if not path.startswith(f"{UPSTREAM_PATH}/"):
        return None
    relative = path[len(UPSTREAM_PATH) + 1 :]
    if any(part in IGNORED for part in relative.split("/")):
        return None
    if relative in SOURCE_FILES or any(relative.startswith(f"{name}/") for name in SOURCE_DIRS):
        return f"jimmy/{relative}"
    return None


def _file_record(path: Path) -> dict[str, int | str]:
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f"managed source is not a regular file: {path}")
    return {
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "mode": stat.S_IMODE(info.st_mode),
    }


def snapshot(root: Path | str) -> dict[str, dict[str, int | str]]:
    """Return content and mode records for exactly the managed source files."""
    root = Path(root)
    files: dict[str, dict[str, int | str]] = {}
    for relative in ("jimmy", ".cursor-plugin"):
        path = root / relative
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            raise ValueError(f"managed source parent is not a directory: {relative}")
    for relative in (".cursor-plugin/plugin.json", *(f"jimmy/{name}" for name in SOURCE_FILES)):
        path = root / relative
        if path.is_symlink():
            raise ValueError(f"managed source is a symlink: {relative}")
        if path.exists():
            files[relative] = _file_record(path)
    for name in SOURCE_DIRS:
        base = root / "jimmy" / name
        if base.is_symlink():
            raise ValueError(f"managed source is a symlink: {base.relative_to(root)}")
        if not base.exists():
            continue
        if not base.is_dir():
            raise ValueError(f"managed source is not a directory: {base.relative_to(root)}")
        for current, directories, filenames in os.walk(base, followlinks=False):
            current_path = Path(current)
            directories[:] = sorted(entry for entry in directories if entry not in IGNORED)
            for entry in directories:
                path = current_path / entry
                if path.is_symlink():
                    raise ValueError(f"managed source is a symlink: {path.relative_to(root)}")
            for entry in sorted(filename for filename in filenames if filename not in IGNORED):
                path = current_path / entry
                relative = path.relative_to(root).as_posix()
                _safe_path(relative)
                files[relative] = _file_record(path)
    return dict(sorted(files.items()))


def _version(root: Path) -> str:
    try:
        manifest = json.loads((root / ".cursor-plugin/plugin.json").read_text(encoding="utf-8"))
        version = manifest["version"]
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
        raise ValueError("invalid source plugin manifest") from error
    if not isinstance(version, str) or not version:
        raise ValueError("source plugin manifest has no version")
    return version


def _load_lock(root: Path) -> dict:
    try:
        lock = json.loads((root / LOCK_FILE).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise ValueError(f"cannot read {LOCK_FILE}") from error
    required = {"repository", "path", "commit", "version", "files"}
    if not isinstance(lock, dict) or not required <= set(lock) or set(lock) - required - {"transform"}:
        raise ValueError(f"invalid {LOCK_FILE} fields")
    if lock.get("transform", TRANSFORM) != TRANSFORM:
        raise ValueError(f"unsupported {LOCK_FILE} transform")
    if lock["repository"] != REPOSITORY or lock["path"] != UPSTREAM_PATH:
        raise ValueError(f"invalid {LOCK_FILE} upstream identity")
    if not isinstance(lock["commit"], str) or not SHA_PATTERN.fullmatch(lock["commit"]):
        raise ValueError(f"invalid {LOCK_FILE} commit")
    if not isinstance(lock["version"], str) or not lock["version"]:
        raise ValueError(f"invalid {LOCK_FILE} version")
    files = lock["files"]
    if not isinstance(files, dict):
        raise ValueError(f"invalid {LOCK_FILE} files")
    for path, record in files.items():
        if not isinstance(path, str):
            raise ValueError(f"invalid {LOCK_FILE} path")
        _safe_path(path)
        if path != ".cursor-plugin/plugin.json" and path not in (f"jimmy/{name}" for name in SOURCE_FILES) and not any(path.startswith(f"jimmy/{name}/") for name in SOURCE_DIRS):
            raise ValueError(f"unmanaged {LOCK_FILE} path: {path}")
        if not isinstance(record, dict) or set(record) != {"sha256", "mode"}:
            raise ValueError(f"invalid {LOCK_FILE} record: {path}")
        if not isinstance(record["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", record["sha256"]):
            raise ValueError(f"invalid {LOCK_FILE} digest: {path}")
        if type(record["mode"]) is not int or record["mode"] not in (0o644, 0o755):
            raise ValueError(f"invalid {LOCK_FILE} mode: {path}")
    return lock


def verify_source(root: Path | str) -> dict:
    """Validate the offline source snapshot against its committed upstream pin."""
    root = Path(root)
    lock = _load_lock(root)
    current = snapshot(root)
    expected = lock["files"]
    missing = sorted(set(expected) - set(current))
    extra = sorted(set(current) - set(expected))
    changed = sorted(path for path in expected.keys() & current.keys() if expected[path] != current[path])
    if missing or extra or changed:
        parts = [f"missing: {', '.join(missing)}" if missing else "", f"extra: {', '.join(extra)}" if extra else "", f"changed: {', '.join(changed)}" if changed else ""]
        raise ValueError("source differs from upstream pin; " + "; ".join(part for part in parts if part))
    if _version(root) != lock["version"]:
        raise ValueError("source manifest version differs from upstream pin")
    return lock


def _git(arguments: list[str], *, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(["git", *arguments], input=input_bytes, capture_output=True, check=False)
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"git {' '.join(arguments[:2])} failed: {message}")
    return result.stdout


def _validate_ref(ref: str) -> None:
    if not REF_PATTERN.fullmatch(ref) or ".." in ref or "//" in ref or any(part.startswith(".") or part.endswith(".lock") for part in ref.split("/")):
        raise ValueError(f"unsafe ref: {ref!r}")


def _fetch(repository: str, ref: str, git_dir: Path) -> str:
    _validate_ref(ref)
    _git(["init", "--quiet", str(git_dir)])
    _git(["-C", str(git_dir), "fetch", "--quiet", "--depth=1", "--no-tags", repository, ref])
    commit = _git(["-C", str(git_dir), "rev-parse", "--verify", "FETCH_HEAD^{commit}"]).decode("ascii").strip()
    if not SHA_PATTERN.fullmatch(commit):
        raise ValueError("git returned an invalid commit")
    return commit


def _tree(git_dir: Path, commit: str) -> dict[str, tuple[str, int]]:
    output = _git(["-C", str(git_dir), "ls-tree", "-r", "-z", commit, "--", UPSTREAM_PATH])
    entries: dict[str, tuple[str, int]] = {}
    for entry in output.split(b"\0"):
        if not entry:
            continue
        try:
            header, raw_path = entry.split(b"\t", 1)
            mode, kind, raw_oid = header.split(b" ", 2)
            path = raw_path.decode("utf-8", errors="surrogateescape")
        except (ValueError, UnicodeError) as error:
            raise ValueError("unsafe upstream tree entry") from error
        target = _managed_path(path)
        if target is None:
            continue
        try:
            path.encode("utf-8")
            oid = raw_oid.decode("ascii")
        except UnicodeError as error:
            raise ValueError(f"unsafe upstream tree entry: {path!r}") from error
        _safe_path(path)
        if not path.startswith(f"{UPSTREAM_PATH}/"):
            raise ValueError(f"unexpected upstream path: {path}")
        if kind != b"blob" or mode not in (b"100644", b"100755") or not SHA_PATTERN.fullmatch(oid):
            raise ValueError(f"unsupported upstream entry: {path}")
        entries[target] = (oid, int(mode[-3:], 8))
    if ".cursor-plugin/plugin.json" not in entries:
        raise ValueError("upstream tree has no pstack plugin manifest")
    return entries


def _blobs(git_dir: Path, entries: dict[str, tuple[str, int]]) -> dict[str, bytes]:
    oids = sorted({oid for oid, _ in entries.values()})
    output = _git(["-C", str(git_dir), "cat-file", "--batch"], input_bytes=("\n".join(oids) + "\n").encode("ascii"))
    result: dict[str, bytes] = {}
    offset = 0
    for expected_oid in oids:
        end = output.find(b"\n", offset)
        if end < 0:
            raise ValueError("incomplete upstream blob response")
        header = output[offset:end].split(b" ")
        if len(header) != 3 or header[0].decode("ascii") != expected_oid or header[1] != b"blob":
            raise ValueError("invalid upstream blob response")
        size = int(header[2])
        offset = end + 1
        data = output[offset : offset + size]
        if len(data) != size or output[offset + size : offset + size + 1] != b"\n":
            raise ValueError("incomplete upstream blob response")
        result[expected_oid] = data
        offset += size + 1
    return result


def _copy_ignore(directory: str, names: list[str]) -> set[str]:
    return set(names) & COPY_IGNORED


def _replace_source(stage: Path, entries: dict[str, tuple[str, int]], blobs: dict[str, bytes]) -> None:
    for name in SOURCE_DIRS:
        shutil.rmtree(stage / "jimmy" / name, ignore_errors=True)
    for relative in (".cursor-plugin/plugin.json", *(f"jimmy/{name}" for name in SOURCE_FILES)):
        (stage / relative).unlink(missing_ok=True)
    files = brand_source({relative: (blobs[oid], mode) for relative, (oid, mode) in entries.items()})
    for relative, (data, mode) in files.items():
        path = stage / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(mode)


def _replace_source_from_preview(stage: Path, preview: Path, files: dict) -> None:
    for name in SOURCE_DIRS:
        shutil.rmtree(stage / "jimmy" / name, ignore_errors=True)
    for relative in (".cursor-plugin/plugin.json", *(f"jimmy/{name}" for name in SOURCE_FILES)):
        (stage / relative).unlink(missing_ok=True)
    for relative, record in files.items():
        path = stage / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((preview / relative).read_bytes())
        path.chmod(record["mode"])
    shutil.copy2(preview / LOCK_FILE, stage / LOCK_FILE)


def _local_snapshot(root: Path) -> dict[str, tuple[str, int]]:
    files: dict[str, tuple[str, int]] = {}
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        relative_dir = current_path.relative_to(root)
        directories[:] = sorted(name for name in directories if name not in COPY_IGNORED)
        if relative_dir == Path("."):
            directories[:] = [name for name in directories if name not in ("jimmy", ".cursor-plugin")]
        for name in sorted(filenames):
            if name in COPY_IGNORED or name in (LOCK_FILE, PREVIEW_FILE):
                continue
            relative = (relative_dir / name).as_posix()
            if relative == ".cursor-plugin/plugin.json":
                continue
            path = current_path / name
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode):
                digest = hashlib.sha256(os.readlink(path).encode("utf-8")).hexdigest()
            elif stat.S_ISREG(info.st_mode):
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
            else:
                raise ValueError(f"unsupported local file: {relative}")
            files[relative] = (digest, stat.S_IMODE(info.st_mode))
    return files


def _build(stage: Path) -> None:
    build = stage / "scripts/build.py"
    if not build.exists() or not stat.S_ISREG(build.lstat().st_mode):
        raise ValueError("staged build.py is missing or not a regular file")
    result = subprocess.run([sys.executable, str(build)], cwd=stage, capture_output=True, text=True, check=False)
    if result.returncode:
        raise ValueError(f"staged build failed ({result.returncode}):\n{result.stdout}{result.stderr}")


def _remove(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink(missing_ok=True)


@contextmanager
def _accept_lock(root: Path):
    lock_path = root.parent / f".{root.name}.upstream-accept.lock"
    with lock_path.open("a+b") as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError("another upstream accept is already running") from error
        try:
            yield
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def _backup_path(root: Path) -> Path:
    return root.parent / f".{root.name}.upstream-backup"


def _recover(root: Path) -> None:
    backup = _backup_path(root)
    if backup.is_symlink():
        raise ValueError(f"upstream backup is a symlink: {backup}")
    if not backup.exists():
        return
    journal = backup / "journal.json"
    if not journal.exists():
        if not any(backup.iterdir()):
            backup.rmdir()
            return
        raise ValueError(f"incomplete upstream backup needs inspection: {backup}")
    try:
        entries = json.loads(journal.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise ValueError(f"invalid upstream backup journal: {backup}") from error
    if not isinstance(entries, dict) or set(entries) - (set(ADOPT_TARGETS) | {"dist"}) or any(not isinstance(path, str) or type(existed) is not bool for path, existed in entries.items()):
        raise ValueError(f"invalid upstream backup journal: {backup}")
    if (backup / "committed").exists():
        shutil.rmtree(backup)
        return
    for relative, existed in reversed(list(entries.items())):
        _safe_path(relative)
        destination = root / relative
        saved = backup / relative
        if saved.exists():
            _remove(destination)
            destination.parent.mkdir(parents=True, exist_ok=True)
            saved.rename(destination)
        elif not existed:
            _remove(destination)
    shutil.rmtree(backup)


def _adopt(root: Path, stage: Path) -> None:
    targets = list(ADOPT_TARGETS)
    if (stage / "dist").exists():
        if (stage / "dist").is_symlink():
            raise ValueError("staged dist is a symlink")
        targets.append("dist")
    backup = _backup_path(root)
    backup.mkdir()
    entries = {relative: (root / relative).exists() for relative in targets}
    journal = backup / "journal.json"
    try:
        journal.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    except BaseException:
        shutil.rmtree(backup)
        raise
    try:
        for relative in targets:
            destination = root / relative
            saved = backup / relative
            if entries[relative]:
                saved.parent.mkdir(parents=True, exist_ok=True)
                destination.rename(saved)
            incoming = stage / relative
            if incoming.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                incoming.rename(destination)
        verify_source(root)
        (backup / "committed").touch()
    except BaseException:
        _recover(root)
        raise
    shutil.rmtree(backup)


def _report(old: dict, new: dict, root: Path) -> str:
    before = old["files"]
    after = new["files"]
    added = sorted(set(after) - set(before))
    deleted = sorted(set(before) - set(after))
    changed = sorted(path for path in before.keys() & after.keys() if before[path] != after[path])
    lines = [
        f"Upstream {old['commit']} -> {new['commit']}",
        f"Version {old['version']} -> {new['version']}",
        f"Changed ({len(changed)}):", *(f"  {path}" for path in changed),
        f"Added ({len(added)}):", *(f"  {path}" for path in added),
        f"Deleted ({len(deleted)}):", *(f"  {path}" for path in deleted),
    ]
    review = [path for path in sorted(set(changed + added + deleted)) if (path.startswith("jimmy/skills/") or path.startswith("jimmy/agents/")) and path.lower().endswith((".md", ".markdown"))]
    lines.extend([f"Semantic adapter review required ({len(review)}):", *(f"  {path}" for path in review)])
    overrides = []
    for path in sorted(set(changed + deleted)):
        if not path.startswith("jimmy/"):
            continue
        relative = path[len("jimmy/") :]
        for host in ("common", "claude", "codex"):
            replacement = f"adapters/{host}/{relative}"
            if (root / replacement).is_file():
                overrides.append((path, replacement))
    lines.extend([f"Adapter override review required ({len(overrides)}). No automatic semantic merge for replaced files.", *(f"  {source} -> {replacement}" for source, replacement in overrides)])
    return "\n".join(lines)


def create_preview(root: Path | str, output: Path | str, ref: str, repository: str | None = None) -> str:
    """Publish a complete update to a new directory after validating and building it."""
    root = Path(root).resolve(strict=True)
    if Path(output).is_symlink():
        raise ValueError("output must not be a symlink")
    output = Path(output).resolve(strict=False)
    if output.exists() or output == root or root in output.parents or output in root.parents:
        raise ValueError("output must be a new directory outside the source tree")
    if not output.parent.is_dir():
        raise ValueError("output parent directory does not exist")
    old = verify_source(root)
    if repository is None:
        source_repository = REPOSITORY
    else:
        local_repository = Path(repository).resolve(strict=True)
        if not local_repository.is_dir():
            raise ValueError("--repository must name a local Git repository")
        source_repository = str(local_repository)
    with tempfile.TemporaryDirectory(prefix="pstack-fetch-") as git_temp:
        git_dir = Path(git_temp) / "repo"
        commit = _fetch(source_repository, ref, git_dir)
        entries = _tree(git_dir, commit)
        blobs = _blobs(git_dir, entries)
        with tempfile.TemporaryDirectory(prefix=".pstack-preview-", dir=output.parent) as stage_temp:
            stage = Path(stage_temp) / "preview"
            shutil.copytree(root, stage, ignore=_copy_ignore, symlinks=True)
            _replace_source(stage, entries, blobs)
            lock = {
                "repository": REPOSITORY,
                "path": UPSTREAM_PATH,
                "commit": commit,
                "version": _version(stage),
                "transform": TRANSFORM,
                "files": snapshot(stage),
            }
            (stage / LOCK_FILE).write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            (stage / PREVIEW_FILE).write_text(json.dumps({
                "base_lock_sha256": hashlib.sha256((root / LOCK_FILE).read_bytes()).hexdigest(),
                "target_commit": commit,
            }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            _build(stage)
            verify_source(stage)
            if output.exists():
                raise ValueError("output appeared while preparing preview")
            stage.rename(output)
    return _report(old, lock, root)


def accept_preview(root: Path | str, preview: Path | str) -> str:
    """Adopt a reviewed preview after rebuilding it with current local adapters."""
    root = Path(root).resolve(strict=True)
    preview_input = Path(preview)
    if preview_input.is_symlink():
        raise ValueError("preview must not be a symlink")
    preview = preview_input.resolve(strict=True)
    if root == preview or root in preview.parents or preview in root.parents:
        raise ValueError("preview must be outside the source tree")
    with _accept_lock(root):
        _recover(root)
        original = verify_source(root)
        target = verify_source(preview)
        try:
            metadata = json.loads((preview / PREVIEW_FILE).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as error:
            raise ValueError("preview metadata is missing or invalid") from error
        if not isinstance(metadata, dict) or set(metadata) != {"base_lock_sha256", "target_commit"}:
            raise ValueError("preview metadata is invalid")
        if metadata["target_commit"] != target["commit"] or metadata["base_lock_sha256"] != hashlib.sha256((root / LOCK_FILE).read_bytes()).hexdigest():
            raise ValueError("preview was made from a different source pin")
        local_before = _local_snapshot(root)
        with tempfile.TemporaryDirectory(prefix=".pstack-accept-", dir=root.parent) as stage_temp:
            stage = Path(stage_temp) / "source"
            shutil.copytree(root, stage, ignore=_copy_ignore, symlinks=True)
            _replace_source_from_preview(stage, preview, target["files"])
            verify_source(stage)
            _build(stage)
            verify_source(stage)
            verify_source(root)
            if _local_snapshot(root) != local_before:
                raise ValueError("local adapters or scripts changed during accept; retry")
            _adopt(root, stage)
        return _report(original, target, root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check, preview, or accept updates to the pinned pstack source.")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="Validate source bytes and modes against upstream.lock.json without network access.")
    check.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent, help="plugins source directory")
    update = commands.add_parser("update", help="Fetch a ref and atomically publish a complete preview in a new directory. Never edits the current source.")
    update.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent, help="plugins source directory")
    update.add_argument("--ref", required=True, help="Upstream branch, tag, or full commit SHA")
    update.add_argument("--output", required=True, type=Path, help="Unused preview directory outside the source tree; parent must exist")
    update.add_argument("--repository", help="Local Git repository for offline testing; omission fetches the pinned public repository")
    accept = commands.add_parser("accept", help="Adopt a reviewed preview after rebuilding with current adapters and scripts.")
    accept.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent, help="plugins source directory")
    accept.add_argument("--preview", required=True, type=Path, help="Previously generated preview directory outside the source tree")
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            lock = verify_source(args.root)
            print(f"PASS source matches {lock['commit']} ({lock['version']})")
        elif args.command == "update":
            print(create_preview(args.root, args.output, args.ref, args.repository))
            print(f"Preview ready at {args.output}")
        else:
            print(accept_preview(args.root, args.preview))
            print(f"Accepted preview from {args.preview}")
    except (OSError, ValueError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
