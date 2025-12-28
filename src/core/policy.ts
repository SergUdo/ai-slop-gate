import type { AnalysisInput } from "./result.js";

/**
 * Policy severity determines how the engine treats violations.
 */
export type PolicySeverity = "pass" | "warn" | "fail";

/**
 * Result of a single policy evaluation.
 */
export interface PolicyResult {
  id: string;
  severity: PolicySeverity;
  message: string;
}

/**
 * Policy contract.
 * Each policy is isolated and stateless.
 */
export interface Policy {
  id: string;
  description: string;
  severity: PolicySeverity;
  evaluate(input: AnalysisInput): PolicyResult | null;
}
