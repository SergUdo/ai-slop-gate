import { readPullRequestDiff } from "./diffReader.js";
import { mapDiffToAnalysisInput } from "./mapper.js";
import type { AnalysisInput } from "../../core/result.js";

/**
 * Entry point for GitHub adapter.
 * Coordinates reading PR diff and mapping it to AnalysisInput.
 * No business logic, no policies, no AI.
 */
export async function analyzeGitHubPullRequest(
  repo: string,
  prNumber: number
): Promise<AnalysisInput> {
  const diff = await readPullRequestDiff(repo, prNumber);
  return mapDiffToAnalysisInput(diff);
}

