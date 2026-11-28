export function createDispatcher({ inline = false } = {}) {
  const pending = [];
  let rejection = null;
  return {
    async dispatch(input, callbacks) {
      if (rejection) {
        const error = rejection;
        rejection = null;
        throw error;
      }
      if (inline) callbacks.onComplete({ id: input.id });
      else pending.push({ input, callbacks });
    },
    rejectNext(error) { rejection = error; },
    completeNext(value) { pending.shift().callbacks.onComplete(value); },
    failNext(error) { pending.shift().callbacks.onFailure(error); },
    pendingCount() { return pending.length; },
  };
}
