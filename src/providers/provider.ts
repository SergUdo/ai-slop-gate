import { BaseProvider } from "./base.js";
import { GeminiProvider } from "./gemini.js";

/**
 * Provider factory.
 *
 * Responsible only for selecting a provider implementation.
 * Configuration logic will be added in later stages.
 */
export function createProvider(): BaseProvider {
  // Stage 1: always return a deterministic provider
  return new GeminiProvider();
}
