export function retry(submission, current) {
  if (
    submission.skipped ||
    submission.operationId !== current.operationId
  ) return 'stale';

  return 'retried';
}
