/**
 * Core analysis contracts.
 *
 * This file defines the canonical data structures used across the system.
 * Everything else (providers, adapters, reporters) must conform to these types.
 *
 * Stage 1:
 * - No policy evaluation
 * - No severity escalation
 * - Deterministic structure
 */

export interface AnalysisInput {
  /** Raw code or content to be analyzed */
  content: string;

  /** Optional metadata (file name, source, etc.) */
  metadata?: Record<string, unknown>;
}

export interface AnalysisIssue {
  /** Human-readable description of the issue */
  message: string;

  /** Logical category of the issue */
  category: string;
}

export interface AIAnalysisResult {
  /** List of detected issues */
  issues: AnalysisIssue[];
}
