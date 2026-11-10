export function retry(submission, current) {
  if (submission.skipped) return 'stale';

  return 'retried';
}
