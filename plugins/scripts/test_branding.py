import unittest

from branding import brand_source


class BrandingTests(unittest.TestCase):
    def test_names_paths_and_attribution_are_normalized(self):
        files = {
            "jimmy/skills/sample-mode/SKILL.md": (b"Sample mode uses sample-agent and SAMPLE settings.", 0o644),
            "jimmy/agents/sample-agent.md": (b"Read ../skills/sample-mode/SKILL.md", 0o644),
            "jimmy/README.md": (b"i'm [sample](https://x.com/sample). My biography.\n", 0o644),
            "jimmy/skills/sample-mode/tool.sh": (b"#!/bin/sh\nsample-mode\n", 0o755),
            "jimmy/skills/sample-mode/image.bin": (b"\xffsample", 0o644),
        }
        result = brand_source(files)
        self.assertEqual(result["jimmy/skills/jimmy-mode/SKILL.md"], (b"Jimmy mode uses jimmy-agent and JIMMY settings.", 0o644))
        self.assertEqual(result["jimmy/agents/jimmy-agent.md"][0], b"Read ../skills/jimmy-mode/SKILL.md")
        self.assertEqual(result["jimmy/README.md"][0], b"Adapted from pstack by Lauren Tan.\n")
        self.assertEqual(result["jimmy/skills/jimmy-mode/tool.sh"], (b"#!/bin/sh\njimmy-mode\n", 0o755))
        self.assertEqual(result["jimmy/skills/jimmy-mode/image.bin"][0], b"\xffsample")
        self.assertEqual(brand_source(result), result)

    def test_ambiguous_modes_require_review(self):
        files = {
            "jimmy/skills/first-mode/SKILL.md": (b"One", 0o644),
            "jimmy/skills/second-mode/SKILL.md": (b"Two", 0o644),
        }
        with self.assertRaisesRegex(ValueError, "branding review"):
            brand_source(files)


if __name__ == "__main__":
    unittest.main()
