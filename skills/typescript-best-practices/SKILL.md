---
name: typescript-best-practices
description: TypeScript best practices. Use when reading or editing any .ts or .tsx file.
disable-model-invocation: true
---

# TypeScript best practices

Apply the **type-system-discipline** principle skill first.

| Rule | Summary |
|------|---------|
| Discriminated unions | Model variants with a `kind` literal discriminant so impossible states can't be represented. No optional-field bags. |
| Branded types | Use `& { readonly __brand: "X" }` when it prevents a concrete mix-up. Validate once at the boundary. A brand comes from a verifying type guard (`input is AgentId`), never from `as`. |
| Constructive modeling | Build the shape so the illegal value can't be constructed. Use `[T, ...T[]]` for non-empty lists and `[T, T][]` for even-length lists. |
| Simplest total type | Keep `T[]` while every operation on it stays total. Strengthen to `NonEmpty<T>` only where the loose type forces `!`, a cast, or a "should never happen" throw. |
| `unknown` over `any` | External data is `unknown`. |
| Schemas before guards | Before hand-writing a property-by-property type guard, use the repository's runtime schema library and infer the type from the schema, such as `z.infer`. |
| No `as` casts | Every `as` is a runtime crash waiting. Cast only after validation. |
| Narrowing hierarchy | Discriminant switch > `in` operator > `typeof`/`instanceof` > user-defined type guard > `as`. |
| Type guards | Must verify the claim. A lying guard is worse than `as` because the bug hides behind a name that says it's safe. Name them `isX` or `hasX`. |
| Exhaustiveness | Inline `const _exhaustive: never = x;` in default arms so the compiler errors when a new variant is added. |
| `satisfies` over `as` | Validates the value without widening literal types. |
| Boundary validation | Parse where data crosses in, into a named domain type. `Record<string, unknown>` (however spelled) stops at that parse. Trust types inside. See the **boundary-discipline** principle skill. |
| Readable types | Reuse authoritative schema types. Prefer simple named input and output types when nested utility types or intersections obscure the operation. |
| Arguments | Pass a single clear input directly, as in `getEligibleDestinations(fileTypes)`. Use an object when naming several inputs clarifies the call. |
| Real tests | Don't mock what you can run. Prefer the framework's real test primitives with leak/disposable checks, and verify UI in a running build. Mock only what you can't run locally. |
| Structured telemetry | Prefer structured logger diagnostics with enough context to debug from an id. No `console.log` in shipped code. |

- **Name meaningful work.** Extract a short transformation or other distinct operation when the name helps the reader, even with one caller. Collapse pass-through wrappers.
- **Compose; don't accumulate.** Write each entry point (handler, hook, job, command) as a short orchestrator: read inputs, check gates, and call separately named request, transformation, effect, and telemetry functions. Express transformations as pipelines of small pure functions (`filter(isBillable).map(toRow)`) rather than one loop doing several jobs. Pass helpers the values they need as explicit arguments. Preserve cancellation and error handling across the seams. Validate external data at the boundary. In React, the hook is the orchestrator and keeps the dependency arrays.
- **Keep editable configuration plain.** Use a typed object and a named multiline string for instructions. Add remote configuration, loaders, schemas, or fallbacks when the requested behavior needs them.

See [TypeScript patterns](references/patterns.md) for examples.
