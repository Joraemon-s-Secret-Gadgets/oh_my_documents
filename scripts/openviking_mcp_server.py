from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import sync_openviking_docs


TARGET_ROOT = sync_openviking_docs.TARGET_ROOT
ROOT = sync_openviking_docs.ROOT
DEFAULT_TIMEOUT_SECONDS = 120

mcp = FastMCP(
    "oh-my-documents-openviking",
    instructions=(
        "Query and manage oh_my_documents resources stored in OpenViking. "
        f"Default scope: {TARGET_ROOT}"
    ),
    host=os.environ.get("OPENVIKING_MCP_HOST", "127.0.0.1"),
    port=int(os.environ.get("OPENVIKING_MCP_PORT", "8765")),
    streamable_http_path=os.environ.get("OPENVIKING_MCP_PATH", "/mcp"),
)


def ov_command() -> str:
    scripts_dir = Path(sys.executable).resolve().parent
    executable = scripts_dir / ("ov.exe" if sys.platform == "win32" else "ov")
    if executable.exists():
        return str(executable)
    return "ov"


def run_ov(args: list[str], *, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> str:
    result = subprocess.run(
        [ov_command(), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    if result.returncode != 0:
        raise RuntimeError(output or f"ov exited with {result.returncode}")
    return output


@mcp.tool()
def openviking_health() -> str:
    """Check whether the configured OpenViking server is reachable."""
    return run_ov(["health", "-o", "json"])


@mcp.tool()
def openviking_tree(
    uri: str = TARGET_ROOT,
    level_limit: int = 3,
    limit: int = 80,
) -> str:
    """Show resources under a Viking URI."""
    return run_ov(
        [
            "tree",
            uri,
            "-L",
            str(level_limit),
            "--limit",
            str(limit),
            "-o",
            "json",
        ]
    )


@mcp.tool()
def openviking_find(
    query: str,
    uri: str = TARGET_ROOT,
    limit: int = 8,
    levels: str = "0,1,2",
) -> str:
    """Run semantic retrieval inside the oh_my_documents OpenViking scope."""
    return run_ov(
        [
            "find",
            query,
            "--uri",
            uri,
            "--limit",
            str(limit),
            "--level",
            levels,
            "-o",
            "json",
        ]
    )


@mcp.tool()
def openviking_read(uri: str) -> str:
    """Read exact file content from a Viking URI."""
    return run_ov(["read", uri, "-o", "json"])


@mcp.tool()
def openviking_upload_sources(wait: bool = True) -> str:
    """Upload the configured oh_my_documents source files into OpenViking."""
    files = sync_openviking_docs.sync_files(ROOT, dry_run=False, wait=wait)
    return f"Uploaded {len(files)} files to {TARGET_ROOT}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the oh_my_documents OpenViking MCP bridge."
    )
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default="stdio",
        help="MCP transport. Use streamable-http for IP/URL based registration.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
