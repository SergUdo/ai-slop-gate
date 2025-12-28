import type { AnalysisInput } from "../../core/result.js";

/**
 * Maps raw GitHub diff into core AnalysisInput.
 * GitHub-specific details go into metadata.
 */
export function mapDiffToAnalysisInput(diff: string): AnalysisInput {
  return {
    content: diff,
    metadata: {
      source: "github"
    }
  };
}

