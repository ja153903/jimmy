# Steer with principle names

Ask Jimmy for a principle by name. For example, “apply Prove It Works to the export” directs Jimmy to the rule for checking the actual export. The 24 references below each cover one decision. Functional Composition also has its own command, `principle-functional-composition`, and Jimmy applies it whenever it writes or reshapes code.

## Steering in practice

Say the agent is about to bolt a new adapter onto three existing ones:

```text
use subtract before you add. delete the obsolete adapters first, then design what's left.
```

Say it claims success because the build passed:

```text
apply prove it works. run the real import flow and show me the written records.
```

Say two parallel attempts are about to write to the same branch:

```text
separate before serializing shared state. give each attempt its own worktree, no locks.
```

Each phrase lands because the rule behind it is specific. The agent still has to say, in its reply, which decision the rule changed. A principle citation with no decision behind it means the agent named the rule without applying it.

## The 25, briefly

The core principles decide how much to build and when to rethink the design:

- [Laziness Protocol](../../skills/jimmy/references/principles/laziness-protocol.md) prefers deletion and the smallest change that solves the problem.
- [Foundational Thinking](../../skills/jimmy/references/principles/foundational-thinking.md) chooses the core data structures before writing logic.
- [Redesign from First Principles](../../skills/jimmy/references/principles/redesign-from-first-principles.md) integrates a new requirement as if it had been there from day one.
- [Attack the Premise](../../skills/jimmy/references/principles/attack-the-premise.md) writes down the premise that two or more failed fixes shared and tests it directly before the next fix.
- [Subtract Before You Add](../../skills/jimmy/references/principles/subtract-before-you-add.md) removes dead weight before building on top of it.
- [Minimize Reader Load](../../skills/jimmy/references/principles/minimize-reader-load.md) collapses layers and hidden state a reader must hold in their head.
- [Functional Composition](../../skills/principle-functional-composition/SKILL.md) builds behavior from small pure functions composed into pipelines, with effects at the edges and entry points as short orchestrators. Jimmy applies it to all code it writes.
- [Outcome-Oriented Execution](../../skills/jimmy/references/principles/outcome-oriented-execution.md) converges rewrites on the target design instead of preserving throwaway compatibility states.
- [Experience First](../../skills/jimmy/references/principles/experience-first.md) chooses the user's result over implementation convenience.
- [Exhaust the Design Space](../../skills/jimmy/references/principles/exhaust-the-design-space.md) builds two or three competing prototypes when there's no precedent.
- [Build the Lever](../../skills/jimmy/references/principles/build-the-lever.md) builds the script that does or proves the work, so a reviewer can rerun it. When an agent keeps doing the same thing by hand, have it write the tool or skill it wishes it had. If a script can do a step the same way every time, use the script, and save agents for the judgment calls.

The architecture principles decide where state, validation, and compatibility live:

- [Model the Domain](../../skills/jimmy/references/principles/model-the-domain.md) encodes repeated rules in one structure, not scattered conditionals.
- [Boundary Discipline](../../skills/jimmy/references/principles/boundary-discipline.md) validates at the boundary and trusts internal types.
- [Type System Discipline](../../skills/jimmy/references/principles/type-system-discipline.md) makes illegal states unrepresentable.
- [Make Operations Idempotent](../../skills/jimmy/references/principles/make-operations-idempotent.md) converges retries on the same end state.
- [Migrate Callers Then Delete Legacy APIs](../../skills/jimmy/references/principles/migrate-callers-then-delete-legacy-apis.md) migrates and deletes in one wave.
- [Separate Before Serializing Shared State](../../skills/jimmy/references/principles/separate-before-serializing-shared-state.md) removes the sharing before adding coordination.

The verification principles define what counts as proof:

- [Prove It Works](../../skills/jimmy/references/principles/prove-it-works.md) verifies the real artifact, not a proxy.
- [Fix Root Causes](../../skills/jimmy/references/principles/fix-root-causes.md) reproduces and traces to the cause before changing code.
- [Sequence Work into Verifiable Units](../../skills/jimmy/references/principles/sequence-verifiable-units.md) ends each small unit in a check before starting the next.
- [Test Behavior, Not Implementation](../../skills/jimmy/references/principles/test-behavior-not-implementation.md) asserts what the code's users can observe, so a test fails when that behavior breaks and survives a change to the internals.
- [Explain the Number](../../skills/jimmy/references/principles/explain-the-number.md) names what limits a measured number and rules out that it measured something else, before anyone trusts or reports it. [`/benchmark-checklist`](../../skills/benchmark-checklist/SKILL.md) turns it into seven questions you answer from real runs.

The delegation principles keep parallel work sane:

- [Guard the Context Window](../../skills/jimmy/references/principles/guard-the-context-window.md) routes bulk reading to subagents and keeps findings in the main chat.
- [Never Block on the Human](../../skills/jimmy/references/principles/never-block-on-the-human.md) proceeds on reversible work and presents the result.

And one meta principle:

- [Encode Lessons in Structure](../../skills/jimmy/references/principles/encode-lessons-in-structure.md) turns advice you've repeated twice into a lint, check, or script. [`/correct`](../../skills/correct/SKILL.md) applies it to a whole repo, as shown in [Make it yours](./09-make-it-yours.md#fix-the-environment-with-correct).

Don't memorize the list. Skim it now, then come back when you catch the agent doing something a name here would have prevented. That's how the vocabulary sticks.

Next: [Make it yours](./09-make-it-yours.md).
