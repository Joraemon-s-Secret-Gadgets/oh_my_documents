from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET_ROOT = "viking://resources/oh_my_documents"

ROOT_INCLUDE_FILES = ("AGENT.md", "README.md")
DOCS_INCLUDE_SUFFIXES = {".md", ".txt", ".json", ".yml", ".yaml"}
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "assets",
    "node_modules",
    "pages",
    "pdf",
}
EXCLUDED_SUFFIXES = {
    ".html",
    ".jpeg",
    ".jpg",
    ".pdf",
    ".png",
    ".pptx",
}


def is_excluded(path: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return True
    return path.suffix.lower() in EXCLUDED_SUFFIXES


def collect_sync_files(root: Path = ROOT) -> list[Path]:
    root = root.resolve()
    root_files: list[Path] = []
    docs_files: set[Path] = set()

    for filename in ROOT_INCLUDE_FILES:
        path = root / filename
        if path.is_file() and not is_excluded(path.relative_to(root)):
            root_files.append(path.relative_to(root))

    docs = root / "docs"
    if docs.is_dir():
        for path in docs.rglob("*"):
            if not path.is_file():
                continue
            relative_path = path.relative_to(root)
            if is_excluded(relative_path):
                continue
            if path.suffix.lower() in DOCS_INCLUDE_SUFFIXES:
                docs_files.add(relative_path)

    return root_files + sorted(docs_files, key=lambda path: path.as_posix().lower())


def target_uri(relative_path: Path) -> str:
    return f"{TARGET_ROOT}/{relative_path.as_posix()}"


def upload_file(source_path: Path, destination_uri: str, *, dry_run: bool = True) -> None:
    if dry_run:
        print(f"DRY-RUN {source_path.as_posix()} -> {destination_uri}")
        return

    # Replace this function body when the OpenViking CLI command is finalized.
    print(f"UPLOAD-TODO {source_path.as_posix()} -> {destination_uri}")


def sync_files(root: Path = ROOT, *, dry_run: bool = True) -> list[Path]:
    files = collect_sync_files(root)
    for relative_path in files:
        upload_file(root / relative_path, target_uri(relative_path), dry_run=dry_run)
    return files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare oh_my_documents source files for OpenViking sync."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root. Defaults to the parent directory of scripts/.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print planned source and target paths without uploading. This is the default.",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Call upload_file() for each target. The current implementation is a placeholder.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dry_run = not args.upload or args.dry_run
    files = sync_files(args.root.resolve(), dry_run=dry_run)
    print(f"Total files: {len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
