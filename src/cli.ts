import { Engine } from "./core/engine.js";
import { ConsoleReporter } from "./reporters/consoleReporter.js";
import { createGitHubInput } from "./adapters/github/index.js";
import { DummyProvider } from "./providers/dummy.js";
import { logger } from "./utils/logger.js";

async function main(): Promise<void> {
  try {
    const provider = new DummyProvider();
    const engine = new Engine(provider);
    const reporter = new ConsoleReporter();

    const input = await createGitHubInput();
    const result = await engine.run(input);

    await reporter.report(result);
  } catch {
    logger.error("ai-slop-gate failed");
    process.exit(1);
  }
}

main();
