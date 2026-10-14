#!/usr/bin/env python3
"""Preview a three-way pstack update while preserving Jimmy adaptations."""

import argparse
import importlib.util
from pathlib import Path
import subprocess
import tempfile

spec = importlib.util.spec_from_file_location("parity", Path(__file__).with_name("check-pstack-parity.py"))
parity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parity)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="Separate directory for merged resources and conflicts")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("--output must be a new directory")
    for root in (args.base, args.source):
        if not (root / "skills").is_dir() or not (root / "agents").is_dir():
            parser.error(f"Not a pstack snapshot: {root}")
    conflicts = []
    changed = 0
    for directory in ("skills", "agents"):
        for incoming in parity.resource_files(args.source / directory):
            relative = incoming.relative_to(args.source)
            base = args.base / relative
            if base.is_file() and incoming.read_bytes() == base.read_bytes():
                continue
            target = parity.local_path(relative)
            local = parity.PLUGIN / target
            if base.is_file() and local.is_file():
                with tempfile.TemporaryDirectory() as scratch:
                    current = Path(scratch) / "current"
                    current.write_bytes(local.read_bytes())
                    result = subprocess.run(["git", "merge-file", "-p", "-L", str(target), "-L", "pstack-base", "-L", "pstack-latest", str(current), str(base), str(incoming)], capture_output=True)
                if result.returncode < 0 or result.returncode > 127:
                    raise RuntimeError(result.stderr.decode())
                merged = result.stdout
                if result.returncode:
                    conflicts.append(target.as_posix())
            elif local.exists():
                raise ValueError(f"New upstream resource collides with local resource: {target}")
            else:
                merged = incoming.read_bytes()
            output = args.output / target
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(merged)
            output.chmod(incoming.stat().st_mode & 0o777)
            changed += 1
    removed = [p.relative_to(args.base).as_posix() for d in ("skills", "agents") for p in parity.resource_files(args.base / d) if not (args.source / p.relative_to(args.base)).exists()]
    print(f"{changed} updated resources; {len(conflicts)} conflicts; {len(removed)} upstream removals")
    for target in conflicts:
        print(f"CONFLICT {target}")
    for target in removed:
        print(f"REMOVED {target}")
    return bool(conflicts or removed)


if __name__ == "__main__":
    raise SystemExit(main())
