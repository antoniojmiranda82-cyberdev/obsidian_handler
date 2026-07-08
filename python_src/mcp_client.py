import subprocess
import json
import time
from .config import MCP_SERVER_PATH

class MCPClient:
    def __init__(self):
        self.server = None

    def start(self):
        """Inicia el proceso de Node.js"""
        print("Iniciando servidor MCP...")
        self.server = subprocess.Popen(
            ['node', MCP_SERVER_PATH], 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        time.sleep(2) # Espera crítica para la conexión a CouchDB
        
        # Inicialización del protocolo
        init_params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "nocturnal-compiler", "version": "1.0.0"}
        }
        init_res = self.send_rpc("initialize", init_params)
        if "error" in init_res:
            print(f"Error de inicialización MCP: {init_res['error']}")
            return False
            
        self.send_rpc("notifications/initialized", {})
        return True

    def send_rpc(self, method: str, params: dict = {}):
        """Envía un comando al servidor y espera la respuesta."""
        if not self.server: return {"error": "Servidor no iniciado"}
        
        request = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        self.server.stdin.write(json.dumps(request) + "\n")
        self.server.stdin.flush()
        
        while True:
            line = self.server.stdout.readline()
            if not line: break
            try:
                data = json.loads(line)
                if data.get("id") == 1: 
                    return data
            except json.JSONDecodeError:
                continue
                
        return {"error": "No se recibió respuesta válida del servidor"}

    def stop(self):
        """Cierra el subproceso limpiamente."""
        if self.server:
            self.server.terminate()