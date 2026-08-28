import os
from dotenv import load_dotenv

load_dotenv()

INBOX_DIR = os.getenv("OBSIDIAN_INBOX_DIR", "01 - Inbox")
SCHEMA_FILE = os.getenv("OBSIDIAN_SCHEMA_FILE", "SCHEMA.md")

OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3.2:1b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "mxbai-embed-large:latest")
OLLAMA_GENERATE_URL = os.getenv("OLLAMA_GENERATE_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_EMBED_URL = os.getenv("OLLAMA_EMBED_URL", "http://127.0.0.1:11434/api/embed")
OLLAMA_TAGS_URL = os.getenv("OLLAMA_TAGS_URL", "http://127.0.0.1:11434/api/tags")

MCP_SERVER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist", "index.cjs")
