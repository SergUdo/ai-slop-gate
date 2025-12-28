import { AIAnalysisResult } from "../core/result.js";

/**
 * Console reporter.
 *
 * Responsible for presenting analysis results to stdout.
 *
 * Stage 1:
 * - No policy interpretation
 * - No exit code logic
 */
export class ConsoleReporter {
  report(result: AIAnalysisResult): void {
    console.log("=== ai-slop-gate report ===");

    if (result.issues.length === 0) {
      console.log("No issues detected.");
    }

    result.issues.forEach((issue, index) => {
      console.log(`${index + 1}. ${issue.message}`);
    });

    console.log("=== end of report ===");
  }
}

