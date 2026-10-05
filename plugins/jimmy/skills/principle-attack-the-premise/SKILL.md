---
name: principle-attack-the-premise
description: "Apply when two or more fixes that share one premise have failed the same gate. Question the shared premise before another fix. For imbalance between actors, take a census to find which actors hold it."
---

# Attack the Premise

When two or more fixes that share one premise have failed the same gate, suspect the premise, not the fixes.

**Why:** Each failure under a shared premise is evidence about the premise.

**Pattern:**
- **Write the premise down.** The premise is the one sentence that every failed fix assumed.
- **Test the premise directly.** Name an observation that would disprove it. Build the smallest rerunnable probe per [Build the Lever](../principle-build-the-lever/SKILL.md). Do not write another fix that assumes the premise before checking that observation.
- **Take a census when actors exist.** For an imbalance between threads, processes, queues, workers, or other actors, count it per actor before the next fix. Record both the total and its distribution.
- **Read the skew.** If the same few actors hold most of the imbalance on every run, investigate what assigns them that role. The assignment is the next "why" per [Fix Root Causes](../principle-fix-root-causes/SKILL.md).
- **Remove a proven asymmetry before compensating for it**, per the [Laziness Protocol](../principle-laziness-protocol/SKILL.md). Compare rotating, randomizing, or moving the role with return paths, shared pools, batched hand-offs, or periodic rebalances. Prefer the change that removes the cause with less work, and verify that it preserves required behavior.

**Stop:**
- Do not start the next fix before the premise is written down and the probe exists. When the problem involves actor imbalance, the census is part of that probe.
- An even census rules out the suspected skew. It does not prove every shared premise correct. Keep the result as evidence and test the next explanation.

This principle is distinct from [Redesign from First Principles](../principle-redesign-from-first-principles/SKILL.md), which rebuilds a design around a new requirement. It questions a fact the current design assumes.
