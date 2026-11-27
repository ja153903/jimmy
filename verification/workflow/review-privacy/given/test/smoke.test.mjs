import assert from 'node:assert/strict';
import { routePrompt } from '../src/routing.mjs';
const input = { prompt: 'A poster', signal: new AbortController().signal };
assert.deepEqual(await routePrompt(input, {
  provider: { async decide(value) { assert.equal(value.prompt, 'A poster'); return 'design'; } },
  logger: { warn() {} },
}), { kind: 'selected', destination: 'design' });
