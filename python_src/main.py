import os
import json
from python_src.config import INBOX_DIR, SCHEMA_FILE
from python_src.mcp_client import MCPClient
from python_src.llm_client import compiler_logic

def main():
    print("=== Iniciando Compilador Nocturno ===")
    
    # 1. Levantar el cliente MCP
    mcp = MCPClient()
    if not mcp.start():
        return

    try:
        # 2. Leer Esquema
        print("Leyendo SCHEMA.md...")
        schema_res = mcp.send_rpc("tools/call", {"name": "get_file_contents", "arguments": {"path": SCHEMA_FILE}})
        if "error" in schema_res: 
            print(f"Error leyendo SCHEMA: {schema_res['error']}"); return
        schema = schema_res['result']['content'][0]['text']
        
        # 3. Listar Inbox
        print(f"Listando archivos en {INBOX_DIR}...")
        files_res = mcp.send_rpc("tools/call", {"name": "list_files_in_dir", "arguments": {"path": INBOX_DIR}})
        if "error" in files_res: 
            print(f"Error listando archivos: {files_res['error']}"); return
        
        # Parsear la lista (usando la lógica defensiva de tu script original)
        try:
            file_list = json.loads(files_res['result']['content'][0]['text'])
        except Exception:
            print("Error procesando lista de archivos.")
            return

        # 4. Procesamiento
        for item in file_list:
            file_path = item.get('path', item) if isinstance(item, dict) else item
            if not isinstance(file_path, str) or file_path.endswith('/'):
                continue
                
            # Leer nota original
            note_res = mcp.send_rpc("tools/call", {"name": "get_file_contents", "arguments": {"path": file_path}})
            if "error" in note_res: continue
            content = note_res['result']['content'][0]['text']
            
            # Filtro anti-bucles
            if "status/propuesta-ia" in content:
                print(f"Saltando {file_path} (Ya procesada).")
                continue
                
            print(f"Procesando nota con IA: {file_path}...")
            proposal_content = compiler_logic(content, schema)
            
            if proposal_content:
                new_path = f"{INBOX_DIR}/propuesta-{os.path.basename(file_path)}"
                mcp.send_rpc("tools/call", {"name": "create_note", "arguments": {"path": new_path, "content": proposal_content}})
                print(f"-> Propuesta guardada exitosamente en: {new_path}")

    finally:
        # Siempre cerramos el servidor, incluso si hay un error
        print("Cerrando servidor MCP...")
        mcp.stop()
        print("=== Compilación finalizada ===")

if __name__ == "__main__":
    main()