# Repository fit

Read this before persisted code edits. Skip it for read-only work and throwaway prototypes. Resolve only the targets and checks needed for the requested change.

## Build the repository contract

Resolve the likely target files or directories before design. Refresh the contract when the target moves into another package or directory.

1. Find the repository root and the nearest package or build boundary for each target.
2. Use the instructions, manifests, and checks already found for those paths. Search from the repository root through each target directory for scoped instruction files and package configuration. Read the relevant files to determine which rules apply.
3. Read every scoped instruction file from the repository root through the target directory. Include repository contribution guidance when it governs the change. Instructions in sibling directories do not govern the target merely because their code consumes it.
4. Read the formatter, lint, type, generated-code, and build configuration that applies to the target. Take commands from repository documentation or manifests instead of inventing substitutes.
5. Read nearby implementation and verification examples needed to settle local conventions. Reuse examples already read. Record conventions that tools cannot enforce, including naming, imports, error handling, file placement, helper reuse, and verification style.
   Trace the changed dependency to its consumers. When relevant, identify import-time registration and bundle loading, generated catalogs, schema transformations, or compatibility with retained clients. Select the existing consumer check that exposes the risk; do not run every build variant for an unrelated edit.
6. Identify generated, vendored, ownership-sensitive, or forbidden paths before editing.

Record a compact contract with these fields:

- `Targets`. The files or directories the change expects to touch.
- `Instruction sources`. Exact paths in scope order.
- `Package boundary`. The nearest manifest or build root for each target.
- `Local examples`. Exact nearby files whose patterns apply.
- `Required checks`. Exact commands and the directory for each command.
- `Protected paths`. Generated, vendored, forbidden, or ownership-sensitive paths.

Do not create a repository file for an ordinary task. Keep the contract in the task state or worker brief. Save it beside the decision record only when the work is long-running or will resume in another session.

## Resolve conflicts

Follow the runtime's instruction precedence and authorization rules first. When that precedence allows the task to change a repository rule, treat the change as intentional within the task's scope. Among repository signals that do not conflict with higher-authority instructions, use this order:

1. The most specific instruction that applies to the target path.
2. Executable repository configuration and checks.
3. Patterns in nearby maintained code.
4. Jimmy's defaults and general language guidance.

When instructions and executable checks disagree, run the check and report the conflict as unresolved. Do not hide the conflict with a suppression. A passing check does not excuse violating a documented convention that the check cannot express.

## Carry the contract into the work

Put the contract's paths and commands in the implementation todo and every code-writing brief. Do not replace exact paths with a paraphrased style summary. A worker re-resolves the contract for its exact targets because a nested instruction or package boundary may change the rules.

Use existing repository helpers and patterns before introducing Jimmy's preferred structure. Jimmy's principles decide where the repository is silent. They do not justify style churn in unrelated code.

## Pass both completion gates

Functional proof and repository fit answer different questions. Pass both before completion.

1. Exercise the requested behavior on the matching runtime or artifact.
2. Run every applicable required check from the contract, or reuse completed evidence per [verification evidence](verification.md#evidence-records). Prefer checks scoped to touched files or the nearest package unless repository instructions require a broader command.
3. Before calling a broad-check failure pre-existing, reproduce it on the matching pre-change tree with the relevant environment unchanged. A focused check on the edited tree can narrow the affected scope but cannot establish a baseline. If baseline proof is unavailable, report the cause as unresolved.
4. Inspect the final diff for unrelated formatting churn, new suppressions, generated-file edits, and deviations from the recorded local examples.
5. Report each command, working directory, and outcome. Report skipped checks with the concrete reason.

Do not run a formatter over the whole repository unless its instructions require that scope. Do not add ignore directives, broad casts, compatibility code, or generated output only to silence a repository check.

Before running a check, identify the failure it can detect and inspect its command, lifecycle hooks, and prerequisites. If a check needs environment setup, reassess its necessity before installing dependencies, bootstrapping builds, or repairing infrastructure. Run applicable required checks or report their concrete blocker. Optional checks that add no necessary evidence do not expand the task.

Adapted from [figma/jimmy repository fit](https://github.com/figma/jimmy/blob/1a941381334cf8683a4e0814fc759baf0e873852/skills/jimmy/references/repository-fit.md). The package retains the upstream MIT license in [LICENSE](../LICENSE).
