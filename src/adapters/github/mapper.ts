import type { AnalysisInput } from "../../core/result.js";

/**
 * Maps raw git diff into AnalysisInput.
 * At this stage we keep it raw and un-opinionated.
 * Any interpretation belongs to analyzers, not adapters.
 */
export function mapDiffToAnalysisInput(diff: string): AnalysisInput {
  return {
    source: "github",
    content: diff,
    metadata: {
      format: "git-diff",
    },
  };
}
