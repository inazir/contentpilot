/**
 * Generates a short unique id suitable for React list keys
 * and form entity identification.
 * Uses crypto.randomUUID when available (all modern browsers),
 * falls back to Math.random-based approach.
 */
export function uid() {
  if (
    typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
  ) {
    return crypto.randomUUID();
  }
  return (
    Date.now().toString(36) +
    "-" +
    Math.random().toString(36).slice(2, 9)
  );
}
