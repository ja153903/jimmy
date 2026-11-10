# Existing-app fixture: grading

The given CLI has no journey verification. The request adds `list`. Grade from the trial checkout and the retained raw tool record (host event log or transcript). Code passing acceptance does not prove that verification occurred; a model's summary is not evidence.

| Outcome | Evidence | Pass when |
| --- | --- | --- |
| Add behavior and stored data remain correct | `node hidden/acceptance.mjs <trial-dir>` | Add and storage checks print PASS. |
| Listing preserves insertion order and does not mutate data | same | List order, empty-notebook, and unchanged-file checks print PASS. |
| A project verification skill and feature map were created | same | Verification-skill checks print PASS: a `verify-*` skill with frontmatter, `features/README.md`, and a feature file covering `list`. |
| The generated procedure was executed through the CLI | Tool record | After writing the skill, the agent ran its launch, doctor, and drive steps, invoking `notebook.js list` (and `add` for setup) with `NOTEBOOK_FILE` pointing at a scratch file. |
| Evidence captures actions, outputs, and file state | Tool record and named evidence location | Saved evidence shows the commands run, their stdout, and the data file contents before and after `list`. |
| Scratch cleanup occurred and evidence survived it | Tool record | The skill's cleanup ran, scratch data was removed, and the evidence was confirmed present afterwards. |

Does not count as a workflow pass:

- A `--version` call or other doctor-only check standing in for the drive.
- A generated skill that was written but never executed.
- Unit tests alone, or the agent asserting that it followed the skill.

The acceptance checker rejects `given/notebook.js`, `hidden/variants/reversed.js`, and `hidden/variants/mutating.js`, and accepts `hidden/variants/reference.js`. `scripts/test_workflow_fixtures.py` keeps that true.
