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
  /** Source content to be analyzed (file, diff, snippet, etc.) */
  content: string;

  /**
   * Optional contextual metadata.
   * Used by adapters and policies, ignored by core engine.
   */
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
