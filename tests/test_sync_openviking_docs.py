from __future__ import annotations

import unittest
from pathlib import Path

from scripts import sync_openviking_docs


def write_file(path: Path, content: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class OpenVikingSyncTests(unittest.TestCase):
    def test_collect_sync_files_includes_only_openviking_source_files(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_file(root / "README.md")
            write_file(root / "AGENT.md")
            write_file(root / "docs" / "OPENVIKING_INDEX.md")
            write_file(root / "docs" / "05_agent_spec" / "AGENT.md")
            write_file(root / "docs" / "sample.txt")
            write_file(root / "docs" / "sample.json")
            write_file(root / "docs" / "sample.yml")
            write_file(root / "docs" / "sample.yaml")

            write_file(root / "index.html")
            write_file(root / "pages" / "sample.html")
            write_file(root / "pdf" / "sample.pdf")
            write_file(root / "assets" / "sample.png")
            write_file(root / ".git" / "config")
            write_file(root / ".venv" / "pyvenv.cfg")
            write_file(root / "node_modules" / "pkg" / "index.js")
            write_file(root / "docs" / "image.jpg")
            write_file(root / "docs" / "slides.pptx")
            write_file(root / "docs" / "page.html")

            files = [
                path.as_posix() for path in sync_openviking_docs.collect_sync_files(root)
            ]

        self.assertEqual(
            files,
            [
                "AGENT.md",
                "README.md",
                "docs/05_agent_spec/AGENT.md",
                "docs/OPENVIKING_INDEX.md",
                "docs/sample.json",
                "docs/sample.txt",
                "docs/sample.yaml",
                "docs/sample.yml",
            ],
        )

    def test_target_uri_preserves_relative_path(self) -> None:
        self.assertEqual(
            sync_openviking_docs.target_uri(Path("docs/OPENVIKING_INDEX.md")),
            "viking://resources/oh_my_documents/docs/OPENVIKING_INDEX.md",
        )


if __name__ == "__main__":
    unittest.main()
