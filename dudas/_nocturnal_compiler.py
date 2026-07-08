import subprocess
import json
import urllib.request
import time
import os

# --- CONFIGURACIÓN ---
INBOX_DIR = "01 - Inbox"
SCHEMA_FILE = "SCHEMA.md"

# 1. Función para llamar a Ollama (nativa)
def compiler_logic(note_content, schema_content, model="qwen2.5:14b"):
    system_prompt = f"Eres un asistente de compilación nocturna para un segundo cerebro. Tu trabajo es transformar notas en bruto en conocimiento atómico siguiendo estrictamente este SCHEMA:\n\n{schema_content}\n\nNo respondas con introducciones. Solo devuelve el contenido de la nota formateado."
    url = "http://localhost:11434/api/generate"
    data = {"model": model, "prompt": f"Procesa esta nota:\n{note_content}", "system": system_prompt, "stream": False}
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))['response']

# 2. Inicialización del servidor
server = subprocess.Popen(['node', 'dist/index.cjs'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
time.sleep(2) # Espera crítica: permite que el servidor MCP arranque y conecte a CouchDB

def send_rpc(method, params={}):
    request = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    server.stdin.write(json.dumps(request) + "\n")
    server.stdin.flush()
    
    # Leer hasta encontrar una respuesta JSON con ID 1
    while True:
        line = server.stdout.readline()
        if not line: break
        try:
            data = json.loads(line)
            if data.get("id") == 1: 
                return data
        except: continue
    return {"error": "No se recibió respuesta válida del servidor"}

# 3. Flujo principal

def run_compiler():
    print("Iniciando Compilador Nocturno...")
    
    # 1. Inicialización corregida
    init_params = {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "nocturnal-compiler", "version": "1.0.0"}
    }
    init = send_rpc("initialize", init_params)
    if "error" in init: print(f"Error inicialización: {init['error']}"); return
    
    # Confirmar inicialización
    send_rpc("notifications/initialized", {})

    # 2. Leer Esquema
    print("Leyendo SCHEMA.md...")
    schema_res = send_rpc("tools/call", {"name": "get_file_contents", "arguments": {"path": SCHEMA_FILE}})
    if "error" in schema_res: print(f"Error leyendo SCHEMA: {schema_res['error']}"); return
    schema = schema_res['result']['content'][0]['text']
    
    # 3. Listar Inbox
    print(f"Listando archivos en {INBOX_DIR}...")
    files_res = send_rpc("tools/call", {"name": "list_files_in_dir", "arguments": {"path": INBOX_DIR}})
    if "error" in files_res: print(f"Error listando archivos: {files_res['error']}"); return
    
    # Parseo seguro
    try:
        files_content = files_res['result']['content'][0]['text']
        file_list = json.loads(files_content)
    except:
        print("Error procesando lista de archivos. ¿El formato del servidor es inesperado?")
        return

# 4. Procesamiento
    for item in file_list:
        # Lógica inteligente: Si es un dict, sacamos el 'path', si es string, lo usamos directo
        file_path = item.get('path', item) if isinstance(item, dict) else item
        
        # Seguridad: asegurarnos que es string antes de operar
        if not isinstance(file_path, str):
            continue

        # Ignorar directorios si los hubiera
        if file_path.endswith('/'): 
            continue
        
        # ... resto del código ...


        
        note_res = send_rpc("tools/call", {"name": "get_file_contents", "arguments": {"path": file_path}})
        if "error" in note_res: continue
        content = note_res['result']['content'][0]['text']
        
        # Bloqueo de seguridad
        if "status/propuesta-ia" in content:
            continue
            
        print(f"Procesando {file_path}...")
        proposal_content = compiler_logic(content, schema)
        
        # Crear propuesta
        new_path = f"{INBOX_DIR}/propuesta-{os.path.basename(file_path)}"
        send_rpc("tools/call", {"name": "create_note", "arguments": {"path": new_path, "content": proposal_content}})
        print(f"Generada: {new_path}")

try:
    run_compiler()
finally:
    server.terminate()