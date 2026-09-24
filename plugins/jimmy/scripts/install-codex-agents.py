#!/usr/bin/env python3
"""Install this plugin's agent definitions as Codex custom agents."""

import argparse
import json
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MODEL_SETTINGS = {
    "sonnet": ("gpt-6-luna", "high"),
    "opus": ("gpt-6-sol", "max"),
    "fable": ("gpt-6-sol", "max"),
}


def parse_agent(path: Path) -> tuple[dict[str, str], str]:
    source = path.read_text()
    if not source.startswith("---\n"):
        raise ValueError(f"Missing frontmatter: {path}")
    frontmatter, body = source[4:].split("\n---\n", 1)
    fields = {}
    for line in frontmatter.splitlines():
        key, separator, value = line.partition(": ")
        if not separator:
            raise ValueError(f"Invalid frontmatter in {path}: {line}")
        fields[key] = value
    return fields, body.strip()


def render_agent(fields: dict[str, str], body: str) -> str:
    name = fields["name"].lower().replace(" ", "-")
    description = fields["description"]
    if name == "jimmy-agent":
        description = "Jimmy workflow specialist. Use when a delegated task should follow the installed jimmy skill."
        body = (
            "Read the installed jimmy skill in full before doing any work, "
            "including its Principles section. Follow its applicable playbook "
            "and leaf principles."
        )
    lines = [
        f"name = {json.dumps(name)}",
        f"description = {json.dumps(description)}",
    ]
    if model := fields.get("model"):
        codex_model, effort = MODEL_SETTINGS[model]
        lines.extend(
            [
                f"model = {json.dumps(codex_model)}",
                f"model_reasoning_effort = {json.dumps(effort)}",
            ]
        )
    if "disallowedTools" in fields or "Read-only" in description:
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
    args = parser.parse_args()
    destination = args.destination.expanduser()
    destination.mkdir(parents=True, exist_ok=True)
    for source in sorted((PLUGIN_ROOT / "agents").glob("*.md")):
        fields, body = parse_agent(source)
        name = fields["name"].lower().replace(" ", "-")
        target = destination / f"{name}.toml"
        target.write_text(render_agent(fields, body))
        print(target)


if __name__ == "__main__":
    main()
