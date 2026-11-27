import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { runAcceptance } from '../../hidden/run-acceptance.mjs';

process.exit(runAcceptance({
  given: fileURLToPath(new URL('../given', import.meta.url)),
  project: resolve(process.argv[2]),
  editable: ["src/suite.json"],
  checks: fileURLToPath(new URL('./check.test.mjs', import.meta.url)),
}));
