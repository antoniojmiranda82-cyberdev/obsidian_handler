import json
from python_src.config import INBOX_DIR, SCHEMA_FILE
from python_src.health import check_ollama_health
from python_src.llm_client import compiler_logic
from python_src.mcp_client import MCPClient
from python_src.scope import asset_dream_path, proposal_path


def main():
    print("=== Iniciando Compilador Nocturno ===")

    health = check_ollama_health()
    if not health["ok"]:
        print(f"Ollama no está listo: {health}")
        return

    mcp = MCPClient()
    if not mcp.start():
        return

    inbox_path = asset_dream_path(INBOX_DIR)
    schema_path = asset_dream_path(SCHEMA_FILE)

    try:
        print(f"Leyendo {schema_path}...")
        schema_res = mcp.send_rpc(
            "tools/call",
            {"name": "get_file_contents", "arguments": {"path": schema_path}},
        )
        if "error" in schema_res:
            print(f"Error leyendo SCHEMA: {schema_res['error']}")
            return
        schema = schema_res["result"]["content"][0]["text"]

        print(f"Listando archivos en {inbox_path}...")
        files_res = mcp.send_rpc(
            "tools/call",
            {"name": "list_files_in_dir", "arguments": {"path": inbox_path}},
        )
        if "error" in files_res:
            print(f"Error listando archivos: {files_res['error']}")
            return

        try:
            file_list = json.loads(files_res["result"]["content"][0]["text"])
        except Exception:
            print("Error procesando lista de archivos.")
            return

        for item in file_list:
            file_path = item.get("path", item) if isinstance(item, dict) else item
            if not isinstance(file_path, str) or file_path.endswith("/"):
                continue

            note_res = mcp.send_rpc(
                "tools/call",
                {"name": "get_file_contents", "arguments": {"path": file_path}},
            )
            if "error" in note_res:
                continue
            content = note_res["result"]["content"][0]["text"]

            if "status/propuesta-ia" in content or file_path.rsplit("/", 1)[-1].startswith("propuesta-"):
                print(f"Saltando {file_path} (Ya procesada o propuesta).")
                continue

            print(f"Procesando nota con IA: {file_path}...")
            proposal_content = compiler_logic(content, schema)

            if proposal_content:
                new_path = proposal_path(file_path)
                create_res = mcp.send_rpc(
                    "tools/call",
                    {"name": "create_note", "arguments": {"path": new_path, "content": proposal_content}},
                )
                if "error" in create_res:
                    print(f"Error guardando propuesta: {create_res['error']}")
                else:
                    print(f"-> Propuesta guardada exitosamente en: {new_path}")

    finally:
        print("Cerrando servidor MCP...")
        mcp.stop()
        print("=== Compilación finalizada ===")


if __name__ == "__main__":
    main()
