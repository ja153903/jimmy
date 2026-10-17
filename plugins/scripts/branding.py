"""Normalize imported workflow names while retaining upstream attribution."""

import re


TRANSFORM = "jimmy-brand-v1"


def brand_source(files):
    modes = {match.group(1) for path in files if (match := re.fullmatch(r"jimmy/skills/([^/]+)-mode/SKILL\.md", path))}
    if len(modes) > 1:
        raise ValueError("multiple upstream mode names require a branding review")
    if not modes or modes == {"jimmy"}:
        return files
    original = modes.pop()
    pattern = re.compile(re.escape(original), re.IGNORECASE)

    def replacement(match):
        word = match.group()
        return "JIMMY" if word.isupper() else "Jimmy" if word[0].isupper() else "jimmy"

    branded = {}
    for path, (data, mode) in files.items():
        target = pattern.sub(replacement, path)
        if target in branded:
            raise ValueError(f"branding path collision: {target}")
        if path == "jimmy/LICENSE":
            branded[target] = (data, mode)
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            branded[target] = (data, mode)
            continue
        text = re.sub(r"(?m)^i'm \[" + re.escape(original) + r"\]\(https://x\.com/[^)]+\).*?$", "Adapted from pstack by Lauren Tan.", text)
        text = pattern.sub(replacement, text)
        branded[target] = (text.encode("utf-8"), mode)
    return branded
