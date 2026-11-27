export function loadSuite(definition) {
  if (definition.kind !== 'unified' || definition.judge !== 'rubric' || !Array.isArray(definition.cases)) {
    throw new Error('unsupported suite');
  }
  return definition.cases.map(item => {
    if (Object.hasOwn(item, 'judge')) throw new Error('unified cases cannot declare a judge');
    if (typeof item.id !== 'string' || typeof item.prompt !== 'string') throw new Error('invalid case');
    return { id: item.id, prompt: item.prompt, criteria: item.injectedContents?.criteria ?? 'Be useful' };
  });
}
