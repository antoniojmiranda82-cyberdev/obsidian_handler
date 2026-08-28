import json
import urllib.request
from .config import OLLAMA_CHAT_MODEL, OLLAMA_GENERATE_URL


def compiler_logic(note_content: str, schema_content: str) -> str:
    """Send a note and schema to local Ollama and return formatted proposal text."""
    system_prompt = (
        "Eres un asistente de compilación nocturna para un segundo cerebro. "
        "Tu trabajo es transformar notas en bruto en conocimiento atómico siguiendo estrictamente este SCHEMA:\n\n"
        f"{schema_content}\n\nNo respondas con introducciones. Solo devuelve el contenido de la nota formateado."
    )

    data = {
        "model": OLLAMA_CHAT_MODEL,
        "prompt": f"Procesa esta nota:\n{note_content}",
        "system": system_prompt,
        "stream": False,
    }

    req = urllib.request.Request(
        OLLAMA_GENERATE_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))["response"]
    except Exception as exc:
        print(f"Error conectando con Ollama: {exc}")
        return ""
