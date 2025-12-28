import { AnalysisInput, AIAnalysisResult } from "../core/result.js";

/**
 * Provider contract.
 *
 * A provider is responsible for turning AnalysisInput into AIAnalysisResult.
 *
 * Stage 1:
 * - Providers are fake / deterministic
 * - No network calls
 * - No retries or fallbacks
 */
export abstract class BaseProvider {
  abstract analyzeCode(
    input: AnalysisInput
  ): Promise<AIAnalysisResult>;
}
