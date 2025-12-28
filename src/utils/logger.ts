/**
 * Minimal logging utility.
 *
 * Exists to avoid direct console usage across the codebase.
 * Will be extended later if structured logging is needed.
 */
export const logger = {
  info: (message: string) => console.log(message),
  error: (message: string) => console.error(message),
};
