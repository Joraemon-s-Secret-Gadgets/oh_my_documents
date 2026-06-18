from __future__ import annotations

import unittest

from scripts import setup_openviking_local_openai


class OpenVikingOpenAIConfigTests(unittest.TestCase):
    def test_build_openviking_config_uses_openai_embedding_defaults(self) -> None:
        values = setup_openviking_local_openai.merged_env(
            {
                "OPENAI_API_KEY": "test-key",
                "OPENVIKING_WORKSPACE": "C:\\tmp\\openviking",
            }
        )

        config = setup_openviking_local_openai.build_openviking_config(values)

        self.assertEqual(config["storage"]["workspace"], "C:\\tmp\\openviking")
        self.assertEqual(
            config["embedding"]["dense"]["model"], "text-embedding-3-small"
        )
        self.assertEqual(config["embedding"]["dense"]["dimension"], 1536)
        self.assertEqual(config["embedding"]["dense"]["api_key"], "test-key")
        self.assertNotIn("vlm", config)

    def test_build_openviking_config_requires_api_key(self) -> None:
        values = setup_openviking_local_openai.merged_env({})

        with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY is required"):
            setup_openviking_local_openai.build_openviking_config(values)


if __name__ == "__main__":
    unittest.main()
