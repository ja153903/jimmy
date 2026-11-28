export function createLauncher({ attempts, dispatcher, onCreated, onError }) {
  return {
    async start(input) {
      const token = attempts.begin();
      if (!token) return 'busy';
      try {
        await dispatcher.dispatch(input, {
          onComplete(value) { if (attempts.finish(token)) onCreated(value); },
          onFailure(error) { if (attempts.finish(token)) onError(error); },
        });
        return 'queued';
      } finally {
        attempts.finish(token);
      }
    },
    cancel() { attempts.cancel(); },
  };
}
