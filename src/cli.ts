import { Engine } from "./core/engine.js";
import { createProvider } from "./providers/provider.js";
import { createGitHubInput } from "./adapters/github/index.js";
import { ConsoleReporter } from "./reporters/consoleReporter.js";

/**
 * CLI entry point.
 *
 * Wires together adapters, engine, and reporters.
 * No business logic should live here.
 */
async function main() {
  const provider = createProvider();
  const engine = new Engine(provider);
  const reporter = new ConsoleReporter();

  const input = createGitHubInput();
  const result = await engine.run(input);

  reporter.report(result);
}

main();
