# Shadow Waves Docker Hosting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn `obsidian_handler` into a clean, Docker-ready QST/Shadow Waves memory service that can host the MCP bridge and integrate safely with CouchDB/Self-Hosted LiveSync and Ollama while preserving compatibility with the existing Asset/Dream configuration.

**Architecture:** Keep Obsidian/CouchDB as the memory store, Ollama as the local model runtime, and `obsidian_handler` as the authenticated MCP boundary. Containerize the Node/Python bridge, provide Docker Compose wiring for CouchDB and the bridge, and treat Ollama as a host service by default so existing laptop models do not need to be duplicated inside Docker. Preserve localhost/private-network defaults and keep all credentials in local environment files.

**Tech Stack:** Node.js 20+, TypeScript, Python 3.10+, MCP SDK, CouchDB, Self-Hosted LiveSync, Ollama, Docker, Docker Compose, GitHub Actions.

**Spec:** Existing `README.md`, `.env.example`, `src/config.ts`, `python_src/config.py`, and `python_src/scope.py` in this repository.

## Global Constraints

- Do not commit `.env`, CouchDB credentials, LiveSync passphrases, or MCP API keys.
- Keep MCP and Ollama private by default; do not expose ports publicly.
- Preserve current Asset/Dream environment variables as backward-compatible aliases during migration.
- Do not overwrite original Obsidian notes automatically; generated content must remain proposal-style writes.
- Keep the default branch untouched until CI and local laptop checks pass.
- Use health checks for CouchDB, MCP bridge, and Ollama connectivity.

---

### Task 1: Generalize project memory scope without breaking old configs

**Files:**
- Modify: `python_src/scope.py`
- Modify: `python_src/config.py`
- Modify: `python_src/main.py`
- Modify: `.env.example`
- Test: `tests/test_scope.py`

**Interfaces:**
- Consumes: existing `ASSET_DREAM_ROOT`, `OBSIDIAN_INBOX_DIR`, `OBSIDIAN_SCHEMA_FILE`
- Produces: `OBSIDIAN_PROJECT_ROOT`, `project_path(relative: str)`, `proposal_path(source_path: str)` with fallback to `ASSET_DREAM_ROOT`

- [ ] Write a failing test proving `OBSIDIAN_PROJECT_ROOT` is preferred and `ASSET_DREAM_ROOT` remains a fallback.
- [ ] Run the focused scope test and confirm it fails for the missing generic configuration.
- [ ] Implement generic project-root naming while retaining the old environment variable alias.
- [ ] Update console messages to neutral English operational messages.
- [ ] Run Python tests and confirm both generic and compatibility cases pass.
- [ ] Commit the scope migration.

### Task 2: Harden runtime configuration

**Files:**
- Modify: `src/config.ts`
- Modify: `src/config.test.ts`
- Modify: `.env.example`

**Interfaces:**
- Consumes: CouchDB URL, database name, credentials, MCP transport and API key
- Produces: validated runtime config that rejects insecure HTTP transport configuration when authentication is absent

- [ ] Write failing tests for HTTP mode without an MCP API key and for invalid public bind assumptions.
- [ ] Run the config tests and verify the new tests fail for the intended reasons.
- [ ] Require an MCP API key whenever HTTP transport is enabled.
- [ ] Keep stdio behavior compatible for local agent clients.
- [ ] Run TypeScript tests and typecheck.
- [ ] Commit runtime hardening.

### Task 3: Add production Docker image for the bridge

**Files:**
- Create: `Dockerfile`
- Create: `.dockerignore`

**Interfaces:**
- Consumes: `package.json`, `package-lock.json`, `requirements.txt`, TypeScript build output
- Produces: a non-root container image that runs the MCP bridge and contains the Python compiler dependencies

- [ ] Add a multi-stage Node 20 build that runs `npm ci` and `npm run build`.
- [ ] Add Python 3.10+ runtime support and install `requirements.txt`.
- [ ] Create a non-root runtime user.
- [ ] Copy only required runtime files and built output.
- [ ] Configure the container command to start the MCP HTTP bridge.
- [ ] Add `.dockerignore` entries for `.env`, `.git`, caches, `node_modules`, `dist`, editor metadata, and local vault data.
- [ ] Build the image locally tomorrow on the laptop and record the result.

### Task 4: Add Docker Compose for CouchDB + MCP bridge

**Files:**
- Create: `docker-compose.yml`
- Create: `docker-compose.override.example.yml`

**Interfaces:**
- Consumes: local `.env` values for CouchDB user/password, database name, LiveSync passphrase, MCP API key, and project root
- Produces: `couchdb` and `obsidian-handler` services on a private Docker network with persistent CouchDB storage

- [ ] Define CouchDB with persistent named volume and health check.
- [ ] Bind CouchDB to localhost by default rather than all interfaces.
- [ ] Define the MCP bridge service with dependency on healthy CouchDB.
- [ ] Point bridge CouchDB hostname at the Compose service name.
- [ ] Point Ollama URLs at `host.docker.internal:11434` by default for Windows/macOS laptop use.
- [ ] Add `extra_hosts: host-gateway` compatibility for Linux.
- [ ] Add an MCP `/health` health check.
- [ ] Keep all secrets environment-driven and absent from committed YAML.
- [ ] Validate with `docker compose config` tomorrow.

### Task 5: Add operator/agent deployment contract

**Files:**
- Create: `docs/SHADOW-WAVES-AGENT-HOSTING.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: MCP base URL and API key
- Produces: one documented contract for Billy, Kanaan, Tommy, Ghost, Sheldon, Trump, and future Q-Core workers to use the same memory bridge safely

- [ ] Document read/search/proposal-write boundaries.
- [ ] Document that agents do not receive raw CouchDB credentials.
- [ ] Document recommended per-agent project roots under `Projects/qst/`.
- [ ] Document laptop-online requirements for local Ollama inference.
- [ ] Document phone-only behavior: Obsidian may sync, but local Ollama agent actions require the laptop/runtime online.
- [ ] Commit agent-hosting documentation.

### Task 6: CI validation for Docker and existing tests

**Files:**
- Modify: `.github/workflows/test.yml`

**Interfaces:**
- Consumes: project source plus Dockerfile/Compose files
- Produces: CI checks for Node tests, Python tests, typecheck, build, Docker image build, and Compose syntax

- [ ] Add Docker build validation to CI.
- [ ] Add `docker compose config` validation using non-secret placeholder environment values.
- [ ] Keep existing tests in place.
- [ ] Run GitHub Actions and inspect every failing job before changing code.
- [ ] Commit only after CI passes.

### Task 7: Tomorrow laptop integration test

**Files:**
- No repository changes required unless a test exposes a defect.

**Interfaces:**
- Consumes: Docker Desktop, local Ollama, Obsidian 1.13.7, Self-Hosted LiveSync, local `.env`
- Produces: verified end-to-end path from agent client to MCP to CouchDB/Obsidian and Ollama

- [ ] Confirm `ollama list` shows the configured chat and embedding models.
- [ ] Start Docker Desktop.
- [ ] Run `docker compose up -d --build`.
- [ ] Verify CouchDB health.
- [ ] Verify MCP `/health`.
- [ ] Verify the bridge can reach Ollama on the host.
- [ ] Configure Self-Hosted LiveSync on desktop and phone against the same CouchDB database.
- [ ] Create one disposable test note from the phone and verify it appears on desktop.
- [ ] Run one agent read/search call and one proposal-note write.
- [ ] Confirm the original note remains unchanged.
- [ ] Only after these checks pass, open/merge the cleanup PR.
