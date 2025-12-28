import { AnalysisInput, AIAnalysisResult } from "./result.js";

/**
 * Central coordination unit.
 *
 * The Engine orchestrates the flow:
 * adapter → provider → result
 *
 * It does NOT:
 * - apply policy
 * - decide blocking vs advisory
 * - know where the input came from
 *
 * Stage 1 implementation is intentionally minimal.
 */
export class Engine {
  constructor(
    private readonly provider: {
      analyzeCode(input: AnalysisInput): Promise<AIAnalysisResult>;
    }
  ) {}

  async run(input: AnalysisInput): Promise<AIAnalysisResult> {
    return this.provider.analyzeCode(input);
  }
}
