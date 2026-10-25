---
name: interrogate
description: Independently review a concrete risk or provide an explicitly requested adversarial or multi-model review.
disable-model-invocation: true
---

# Interrogate

Identify the intended behavior, review scope, and specific risks. Use the relevant diff and surrounding code. For ordinary work, the lead reviews directly. For a concrete correctness, security, migration, or concurrency risk needing another perspective, default to one independent reviewer and one review round under the task-wide [efficiency budget](../../docs/efficiency.md).

An explicit request for multiple reviewers or models overrides the corresponding default. Use only models and roles the host exposes, honor valid preferences, and disclose unavailable independence or diversity. Do not claim different personas on the same model provide model diversity.

Use the [delegate contract](../../docs/delegation.md). Reviewers get the same intent and relevant evidence, without other reviewers' conclusions. Return actionable findings with locations, failure mechanisms, and evidence; do not require a long rubric dump.

The lead checks findings against the code, merges duplicates, and distinguishes defects, uncertain concerns, and dismissals with reasons. Agreement alone does not prove a finding. Review does not authorize applying changes. When fixes are in scope, verify each fix and recheck affected behavior; do not restart the full panel for a local correction. Report unresolved risks and coverage gaps.
