import importlib
import json
import os
import unittest
from unittest.mock import patch


class ConfigTests(unittest.TestCase):
    def test_defaults_match_local_models(self):
        with patch.dict(os.environ, {}, clear=True):
            import python_src.config as config
            importlib.reload(config)
            self.assertEqual(config.OLLAMA_CHAT_MODEL, "llama3.2:1b")
            self.assertEqual(config.OLLAMA_EMBED_MODEL, "mxbai-embed-large:latest")
            self.assertEqual(config.OLLAMA_GENERATE_URL, "http://127.0.0.1:11434/api/generate")
            self.assertEqual(config.OLLAMA_EMBED_URL, "http://127.0.0.1:11434/api/embed")
            self.assertEqual(config.OLLAMA_TAGS_URL, "http://127.0.0.1:11434/api/tags")

    def test_environment_overrides_defaults(self):
        overrides = {
            "OLLAMA_CHAT_MODEL": "custom-chat",
            "OLLAMA_EMBED_MODEL": "custom-embed",
            "OLLAMA_GENERATE_URL": "http://localhost:9999/generate",
            "OLLAMA_EMBED_URL": "http://localhost:9999/embed",
            "OLLAMA_TAGS_URL": "http://localhost:9999/tags",
        }
        with patch.dict(os.environ, overrides, clear=True):
            import python_src.config as config
            importlib.reload(config)
            self.assertEqual(config.OLLAMA_CHAT_MODEL, "custom-chat")
            self.assertEqual(config.OLLAMA_EMBED_MODEL, "custom-embed")
            self.assertEqual(config.OLLAMA_TAGS_URL, "http://localhost:9999/tags")


class HealthTests(unittest.TestCase):
    def test_health_reports_missing_models_without_raising(self):
        with patch.dict(os.environ, {}, clear=True):
            import python_src.config as config
            importlib.reload(config)
            import python_src.health as health
            importlib.reload(health)

            payload = json.dumps({"models": [{"name": "llama3.2:1b"}]}).encode("utf-8")

            class Response:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    return False

                def read(self):
                    return payload

            with patch("python_src.health.urllib.request.urlopen", return_value=Response()):
                result = health.check_ollama_health()

        self.assertFalse(result["ok"])
        self.assertEqual(result["chat_model"], "llama3.2:1b")
        self.assertEqual(result["embed_model"], "mxbai-embed-large:latest")
        self.assertEqual(result["missing_models"], ["mxbai-embed-large:latest"])
        self.assertIsNone(result["error"])


if __name__ == "__main__":
    unittest.main()
