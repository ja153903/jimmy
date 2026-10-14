---
name: ketchup
description: Catch the user up on what changed in this chat since their last message, including work completed and decisions waiting on them. Use for ketchup or a quick same-chat catch-up.
---

# Ketchup

Summarize what changed in this chat since the user's last message before this request. Subagent reports and notifications are not user messages. Keep this turn read-only. Check live PR, test, and agent status before reporting them. Name a gap when the available record cannot verify a claim.

Use plain language as in [`bro`](../bro/SKILL.md). Say what the work means for the user before implementation detail. Leave out hashes, file paths, commands, and test counts unless the user needs them to act. Distinguish completed work, work still running, and work you can finish yourself. An action item is a decision or step only the user can take, including any earlier decision still pending. Do not manufacture one to fill the reply.

Keep the response under 150 words. Start with how many things need the user, or say that nothing does. Then state what changed and the next useful step. For each action item, give the recommendation, why it matters, and what happens if they do not answer. Link to any detail the user needs to make the call.

Use a small Mermaid diagram or the available visualization skill when the state is easier to understand as a flow or comparison. Use a screenshot only when one was actually captured. Do not repeat the same fact in prose and a visual. If nothing changed and nothing waits on the user, say so and stop.
