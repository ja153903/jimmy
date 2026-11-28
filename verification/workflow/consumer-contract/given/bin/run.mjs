import { readFileSync } from 'node:fs';
import { loadSuite } from '../src/loader.mjs';
const definition = JSON.parse(readFileSync(new URL('../src/suite.json', import.meta.url), 'utf8'));
console.log(JSON.stringify(loadSuite(definition)));
