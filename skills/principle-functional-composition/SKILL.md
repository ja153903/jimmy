---
name: principle-functional-composition
description: "Apply whenever writing or reshaping code, in any language. Build behavior from small pure functions composed into pipelines, keep effects at the edges, and write entry points as short orchestrators of reusable modules."
disable-model-invocation: true
---

# Functional Composition

Build behavior by composing small, named, reusable pieces instead of growing one routine that does several jobs. Composition is the default shape for new code; it makes each step testable alone, reusable by the next feature, and readable as the sequence of steps it performs.

- **Pure core, effects at the edges.** Keep transformations pure: inputs in, value out, no hidden reads or writes. Push I/O, mutation, and logging to the entry point that calls them.
- **Entry points orchestrate.** A handler, command, hook, job, or action reads inputs, checks gates, and calls separately named request, transformation, and effect functions. It reads as the steps.
- **Pipelines over multi-job loops.** Express a transformation as a chain of small functions (`filter(isBillable).map(toRow)`, `|>`, iterator adapters). Where the language lacks them, a tiny local `map`/`filter` helper or a loop that does one job is fine.
- **Explicit inputs.** Pass a function the values it needs as arguments. Avoid reaching into module state, globals, or ambient context from inside a transformation.
- **Return new values.** Prefer building and returning data over mutating arguments or shared structures. Mutate locally only when it is contained and measurably cheaper.
- **Modules by responsibility.** Group reusable pieces into a module with a narrow interface, so the next feature imports them instead of copying them. Extract on the second real use, or sooner when the name clarifies the step.

Composition serves the reader; it is not a license to layer. [Minimize Reader Load](../principle-minimize-reader-load/SKILL.md) still applies: no pass-through wrappers, no point-free chains that hide what flows through them. [Laziness Protocol](../principle-laziness-protocol/SKILL.md) still applies: reuse means sharing what exists, not building generic machinery for imagined callers.

For examples of each rule, including Python and React, see [examples](references/examples.md).

**The test:** can each function be described in one sentence and tested without the others, and does the entry point read as the list of steps?
