#!/usr/bin/env node
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

const VERSION = '1.0.0';
const file = process.env.NOTEBOOK_FILE || join(homedir(), '.notebook.json');

function load() {
  return existsSync(file) ? JSON.parse(readFileSync(file, 'utf8')) : { titles: [] };
}

const [command, ...args] = process.argv.slice(2);

if (command === '--version') {
  console.log(VERSION);
} else if (command === 'add' && args.length === 1 && args[0].trim()) {
  const notebook = load();
  notebook.titles.push(args[0]);
  writeFileSync(file, JSON.stringify(notebook, null, 2) + '\n');
} else if (command === 'list' && args.length === 0) {
  for (const title of load().titles) console.log(title);
} else {
  console.error('usage: notebook add "title" | notebook list | notebook --version');
  process.exit(2);
}
