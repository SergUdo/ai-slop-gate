# 🛡️ ai-slop-gate

⚠️ **Status: Pre-Alpha / Experimental**

*ai-slop-gate is under active development. APIs, behavior, and policies may change without notice. Do NOT rely on this tool for production security decisions yet.*

---

**ai-slop-gate** is an open-source tool designed for automatic analysis of PRs/MRs to detect low-quality AI-generated code ("AI slop"), security vulnerabilities, and style issues. It provides a vendor-agnostic way to maintain code quality in the age of AI-assisted development.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Stage](https://img.shields.io/badge/stage-MVP-blue)


### Run

```
python -m venv .venv
source .venv/bin/activate
pip install -e .
python src/cli.py --policy policy.yaml --mode advisory
```

### Local Usage
To run the analysis manually from your terminal, use the following command:

```
python -m ai_slop_gate.cli --policy policy.yml
```

#### Options Breakdown

* **`-policy`**: Path to your YAML configuration file (e.g., `policy.yml`).
* **`-github-repo`**: The full name of the GitHub repository (e.g., `owner/repo`).
* **`-pr-id`**: The numeric ID of the Pull Request you wish to analyze.


## 📄 License
MIT License © 2025 Vira Udovychenko.

See the [MIT License](LICENSE) file for details.
