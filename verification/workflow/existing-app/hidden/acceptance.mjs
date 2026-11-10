#!/usr/bin/env node
// Usage: node acceptance.mjs <trial dir | candidate notebook.js>
// A trial dir is also checked for a generated verification skill and feature map.
import { spawnSync } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';

const target = resolve(process.argv[2] ?? '');
const isDir = statSync(target).isDirectory();
const cli = isDir ? join(target, 'notebook.js') : target;
const scratch = mkdtempSync(join(tmpdir(), 'notebook-acceptance-'));
let failed = 0;

function check(name, ok, detail = '') {
  if (!ok) failed++;
  console.log(`${ok ? 'PASS' : 'FAIL'} ${name}${ok || !detail ? '' : `: ${detail}`}`);
}

function run(file, ...args) {
  return spawnSync(process.execPath, [cli, ...args], { env: { ...process.env, NOTEBOOK_FILE: file }, encoding: 'utf8' });
}

try {
  const missing = join(scratch, 'missing.json');
  let r = run(missing, 'list');
  check('list on a missing notebook prints nothing', r.status === 0 && r.stdout === '', JSON.stringify(r));

  const empty = join(scratch, 'empty.json');
  writeFileSync(empty, '{\n  "titles": []\n}\n');
  r = run(empty, 'list');
  check('list on an empty notebook prints nothing', r.status === 0 && r.stdout === '', JSON.stringify(r));
  check('list leaves an empty notebook unchanged', readFileSync(empty, 'utf8') === '{\n  "titles": []\n}\n');

  const data = join(scratch, 'data.json');
  const titles = ['Alpha', 'Beta two', 'Gamma'];
  for (const title of titles) check(`add "${title}" exits 0`, run(data, 'add', title).status === 0);
  const stored = JSON.parse(readFileSync(data, 'utf8'));
  check('add stores titles in order', JSON.stringify(stored.titles) === JSON.stringify(titles), JSON.stringify(stored));
  const before = readFileSync(data);
  r = run(data, 'list');
  check('list prints titles in insertion order', r.status === 0 && r.stdout === titles.join('\n') + '\n', JSON.stringify(r.stdout));
  check('list does not modify the data file', readFileSync(data).equals(before));

  r = run(data, '--version');
  check('--version still works', r.status === 0 && r.stdout.trim().length > 0);
} finally {
  rmSync(scratch, { recursive: true, force: true });
}

function findVerifySkills(dir, depth = 0) {
  if (depth > 4) return [];
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    if (!entry.isDirectory() || ['node_modules', '.git'].includes(entry.name)) return [];
    const path = join(dir, entry.name);
    return entry.name.startsWith('verify-') && existsSync(join(path, 'SKILL.md')) && dir.endsWith('skills')
      ? [path]
      : findVerifySkills(path, depth + 1);
  });
}

if (isDir) {
  const skills = findVerifySkills(target);
  check('project verification skill exists under a skills directory', skills.length > 0);
  for (const skill of skills) {
    const body = readFileSync(join(skill, 'SKILL.md'), 'utf8');
    check(`${skill}: has name and description frontmatter`, /^---\n[\s\S]*?name: verify-[\s\S]*?description:[\s\S]*?\n---/.test(body));
    const features = join(skill, 'features');
    check(`${skill}: has features/README.md`, existsSync(join(features, 'README.md')));
    const mapsList = existsSync(features) && readdirSync(features).some((name) => name !== 'README.md' && /\blist\b/.test(readFileSync(join(features, name), 'utf8')));
    check(`${skill}: feature map covers list`, mapsList);
  }
}

console.log(failed ? `REJECTED: ${failed} checks failed` : 'ACCEPTED');
console.log('Artifacts alone are not a workflow pass; grade execution and evidence from the tool record with hidden/rubric.md.');
process.exit(failed ? 1 : 0);
