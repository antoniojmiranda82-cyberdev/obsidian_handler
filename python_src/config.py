import os
from dotenv import load_dotenv

# Cargamos el archivo .env
load_dotenv()

# Configuraciones principales
INBOX_DIR = "01 - Inbox"
SCHEMA_FILE = "SCHEMA.md"

# El modelo de Ollama que vas a usar
OLLAMA_MODEL = "qwen2.5:14b"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Ruta al servidor MCP (ahora está en la carpeta superior, dentro de dist)
MCP_SERVER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dist', 'index.cjs')