### Authoring or modifying a skill

Use an available host skill creator. Keep the entrypoint concise and move conditional detail into linked references. Preserve the user's scope and existing invocation policy. Change adapters for imported workflows rather than modifying the pinned source.

Validate frontmatter and links, inspect the generated skill, and exercise realistic requests when the change affects routing or behavior. Package checks alone do not establish behavioral correctness. A focused independent forward-test can be justified within the shared [budget](../../../docs/efficiency.md); give it the request and relevant artifacts without the intended answer.

Use [Opening a PR](opening-a-pr.md) when PR delivery is in scope. Report changed decisions, validation evidence, and untested behavior.
