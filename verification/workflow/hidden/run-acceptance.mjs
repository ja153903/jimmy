import assert from 'node:assert/strict';
import { cpSync, mkdtempSync, readdirSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, relative } from 'node:path';
import { spawnSync } from 'node:child_process';

function runIsolatedCheck({ project, command, args }) {
  const temporary = mkdtempSync(join(tmpdir(), 'jimmy-acceptance-'));
  try {
    const candidate = join(temporary, 'app');
    cpSync(project, candidate, {
      recursive: true, dereference: true, filter: path => path !== join(project, '.git'),
    });
    const result = spawnSync(command, args, {
      cwd: candidate, env: { ...process.env, PROJECT_PATH: candidate }, encoding: 'utf8', timeout: 15000,
    });
    process.stdout.write(result.stdout || '');
    process.stderr.write(result.stderr || '');
    if (result.error) console.error(result.error.message);
    return result.status === 0 ? 0 : 1;
  } finally {
    rmSync(temporary, { recursive: true, force: true });
  }
}

export function runAcceptance({ given, project, editable, checks }) {
  const editablePaths = new Set(editable);
  for (const entry of readdirSync(given, { recursive: true, withFileTypes: true })) {
    if (!entry.isFile()) continue;
    const path = relative(given, join(entry.parentPath, entry.name));
    if (!editablePaths.has(path)) {
      assert.deepEqual(readFileSync(join(project, path)), readFileSync(join(given, path)),
        `protected fixture file changed: ${path}`);
    }
  }
  for (const [command, args] of [['npm', ['test']], [process.execPath, ['--test', checks]]]) {
    if (runIsolatedCheck({ project, command, args }) !== 0) return 1;
  }
  return 0;
}
