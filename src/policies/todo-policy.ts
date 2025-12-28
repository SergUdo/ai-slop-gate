import type { Policy } from "../core/policy.js";

/**
 * Detects TODO comments in code.
 * This is intentionally naive and deterministic.
 */
export const todoPolicy: Policy = {
  id: "todo-comment",
  description: "Detect TODO comments in code",
  severity: "warn",

  evaluate(input) {
    if (!input.content.includes("TODO")) {
      return null;
    }

    return {
      id: this.id,
      severity: this.severity,
      message: "Found TODO comment in code",
    };
  },
};
