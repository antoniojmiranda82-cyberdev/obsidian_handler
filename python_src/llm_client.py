import json
import urllib.request
from .config import OLLAMA_URL, OLLAMA_MODEL

def compiler_logic(note_content: str, schema_content: str) -> str:
    """Envía la nota y el esquema a Ollama y devuelve la propuesta formateada."""
    system_prompt = f"Eres un asistente de compilación nocturna para un segundo cerebro. Tu trabajo es transformar notas en bruto en conocimiento atómico siguiendo estrictamente este SCHEMA:\n\n{schema_content}\n\nNo respondas con introducciones. Solo devuelve el contenido de la nota formateado."
    
    data = {
        "model": OLLAMA_MODEL, 
        "prompt": f"Procesa esta nota:\n{note_content}", 
        "system": system_prompt, 
        "stream": False
    }
    
    req = urllib.request.Request(
        OLLAMA_URL, 
        data=json.dumps(data).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))['response']
    except Exception as e:
        print(f"Error conectando con Ollama: {e}")
        return ""