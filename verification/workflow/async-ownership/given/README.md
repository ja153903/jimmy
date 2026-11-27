# Queued creation

The public entry is createLauncher in src/launcher.mjs, composed with createAttempts and createDispatcher.

start(input) resolves to "queued" after the dispatcher accepts the request, or "busy" if an operation is already active. Dispatch acceptance is not completion: onComplete or onFailure can run later. A rejected dispatch rejects start and must permit a subsequent attempt.

Exactly one operation may be active. Success calls onCreated once and failure calls onError once, releasing only that operation. cancel() invalidates the active operation and permits another. Late callbacks from a cancelled operation must not affect the replacement, including its ownership or notifications. Recreating the UI session does not cancel the operation.

src/attempts.mjs and src/dispatcher.mjs model the existing local integration. Preserve them unchanged. The dispatcher defaults to queued callbacks; inline mode is a supported fast path.
