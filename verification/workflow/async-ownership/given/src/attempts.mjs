export function createAttempts() {
  let active = null;
  let nextId = 0;
  let session = 0;
  return {
    begin() {
      if (active) return null;
      active = Object.freeze({ id: ++nextId });
      return active;
    },
    finish(token) {
      if (active !== token) return false;
      active = null;
      return true;
    },
    cancel() { active = null; },
    recreateSession() { session++; },
    current() { return active; },
    session() { return session; },
  };
}
