import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

/**
 * Reads pull request diff using GitHub CLI.
 * This is intentionally simple and synchronous in behavior
 * to keep adapter deterministic and debuggable.
 */
export async function readPullRequestDiff(
  repo: string,
  prNumber: number
): Promise<string> {
  try {
    const { stdout } = await execFileAsync("gh", [
      "pr",
      "diff",
      prNumber.toString(),
      "--repo",
      repo,
    ]);

    if (!stdout || stdout.trim().length === 0) {
      throw new Error("Empty diff received from GitHub");
    }

    return stdout;
  } catch (error) {
    throw new Error(
      `Failed to read PR diff via gh CLI: ${
        error instanceof Error ? error.message : String(error)
      }`
    );
  }
}
