import { BaseProvider } from "./base.js";
import { AnalysisInput, AIAnalysisResult } from "../core/result.js";

/**
 * Fake Gemini provider.
 *
 * Stage 1 stub implementation used for pipeline validation.
 * This does NOT call any external service.
 */
export class GeminiProvider extends BaseProvider {
  async analyzeCode(input: AnalysisInput): Promise<AIAnalysisResult> {
    return {
      issues: input.content.includes("TODO")
        ? [
            {
              message: "Found TODO comment in code",
              category: "style",
            },
          ]
        : [],
    };
  }
}
