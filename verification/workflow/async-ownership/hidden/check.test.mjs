import assert from 'node:assert/strict';
import { test } from 'node:test';
import { pathToFileURL } from 'node:url';
import { join } from 'node:path';
const root = process.env.PROJECT_PATH;
const { createLauncher } = await import(pathToFileURL(join(root, 'src/launcher.mjs')));
const { createAttempts } = await import(pathToFileURL(join(root, 'src/attempts.mjs')));
const { createDispatcher } = await import(pathToFileURL(join(root, 'src/dispatcher.mjs')));

function setup() {
  const attempts = createAttempts(), dispatcher = createDispatcher(), created = [], failed = [];
  const launcher = createLauncher({ attempts, dispatcher, onCreated: value => created.push(value), onError: error => failed.push(error) });
  return { attempts, dispatcher, created, failed, launcher };
}

test('real queued callbacks retain ownership after dispatch and across session recreation', { timeout: 2000 }, async () => {
  const { attempts, dispatcher, created, launcher } = setup();
  assert.equal(await launcher.start({ id: 'one' }), 'queued');
  assert.ok(attempts.current(), 'the supplied provider owns the pending operation');
  attempts.recreateSession();
  assert.equal(await launcher.start({ id: 'duplicate' }), 'busy');
  assert.equal(dispatcher.pendingCount(), 1);
  dispatcher.completeNext({ id: 'created-one' });
  assert.deepEqual(created, [{ id: 'created-one' }]);
  assert.equal(attempts.current(), null);
  assert.equal(await launcher.start({ id: 'two' }), 'queued');
});

test('two launchers sharing the provider cannot overlap their operations', { timeout: 2000 }, async () => {
  const { attempts, dispatcher, created, failed, launcher } = setup();
  const other = createLauncher({ attempts, dispatcher, onCreated: value => created.push(value), onError: error => failed.push(error) });
  await launcher.start({ id: 'first' });
  assert.equal(await other.start({ id: 'overlap' }), 'busy');
  assert.equal(dispatcher.pendingCount(), 1);
  dispatcher.completeNext({ id: 'first' });
  assert.equal(await other.start({ id: 'next' }), 'queued');
  dispatcher.completeNext({ id: 'next' });
  assert.deepEqual(created, [{ id: 'first' }, { id: 'next' }]);
});

test('a rejected dispatch settling late cannot release its replacement', { timeout: 2000 }, async () => {
  const { attempts, dispatcher, created, launcher } = setup();
  const failure = new Error('old dispatch rejected');
  dispatcher.rejectNext(failure);
  const old = launcher.start({ id: 'old' });
  const rejected = assert.rejects(old, error => error === failure);
  launcher.cancel();
  const next = launcher.start({ id: 'replacement' });
  const token = attempts.current();
  assert.ok(token);
  await rejected;
  assert.equal(await next, 'queued');
  assert.equal(attempts.current(), token);
  assert.equal(await launcher.start({ id: 'overlap' }), 'busy');
  dispatcher.completeNext({ id: 'replacement' });
  assert.deepEqual(created, [{ id: 'replacement' }]);
});

test('completion failure and rejected dispatch permit recovery', { timeout: 2000 }, async () => {
  const { dispatcher, created, failed, launcher } = setup();
  const failure = new Error('provider unavailable');
  assert.equal(await launcher.start({ id: 'one' }), 'queued');
  dispatcher.failNext(failure);
  assert.deepEqual(failed, [failure]);
  assert.equal(await launcher.start({ id: 'two' }), 'queued');
  dispatcher.completeNext({ id: 'two' });
  dispatcher.rejectNext(failure);
  await assert.rejects(launcher.start({ id: 'three' }), error => error === failure);
  assert.equal(await launcher.start({ id: 'four' }), 'queued');
  dispatcher.completeNext({ id: 'four' });
  assert.deepEqual(created, [{ id: 'two' }, { id: 'four' }]);
});

test('late success and failure cannot settle or notify for a replacement', { timeout: 2000 }, async () => {
  for (const oldOutcome of ['completeNext', 'failNext']) {
    const { attempts, dispatcher, created, failed, launcher } = setup();
    await launcher.start({ id: 'old' });
    launcher.cancel();
    await launcher.start({ id: 'replacement' });
    const replacement = attempts.current();
    dispatcher[oldOutcome](new Error('old result'));
    assert.equal(attempts.current(), replacement);
    assert.equal(await launcher.start({ id: 'duplicate' }), 'busy');
    assert.deepEqual(created, []);
    assert.deepEqual(failed, []);
    dispatcher.completeNext({ id: 'replacement' });
    assert.deepEqual(created, [{ id: 'replacement' }]);
    assert.equal(attempts.current(), null);
  }
});
