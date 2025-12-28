import { AnalysisInput } from "../../core/result.js";

/**
 * GitHub adapter.
 *
 * Converts GitHub-specific context into a generic AnalysisInput.
 *
 * Stage 1:
 * - No GitHub API
 * - No filesystem access
 * - Deterministic fake payload
 */
export function createGitHubInput(): AnalysisInput {
  return {
    content: "// TODO: refactor this function",
    metadata: {
      source: "github",
    },
  };
}
