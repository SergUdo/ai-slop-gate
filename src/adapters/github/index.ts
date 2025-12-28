import { readPullRequestDiff } from "./diffReader.js";
import { mapDiffToAnalysisInput } from "./mapper.js";
import type { AnalysisInput } from "../../core/result.js";

/**
 * High-level GitHub adapter entry point.
 * Used by CLI to produce AnalysisInput from GitHub PR context.
 */
export async function createGitHubInput(): Promise<AnalysisInput> {
  const diff = await readPullRequestDiff();
  return mapDiffToAnalysisInput(diff);
}


