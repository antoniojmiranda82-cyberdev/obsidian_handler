import json
import urllib.request
from .config import OLLAMA_CHAT_MODEL, OLLAMA_EMBED_MODEL, OLLAMA_TAGS_URL


def check_ollama_health() -> dict:
    result = {
        "ok": False,
        "chat_model": OLLAMA_CHAT_MODEL,
        "embed_model": OLLAMA_EMBED_MODEL,
        "missing_models": [],
        "error": None,
    }
    try:
        with urllib.request.urlopen(OLLAMA_TAGS_URL, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        names = {item.get("name") for item in payload.get("models", []) if isinstance(item, dict)}
        required = [OLLAMA_CHAT_MODEL, OLLAMA_EMBED_MODEL]
        result["missing_models"] = [name for name in required if name not in names]
        result["ok"] = not result["missing_models"]
    except Exception as exc:
        result["error"] = str(exc)
    return result
