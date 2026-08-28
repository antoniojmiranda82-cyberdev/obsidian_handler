# 🌙 Obsidian + Ollama Local Memory Bridge

This repository connects an Obsidian vault synchronized through Self-Hosted LiveSync/CouchDB to local Ollama models through Model Context Protocol (MCP).

For the Asset Ave + Dream Blvd operator, it is intentionally kept as a separate local service. The operator talks to the authenticated MCP HTTP transport, while Ollama and vault credentials stay on the local machine.

## Architecture

```text
Asset/Dream Operator
        |
        | authenticated Streamable HTTP MCP
        v
obsidian_handler (localhost:3100)
        |
        +--> CouchDB / Self-Hosted LiveSync / Obsidian
        |
        `--> Python compiler --> Ollama (localhost:11434)
```

The Python compiler is scoped by default to `Projects/asset-dream`. It reads raw notes, sends them to Ollama, and creates new `propuesta-*` notes instead of overwriting originals.

## Default Ollama Models

- Chat / local worker: `llama3.2:1b`
- Embeddings: `mxbai-embed-large:latest`

Both model names and all Ollama URLs are environment configurable.

## Requirements

- Node.js 20+
- Python 3.10+
- Ollama running locally
- CouchDB connected to Obsidian through Self-Hosted LiveSync

## Windows Setup

From PowerShell in the repository folder:

```powershell
npm install
npm run build
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in the local values. Never commit `.env`.

```powershell
Copy-Item .env.example .env
```

The Node MCP service expects these important keys:

```env
hostname=http://127.0.0.1:5984
dbname=obsidian_vault
username=YOUR_LOCAL_COUCHDB_USER
password=YOUR_LOCAL_COUCHDB_PASSWORD
passphrase=YOUR_LIVESYNC_PASSPHRASE

MCP_API_KEY=USE_A_STRONG_LOCAL_TOKEN
MCP_TRANSPORT=http
MCP_PORT=3100

OLLAMA_CHAT_MODEL=llama3.2:1b
OLLAMA_EMBED_MODEL=mxbai-embed-large:latest
OLLAMA_GENERATE_URL=http://127.0.0.1:11434/api/generate
OLLAMA_EMBED_URL=http://127.0.0.1:11434/api/embed
OLLAMA_TAGS_URL=http://127.0.0.1:11434/api/tags

ASSET_DREAM_ROOT=Projects/asset-dream
OBSIDIAN_INBOX_DIR=01 - Inbox
OBSIDIAN_SCHEMA_FILE=SCHEMA.md
```

Do not paste passwords, passphrases, or the MCP API key into chat or commit them to GitHub.

## Required Obsidian Layout

By default the project memory lives here:

```text
Projects/
└── asset-dream/
    ├── SCHEMA.md
    ├── 01 - Inbox/
    └── Proposals/
```

The `Proposals` folder is the safe write area for the operator. Existing notes are not automatically overwritten.

## Start the MCP Bridge

```powershell
npm start
```

With `MCP_TRANSPORT=http`, the bridge stays local on port `3100` by default.

Test its health from another PowerShell window:

```powershell
Invoke-RestMethod http://127.0.0.1:3100/health
```

Test Ollama separately:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

## Run the Python Compiler

```powershell
python -m python_src.main
```

Before processing notes, the compiler checks that Ollama is reachable and that both required models are installed. It stops cleanly if the local model service is not ready.

## Asset/Dream Operator Connection

The separate `codex-plus-hermes-team` operator uses:

```env
ASSET_DREAM_MEMORY_BRIDGE_URL=http://127.0.0.1:3100
ASSET_DREAM_MEMORY_BRIDGE_API_KEY=THE_SAME_VALUE_AS_MCP_API_KEY
ASSET_DREAM_MEMORY_ROOT=Projects/asset-dream

OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_CHAT_MODEL=llama3.2:1b
OLLAMA_EMBED_MODEL=mxbai-embed-large:latest
```

The operator exposes only project-scoped memory operations for `asset-dream:*` workers: health, search, read, and proposal creation.

## Security

- `.env` is ignored and must remain local.
- The MCP HTTP transport should stay on localhost/private networking.
- Do not expose Ollama port `11434` directly to the public internet.
- Do not expose MCP port `3100` publicly without an authenticated private tunnel.
- Any secrets that were committed to Git history before `.env` was removed should be treated as exposed and rotated.

## Tests

```powershell
python -m unittest discover -s tests -v
npm run typecheck
npm test
npm run build
```
