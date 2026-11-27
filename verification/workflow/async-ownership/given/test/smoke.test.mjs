import assert from 'node:assert/strict';
import { createAttempts } from '../src/attempts.mjs';
import { createDispatcher } from '../src/dispatcher.mjs';
import { createLauncher } from '../src/launcher.mjs';

const events = [];
const launcher = createLauncher({
  attempts: createAttempts(), dispatcher: createDispatcher({ inline: true }),
  onCreated: value => events.push(value), onError: error => { throw error; },
});
assert.equal(await launcher.start({ id: 'first' }), 'queued');
assert.deepEqual(events, [{ id: 'first' }]);
assert.equal(await launcher.start({ id: 'second' }), 'queued');
assert.deepEqual(events, [{ id: 'first' }, { id: 'second' }]);
