## ai-slop gate

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
python -m ai_slop_gate.cli --policy <path_to_policy> --github-repo <owner/repo> --pr-id <pull_request_number>
```

#### Options Breakdown

* **`-policy`**: Path to your YAML configuration file (e.g., `policy.yml`).
* **`-github-repo`**: The full name of the GitHub repository (e.g., `owner/repo`).
* **`-pr-id`**: The numeric ID of the Pull Request you wish to analyze.

#### Example

```
python -m ai_slop_gate.cli --policy policy.yml --github-repo zaproxy/zaproxy --pr-id 13407
```
