import type { AnalysisInput } from "./result.js";
import type { Policy, PolicyResult, PolicySeverity } from "./policy.js";

/**
 * Aggregated policy evaluation result.
 */
export interface PolicyEngineResult {
  status: PolicySeverity;
  results: PolicyResult[];
}

/**
 * Runs all policies and determines final status.
 *
 * Rules:
 * - any "fail" → fail
 * - otherwise any "warn" → warn
 * - otherwise → pass
 */
export function runPolicies(
  input: AnalysisInput,
  policies: Policy[]
): PolicyEngineResult {
  const results: PolicyResult[] = [];

  for (const policy of policies) {
    const result = policy.evaluate(input);
    if (result) {
      results.push(result);
    }
  }

  const status = deriveStatus(results);

  return {
    status,
    results,
  };
}

function deriveStatus(results: PolicyResult[]): PolicySeverity {
  if (results.some(r => r.severity === "fail")) {
    return "fail";
  }

  if (results.some(r => r.severity === "warn")) {
    return "warn";
  }

  return "pass";
}
