from pathlib import Path
import yaml

CONFIG_FILE = ".ai-slop-gate.yml"

DEFAULT_CONFIG = {
    "version": 1,
    "mode": "advisory",
    "providers": ["static", "llm"],
    "reporters": ["stdout"],
    "policy": {
        "ruleset": "default",
    },
}


def run_init(force: bool = False) -> None:
    path = Path(CONFIG_FILE)

    if path.exists() and not force:
        raise SystemExit(
            f"{CONFIG_FILE} already exists. Use --force to overwrite."
        )

    with path.open("w") as f:
        yaml.safe_dump(DEFAULT_CONFIG, f, sort_keys=False)

    print(f"✔ Created {CONFIG_FILE}")
