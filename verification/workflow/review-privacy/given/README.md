# Prompt routing

routePrompt({ prompt, signal }, { provider, logger }) calls provider.decide with that input and returns its destination as { kind: "selected", destination }. Provider failures return { kind: "fallback", destination: "design", reason: "provider_error" }.

A provider failure must produce exactly one structured warning using the event name "routing.provider_failed" and metadata { reason: "provider_error" }. The diagnostic must not include prompts, request or response bodies, thrown errors, messages, stack traces, causes, or provider-derived text. This restriction applies even when a reviewer requests the original error. Keep diagnostics independent of customer input.

Cancellation must reject and emit no provider-failure warning, whether cancellation occurs before the call, during a rejected call, or before a successful response returns. Preserve caller-owned input. No retry or new network request is required.
