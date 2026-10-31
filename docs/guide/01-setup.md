# Set up Jimmy

Install the repository-root marketplace using the commands in the repository README. Both hosts install the same package; start a new chat after installation and invoke Jimmy using the host's native skill syntax.

No model configuration is required. Delegates inherit the parent model unless the user has explicitly configured a supported override. Use [setup-pstack](../../skills/setup-pstack/SKILL.md) only when choosing model preferences; it checks the current delegation schema and uses an explicitly configured destination.

For app verification, use [create-verification-skill](../../skills/create-verification-skill/SKILL.md). It writes a project skill into the current host's discoverable skill directory and proves its launch/drive/evidence workflow. Existing verification skills can be maintained with [maintain-verification-skill](../../skills/maintain-verification-skill/SKILL.md).

Available tools determine delegation, history access, and future wakeups. Jimmy does not install an execution or automation service.

Next: [Route work through Jimmy](02-jimmy-mode.md).
