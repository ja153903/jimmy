export async function routePrompt(input, { provider, logger }) {
  input.signal.throwIfAborted();
  try {
    const destination = await provider.decide(input);
    input.signal.throwIfAborted();
    return { kind: 'selected', destination };
  } catch (error) {
    input.signal.throwIfAborted();
    return { kind: 'fallback', destination: 'design', reason: 'provider_error' };
  }
}
