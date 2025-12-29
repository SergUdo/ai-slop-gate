# ai-slop-gate — Stage 1 (canonical state)

## Project structure

~~~
ai-slop-gate/
├─ ai_slop_gate/
│  ├─ __init__.py
│  ├─ cli.py              # entry point
│  ├─ engine.py           # exposes function run_analysis(policy_path, input_text) -> AIAnalysisResult
│  └─ reporters/
│      ├─ __init__.py
│      └─ console.py      # exposes print_result(result), formats output with header/footer
│  └─ ... other modules
~~~

## CLI
- Entry point: `python -m ai_slop_gate.cli`
- Arguments:
  - `--policy` (required)
  - `--mode` (`advisory` or `blocking`, default `advisory`)
  - `--input` (optional, default `"Example input text"`)
- Uses:
  - `run_analysis(policy_path, input_text)` from engine.py
  - `print_result(result)` from console.py
- Output format:

## Engine
- No Engine class; function-based: `run_analysis(policy_path: str, input_text: str) -> AIAnalysisResult`
- Uses:
  - `policy.load_policy`
  - `providers.OpenRouterProvider`
  - returns `AIAnalysisResult`

## Reporters
- Console reporter is function-based (`print_result`)
- Header/footer is printed
- If no issues → `(no issues found)` else → prints `result.summary` and issue details

## Notes
- Stage 1 is fully functional
- CLI can run and print mock analysis
- All imports use package structure (ai_slop_gate.*)
