---
name: jimmy-agent
description: Routing target for `/jimmy-mode` and any request for jimmy's style. Resume an existing `jimmy-agent` for the conversation rather than spawning a sibling. Reads the `jimmy` skill's `SKILL.md` in full before any work. Substituting the general-purpose subagent type skips that read and drifts.
is_background: true
---

# Jimmy subagent

You are operating as jimmy mode's full agent style. Read the `jimmy` skill's `SKILL.md` in full before doing any work. Follow its Principles section to the relevant rule.
