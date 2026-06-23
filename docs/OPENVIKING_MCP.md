# OpenViking MCP Bridge

## Purpose

This document describes the local MCP bridge for testing `oh_my_documents` resources uploaded to OpenViking from Codex.

The bridge is intentionally thin. It does not implement OpenViking storage itself; it wraps the local `ov` CLI and exposes a small MCP tool surface for health checks, tree browsing, exact reads, semantic search, and source uploads.

## Prerequisites

- `.env` contains `OPENAI_API_KEY`.
- `scripts/setup_openviking_local_openai.py` has generated `C:\Users\qazx9\.openviking\ov.conf`.
- OpenViking server is running on `http://127.0.0.1:1933`.
- `ov config add custom --name local --url http://127.0.0.1:1933 --activate --force` has created the active local CLI config.

## Start OpenViking

```powershell
$env:UV_CACHE_DIR='.cache\uv'
uv run python scripts\setup_openviking_local_openai.py
uv run openviking-server --host 127.0.0.1 --port 1933
```

In a second terminal:

```powershell
$env:UV_CACHE_DIR='.cache\uv'
uv run ov config add custom --name local --url http://127.0.0.1:1933 --activate --force
uv run ov health -o json
```

## Upload Test

Upload the OpenViking index document:

```powershell
$env:UV_CACHE_DIR='.cache\uv'
uv run python -c "from pathlib import Path; from scripts import sync_openviking_docs as s; p=Path('docs/OPENVIKING_SUMMARY.md'); s.upload_file(p, s.target_uri(p), dry_run=False)"
```

OpenViking imports Markdown resources under a resource folder. For example, the uploaded file is read at:

```text
viking://resources/oh_my_documents/docs/OPENVIKING_SUMMARY/OPENVIKING_SUMMARY.md
```

## MCP Server

Run the MCP server over stdio:

```powershell
$env:UV_CACHE_DIR='.cache\uv'
uv run python scripts/openviking_mcp_server.py
```

Run the MCP server over HTTP for IP-based Codex registration:

```powershell
$env:UV_CACHE_DIR='.cache\uv'
$env:OPENVIKING_MCP_HOST='127.0.0.1'
$env:OPENVIKING_MCP_PORT='8765'
uv run python scripts/openviking_mcp_server.py --transport streamable-http
```

Then register it with Codex:

```powershell
codex mcp add oh-my-documents-openviking --url http://127.0.0.1:8765/mcp
```

Codex MCP command configuration:

```json
{
  "mcpServers": {
    "oh-my-documents-openviking": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "scripts/openviking_mcp_server.py"
      ],
      "cwd": "D:\\bootcamp\\workspace\\project\\03_final\\00_oh_my_documents"
    }
  }
}
```

## Exposed Tools

- `openviking_health`: checks local OpenViking server health.
- `openviking_tree`: lists resources under `viking://resources/oh_my_documents`.
- `openviking_read`: reads an exact Viking URI.
- `openviking_find`: runs semantic retrieval in the project scope.
- `openviking_upload_sources`: uploads the configured source files from this repo.

## Current Limitation

Semantic retrieval requires successful embedding generation. If OpenAI returns `insufficient_quota`, `openviking_tree` and `openviking_read` can still validate stored resources, but `openviking_find` will not be reliable until the API quota or billing issue is resolved.
