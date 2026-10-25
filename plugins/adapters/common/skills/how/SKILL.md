---
name: how
description: Explain code behavior, runtime flow, placement, ownership, or layering from relevant source files.
disable-model-invocation: true
---

# How

Answer directly from relevant source files and tests. Trace the path needed for the question, using targeted search before broad reads. For implementation grounding, keep a short internal summary of ownership, interfaces, and constraints; no separate onboarding report is required.

For a user-facing explanation, describe the behavior and relevant boundaries, cite file locations, and name material gaps. Expand only to the depth the question needs. Reuse established findings while their source remains unchanged.

For a broad investigation with independent questions, use [swarm](../swarm/SKILL.md) only when it repays startup and synthesis. The lead explains the findings; do not spawn a separate explainer.
