from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Mapping


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = ROOT / ".env"
DEFAULT_CONFIG_FILE = Path.home() / ".openviking" / "ov.conf"

DEFAULTS = {
    "OPENVIKING_WORKSPACE": str(Path.home() / ".openviking" / "data"),
    "OPENVIKING_EMBEDDING_PROVIDER": "openai",
    "OPENVIKING_EMBEDDING_MODEL": "text-embedding-3-small",
    "OPENVIKING_EMBEDDING_DIMENSION": "1536",
    "OPENVIKING_EMBEDDING_API_BASE": "https://api.openai.com/v1",
}


def load_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def merged_env(dotenv_values: Mapping[str, str]) -> dict[str, str]:
    values = dict(DEFAULTS)
    values.update(dotenv_values)

    for key in DEFAULTS:
        if os.environ.get(key):
            values[key] = os.environ[key]
    if os.environ.get("OPENAI_API_KEY"):
        values["OPENAI_API_KEY"] = os.environ["OPENAI_API_KEY"]

    return values


def require_openai_api_key(values: Mapping[str, str]) -> str:
    api_key = values.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required. Add it to .env first.")
    return api_key


def build_openviking_config(values: Mapping[str, str]) -> dict[str, object]:
    api_key = require_openai_api_key(values)
    embedding_dimension = int(values["OPENVIKING_EMBEDDING_DIMENSION"])

    return {
        "storage": {
            "workspace": values["OPENVIKING_WORKSPACE"],
        },
        "embedding": {
            "dense": {
                "provider": values["OPENVIKING_EMBEDDING_PROVIDER"],
                "model": values["OPENVIKING_EMBEDDING_MODEL"],
                "api_key": api_key,
                "api_base": values["OPENVIKING_EMBEDDING_API_BASE"],
                "dimension": embedding_dimension,
            },
        },
    }


def write_config(config: Mapping[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a local OpenViking config that uses OpenAI embeddings."
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=DEFAULT_ENV_FILE,
        help="Path to the local .env file. Defaults to the repository .env.",
    )
    parser.add_argument(
        "--config-file",
        type=Path,
        default=DEFAULT_CONFIG_FILE,
        help="OpenViking config path. Defaults to ~/.openviking/ov.conf.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print the target path without writing ov.conf.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    values = merged_env(load_dotenv(args.env_file))
    config = build_openviking_config(values)

    if args.dry_run:
        print(f"OK OpenViking config can be written to {args.config_file}")
        return 0

    write_config(config, args.config_file)
    print(f"Wrote OpenViking config to {args.config_file}")
    print("API key was loaded but not printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
