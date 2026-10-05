---
name: principle-test-behavior-not-implementation
description: "Apply when you write, change, or keep a test. Exercise the public behavior and assert a concrete expected result or observable effect. Check that a plausible defect makes the test fail."
---

# Test Behavior, Not Implementation

A test calls the code the way its users do and asserts a concrete expected result or observable effect. Prefer literal expected values that make the contract visible. Internal call order and copied constants usually test implementation choices instead of that contract.

Before keeping a test, name the defect it catches. When returning `undefined` would violate the contract, check that this mutation makes the test fail. Also consider a wrong payload, omitted side effect, invalid accepted input, or unexpected success. A legitimate absence or error test needs a mutation suited to its contract.

**Why:** A test that cannot fail for a relevant defect costs CI time and review attention without protecting behavior. A copied constant or prompt string often blocks an edit without checking its effect.

**Five shapes to inspect:**

- **Weak or no assertion.** No assertion, or an assertion that establishes only presence or broad shape when the contract specifies more. `toBeDefined`, `toBeTruthy`, `toBeInstanceOf`, and `toBeGreaterThan(0)` can fail on `undefined`. That does not make them sufficient for every contract.
- **Mock or absence only.** A bare call count or an absence check can miss a wrong payload or the wrong branch. Keep valid absence and error tests when they exercise the relevant public path and distinguish a plausible defect. The matcher alone does not decide their value.
- **Self-referential.** The expected value comes from the code under test: `expect(f(a)).toBe(f(a))`, `expect(parsed.url).toBe(buildUrl(...))`.
- **Constant pin.** The assertion restates a hand-maintained constant, config default, table row, or prompt string: `expect(LIMITS.maxTools).toBe(8)`, `expect(PROMPT).toContain("You are")`.
- **Fixture asserts fixture.** The assertion reads data the test built or a value computed in `beforeEach`, and the subject never runs inside the body.

**The fix:** call the subject with one concrete input and assert the literal output or observable effect, such as `expect(slugify("Hello, World!")).toBe("hello-world")`. For absence, cover the contrasting presence case where it is part of the contract. Separate tests are fine. For errors, verify the expected error and relevant side effects. For a constant, test the mechanism that reads it. For a mock at an external boundary, assert the payload or resulting state. Rewrite or delete a test only after checking which behavior it protects.

**Keep** a test of a relation across a table's rows (a key present in two tables, a parent that exists), and a compile-time check in a `*.test-d.ts` file.
