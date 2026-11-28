import assert from 'node:assert/strict';
import { test } from 'node:test';
import { spawnSync } from 'node:child_process';

test('the real operator command loads both original prompts and individual criteria', () => {
  const result = spawnSync('npm', ['run', '--silent', 'load'], { cwd: process.env.PROJECT_PATH, encoding: 'utf8', timeout: 3000 });
  assert.equal(result.status, 0, result.stderr);
  const cases = JSON.parse(result.stdout);
  assert.deepEqual([...cases].sort((a, b) => a.id.localeCompare(b.id)), [
    { id: 'accessible', prompt: 'Describe the chart', criteria: 'Describe labels and trends without color alone' },
    { id: 'short', prompt: 'Summarize the plan', criteria: 'At most two sentences' },
  ]);
});
