# Word the request

A useful request states the outcome and a check that can pass or fail. Jimmy's playbook supplies the steps. Add relevant context and constraints without prescribing a sequence the agent may need to revise.

Include the symptom or goal, a concrete done check, evidence to show, and what the user already knows. For example, a report can include a reproduction step, log, issue, or branch. A constraint such as "read-only investigation" or "review before implementing" changes the workflow and belongs in the request.

Keep a suspected cause separate from the observed symptom. Ask [`in-your-own-words`](../../in-your-own-words/SKILL.md) to restate a noisy report when a misreading would be costly. Use [`recall`](../../recall/SKILL.md) to recover relevant recent work in a fresh chat. For unfamiliar code, [`how`](../../how/SKILL.md) traces behavior and [`why`](../../why/SKILL.md) investigates the reasons behind it.

For design work, ask for a prototype when observation can settle a choice. Ask for an architectural sketch when ownership, interfaces, or shared state are unclear. A plan is useful after the design is settled. Each plan step should end with a check.

For a long run, give a done predicate that the agent can test, a base branch or worktree requirement if one matters, and the gates that still need your review. Ask for a decision trail when you will review the work later. Codex can keep working in the current task; recurring work requires a scheduler available in the session.

A short follow-up such as "continue" or "keep going until the checks pass" is enough when this chat contains the task. Say "new task" when the subject changes. To correct drift, restate the goal and the observed mismatch. Ask for real output or an exercised user path when the agent reports only that the build passes.
