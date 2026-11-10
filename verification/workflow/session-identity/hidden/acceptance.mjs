#!/usr/bin/env node
// Usage: node acceptance.mjs <candidate retry.js or project dir>
import { statSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const target = resolve(process.argv[2] ?? '');
const file = statSync(target).isDirectory() ? join(target, 'retry.js') : target;
const { retry } = await import(pathToFileURL(file).href);

const cases = [
  ['same operation across a session change retries', { operationId: 'op1', sessionId: 's1', skipped: false }, { operationId: 'op1', sessionId: 's2' }, 'retried'],
  ['same operation in the same session retries', { operationId: 'op1', sessionId: 's1', skipped: false }, { operationId: 'op1', sessionId: 's1' }, 'retried'],
  ['replaced operation in the same session is stale', { operationId: 'op1', sessionId: 's1', skipped: false }, { operationId: 'op2', sessionId: 's1' }, 'stale'],
  ['replaced operation across a session change is stale', { operationId: 'op1', sessionId: 's1', skipped: false }, { operationId: 'op2', sessionId: 's2' }, 'stale'],
  ['skipped submission in the same session is stale', { operationId: 'op1', sessionId: 's1', skipped: true }, { operationId: 'op1', sessionId: 's1' }, 'stale'],
  ['skipped submission across a session change is stale', { operationId: 'op1', sessionId: 's1', skipped: true }, { operationId: 'op1', sessionId: 's2' }, 'stale'],
];

let failed = 0;
for (const [name, submission, current, expected] of cases) {
  const actual = retry(submission, current);
  const ok = actual === expected;
  if (!ok) failed++;
  console.log(`${ok ? 'PASS' : 'FAIL'} ${name}: expected ${expected}, got ${actual}`);
}
console.log(failed ? `REJECTED: ${failed} of ${cases.length} cases failed` : `ACCEPTED: ${cases.length} cases`);
process.exit(failed ? 1 : 0);
