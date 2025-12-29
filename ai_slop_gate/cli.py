import argparse

from ai_slop_gate.engine import run_analysis
from ai_slop_gate.reporters.console import print_result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ai-slop-gate — detect low-quality AI-generated code"
    )

    parser.add_argument(
        "--policy",
        required=True,
        help="Path to policy.yaml file",
    )

    parser.add_argument(
        "--mode",
        choices=["advisory", "blocking"],
        default="advisory",
        help="Run mode (default: advisory)",
    )

    parser.add_argument(
        "--input",
        required=False,
        default="Example input text",
        help="Input text or code to analyze",
    )

    args = parser.parse_args()

    # Використовуємо функцію run_analysis напряму
    result = run_analysis(policy_path=args.policy, input_text=args.input)

    # Вивід результату
    print_result(result)


if __name__ == "__main__":
    main()
