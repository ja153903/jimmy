# submission-retry

`retry(submission, current)` is this library's public function. It decides whether a pending submission may be retried against the current client state, returning `'retried'` or `'stale'`.

- `submission`: `{ operationId, sessionId, skipped }`, captured when the user submitted.
- `current`: `{ operationId, sessionId }`, the client's state when the retry is attempted.

## Project facts

- Operation IDs survive navigation and reconnection.
- Session IDs can change during the same operation.
- Replacing or skipping an operation invalidates its previous submission.

Run `npm test` for the local checks.
