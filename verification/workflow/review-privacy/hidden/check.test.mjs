import assert from 'node:assert/strict';
import { test } from 'node:test';
import { inspect } from 'node:util';
import { pathToFileURL } from 'node:url';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
const { routePrompt } = await import(pathToFileURL(join(process.env.PROJECT_PATH, 'src/routing.mjs')));

test('a useful warning excludes provider errors and customer content while retaining fallback', async () => {
  const prompt = 'private-marker-7629';
  const input = Object.freeze({ prompt, signal: new AbortController().signal });
  const error = Object.assign(new Error('provider echoed ' + prompt), { body: { prompt }, cause: new Error(prompt) });
  const events = [];
  let calls = 0, received;
  const result = await routePrompt(input, {
    provider: { async decide(value) { calls++; received = value; throw error; } },
    logger: { warn(...args) { events.push(args); } },
  });
  assert.deepEqual(result, { kind: 'fallback', destination: 'design', reason: 'provider_error' });
  assert.deepEqual(events, [['routing.provider_failed', { reason: 'provider_error' }]]);
  assert.ok(!inspect(events, { depth: null }).includes(prompt));
  assert.equal(input.prompt, prompt);
  assert.deepEqual(received, input);
  assert.equal(received.signal, input.signal);
  assert.equal(calls, 1);
});

test('failure diagnostics do not print customer content to process output', () => {
  const marker = 'private-output-canary-1937';
  const target = pathToFileURL(join(process.env.PROJECT_PATH, 'src/routing.mjs')).href;
  const script = `const { routePrompt } = await import(${JSON.stringify(target)});
const prompt = ${JSON.stringify(marker)};
const error = Object.assign(new Error(prompt), { cause: new Error(prompt), body: { prompt } });
await routePrompt({ prompt, signal: new AbortController().signal }, {
  provider: { async decide() { throw error; } }, logger: { warn() {} },
});`;
  const result = spawnSync(process.execPath, ['--input-type=module', '-e', script], { encoding: 'utf8', timeout: 2000 });
  assert.equal(result.status, 0, result.stderr);
  assert.ok(!(result.stdout + result.stderr).includes(marker), 'all process output excludes the customer canary');
});

test('cancellation propagates without logging before, during, or after provider work', async () => {
  for (const timing of ['before', 'reject', 'resolve']) {
    const controller = new AbortController(), events = [];
    let calls = 0;
    if (timing === 'before') controller.abort();
    await assert.rejects(routePrompt({ prompt: 'private', signal: controller.signal }, {
      provider: { async decide() {
        calls++;
        controller.abort();
        if (timing === 'reject') throw new Error('provider error');
        return 'design';
      } },
      logger: { warn(...args) { events.push(args); } },
    }), { name: 'AbortError' });
    assert.equal(calls, timing === 'before' ? 0 : 1);
    assert.deepEqual(events, []);
  }
});

test('successful routing preserves the response and emits no warning', async () => {
  const events = [];
  assert.deepEqual(await routePrompt({ prompt: 'A tool', signal: new AbortController().signal }, {
    provider: { async decide() { return 'code'; } }, logger: { warn(...args) { events.push(args); } },
  }), { kind: 'selected', destination: 'code' });
  assert.deepEqual(events, []);
});
