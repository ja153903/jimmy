---
name: interrogate
description: Independently review a concrete risk or provide an explicitly requested adversarial or multi-model review.
disable-model-invocation: true
---

# Interrogate

Identify the intended behavior, review scope, and specific risks. Use the relevant diff and surrounding code. For ordinary work, the lead reviews directly. For a concrete correctness, security, migration, or concurrency risk needing another perspective, default to one independent reviewer and one review round under the task-wide [efficiency budget](../../docs/efficiency.md).

An explicit request for multiple reviewers or models overrides the corresponding default. Use only models and roles the host exposes, honor valid preferences, and disclose unavailable independence or diversity. Do not claim different personas on the same model provide model diversity.

Use the [delegate contract](../../docs/delegation.md). Reviewers get the same intent and relevant evidence, without other reviewers' conclusions. Give each reviewer an isolated checkout matching the review scope, including relevant uncommitted changes. Reproduction tests and probes belong there; reviewers do not edit the user's checkout or apply fixes. If isolation is unavailable, use non-mutating checks and disclose the coverage limit.

Ask reviewers to break the intended behavior with the real code. Each defect needs a location, a failure mechanism, the exact reproduction command, observed output, and expected behavior. For a design, use a small prototype or probe of the current code. A shipped documentation defect can instead cite the incorrect line and the behavior or contract that disproves it. Style preferences and speculative future failures are not verified defects.

The lead reruns each executable reproduction against the reviewed input state, checks that it breaks the intent, and merges findings with the same root cause. Agreement alone does not prove a finding. Keep an unrun but material security, migration, or concurrency concern visible as an unresolved risk with the missing evidence; do not present it as verified or silently discard it. Distinguish verified defects, unresolved risks, and dropped findings with reasons. Say "no verified findings" when appropriate, with coverage limits.

Review does not authorize applying changes. When fixes are in scope, verify each fix and recheck affected behavior; do not restart the full panel for a local correction.
