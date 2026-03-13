# Refactor ai-slop-gate to Separate Compliance Checking from Analysis

## Problem/Feature Description

A DevOps lead is doing a code review of ai-slop-gate and has flagged several architectural concerns. The current codebase draft they received mixes compliance checking directly into the PolicyEngine, prints results from within the engine, and has the CLI making direct policy decisions rather than just parsing arguments and wiring components together. The lead wants a clear separation of concerns before the project ships to enterprise customers with strict audit requirements.

You have been asked to write a refactoring proposal and produce a cleaned-up code example that demonstrates the correct architectural boundaries. The enterprise customers include EU-based clients who need GDPR compliance checks (forbidden licenses, secret detection, data residency) and they want to control compliance via a config flag.

Your output should demonstrate how the system should be structured and where each concern belongs. Focus on correctness of architecture rather than a fully runnable implementation.

## Output Specification

Produce the following files:

- `architecture_review.md` — a document (400–600 words) identifying the architectural violations in the draft below and explaining the correct structure. Cover: where compliance checking belongs in the execution flow, what the engine must NOT do, what the CLI must NOT do, what compliance profiles exist and how they are enabled, and what the exit code contract is.
- `refactored_example.py` — a Python file showing a corrected outline of the execution pipeline (CLI wiring, engine call, compliance sidecar call, reporter call, exit code logic) with inline comments explaining each layer's responsibility. Stub functions are fine; the code does not need to run.

## Input Files

The following draft code is provided for review. Extract it before beginning.

=============== FILE: draft_pipeline.py ===============
# DRAFT — contains architectural issues for review
import sys

def run_analysis(args):
    # Load policy
    policy = load_policy(args.policy_file)

    # Run providers
    observations = []
    for provider_name in args.providers:
        provider = get_provider(provider_name)
        obs = provider.analyze(args.path)
        observations.extend(obs.observations)

        # Compliance: check licenses inline with provider results
        if "gpl" in obs.raw_text.lower() or "agpl" in obs.raw_text.lower():
            print("COMPLIANCE VIOLATION: forbidden license detected")
            sys.exit(1)

    # Policy engine also handles printing and exit
    engine = PolicyEngine()
    decision = engine.evaluate(observations, policy)
    print(f"Decision: {decision.mode}")

    # Check secrets inside engine
    if any(o.category == "secret" for o in observations):
        engine._print_secret_warning()
        sys.exit(1)

    # Exit based on mode
    if decision.mode == "blocking":
        sys.exit(1)
    else:
        sys.exit(0)
=============== END FILE ===============
