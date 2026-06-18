from __future__ import annotations

import subprocess
import unittest
from unittest.mock import patch

from scripts import openviking_mcp_server


class OpenVikingMcpServerTests(unittest.TestCase):
    def test_run_ov_returns_stdout(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["ov", "health"],
            returncode=0,
            stdout='{"ok": true}\n',
            stderr="",
        )

        with patch.object(openviking_mcp_server, "ov_command", return_value="ov"):
            with patch.object(
                openviking_mcp_server.subprocess,
                "run",
                return_value=completed,
            ) as run:
                output = openviking_mcp_server.run_ov(["health", "-o", "json"])

        self.assertEqual(output, '{"ok": true}')
        run.assert_called_once()

    def test_run_ov_raises_on_failure(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["ov", "health"],
            returncode=1,
            stdout="",
            stderr="server unavailable",
        )

        with patch.object(openviking_mcp_server, "ov_command", return_value="ov"):
            with patch.object(
                openviking_mcp_server.subprocess,
                "run",
                return_value=completed,
            ):
                with self.assertRaisesRegex(RuntimeError, "server unavailable"):
                    openviking_mcp_server.run_ov(["health"])


if __name__ == "__main__":
    unittest.main()
