export function retry(submission, current) {
  if (
    submission.skipped ||
    submission.sessionId !== current.sessionId
  ) return 'stale';

  return 'retried';
}
