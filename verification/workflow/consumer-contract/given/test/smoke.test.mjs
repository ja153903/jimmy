import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const definition = JSON.parse(readFileSync(new URL('../src/suite.json', import.meta.url), 'utf8'));
assert.equal(definition.kind, 'unified');
assert.deepEqual(definition.cases.map(item => item.id), ['short', 'accessible']);
