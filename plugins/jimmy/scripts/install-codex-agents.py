#!/usr/bin/env python3
"""Install this plugin's agent definitions as Codex custom agents."""

import argparse
import json
import re
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
LEGACY_MODEL_SETTINGS = {
    "sonnet": ("gpt-6-luna", "high"),
    "opus": ("gpt-6-sol", "max"),
    "fable": ("gpt-6-sol", "max"),
}
SUPPORTED_EFFORTS = {
    "gpt-6-luna": ("low", "medium", "high", "xhigh", "max"),
    "gpt-6-sol": ("low", "medium", "high", "xhigh", "max", "ultra"),
}


def parse_agent(path: Path) -> tuple[dict[str, str], str]:
    source = path.read_text()
    if not source.startswith("---\n"):
        raise ValueError(f"Missing frontmatter: {path}")
    try:
        frontmatter, body = source[4:].split("\n---\n", 1)
    except ValueError as error:
        raise ValueError(f"Missing frontmatter terminator: {path}") from error
    fields = {}
    for line in frontmatter.splitlines():
        key, separator, value = line.partition(": ")
        if not separator or key in fields:
            raise ValueError(f"Invalid frontmatter in {path}: {line}")
        fields[key] = value
    for key in ("name", "description"):
        if not fields.get(key):
            raise ValueError(f"Missing {key}: {path}")
    name = fields["name"].lower().replace(" ", "-")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError(f"Invalid agent name: {fields['name']}")
    model = fields.get("model")
    if model in LEGACY_MODEL_SETTINGS:
        model, default_effort = LEGACY_MODEL_SETTINGS[model]
        fields["model"] = model
    else:
        default_effort = None
    effort = fields.get("model_reasoning_effort", fields.get("effort", default_effort))
    if model and model not in SUPPORTED_EFFORTS:
        raise ValueError(f"Unsupported model in {path}: {model}")
    if effort and (not model or effort not in SUPPORTED_EFFORTS[model]):
        raise ValueError(f"Unsupported reasoning effort in {path}: {effort}")
    if model and not effort:
        raise ValueError(f"Missing model_reasoning_effort: {path}")
    if effort:
        fields["model_reasoning_effort"] = effort
    if fields.get("sandbox_mode") not in (None, "read-only"):
        raise ValueError(f"Unsupported sandbox_mode: {path}")
    return fields, body.strip()


def render_agent(
    fields: dict[str, str], body: str, reasoning_effort: str | None = None
) -> str:
    name = fields["name"].lower().replace(" ", "-")
    description = fields["description"]
    lines = [
        f"name = {json.dumps(name)}",
        f"description = {json.dumps(description)}",
    ]
    if model := fields.get("model"):
        effort = reasoning_effort or fields["model_reasoning_effort"]
        if effort not in SUPPORTED_EFFORTS[model]:
            raise ValueError(f"{model} does not support reasoning effort {effort}")
        lines.extend(
            [
                f"model = {json.dumps(model)}",
                f"model_reasoning_effort = {json.dumps(effort)}",
            ]
        )
    if (
        fields.get("sandbox_mode") == "read-only"
        or "disallowedTools" in fields
        or "Read-only" in description
    ):
        lines.append('sandbox_mode = "read-only"')
    lines.append(f"developer_instructions = {json.dumps(body + chr(10))}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "destination",
        type=Path,
        help="Codex agent directory, such as .codex/agents or ~/.codex/agents",
    )
    parser.add_argument(
        "--reasoning-effort",
        choices=tuple(
            dict.fromkeys(
                effort for efforts in SUPPORTED_EFFORTS.values() for effort in efforts
            )
        ),
        help="Override effort for agents with an explicit model. Omit to restore source defaults.",
    )
    args = parser.parse_args()
    destination = args.destination.expanduser()
    agents = {}
    try:
        for source in sorted((PLUGIN_ROOT / "agents").glob("*.md")):
            fields, body = parse_agent(source)
            name = fields["name"].lower().replace(" ", "-")
            if name in agents:
                raise ValueError(f"Duplicate agent name: {name}")
            agents[name] = render_agent(fields, body, args.reasoning_effort)
        if not agents:
            raise ValueError("No Jimmy agent definitions found")
    except ValueError as error:
        parser.error(str(error))
    destination.mkdir(parents=True, exist_ok=True)
    for name, content in agents.items():
        target = destination / f"{name}.toml"
        if not target.exists() or target.read_text() != content:
            target.write_text(content)
        print(target)


if __name__ == "__main__":
    main()
