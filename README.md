# 🌙 Compilador Nocturno (Segundo Cerebro impulsado por MCP y Ollama)

Este sistema implementa un patrón de arquitectura avanzado conocido como **"Compilador Nocturno"** para la gestión del conocimiento personal. Su objetivo es automatizar la limpieza, formateo y atomización de notas rápidas o desorganizadas que se han guardado en la bandeja de entrada de **Obsidian** durante el día, utilizando Inteligencia Artificial local (**Ollama**) de forma autónoma.

Este proyecto unifica en un solo repositorio el **Orquestador (Python)** y el **Servidor de Base de Datos (Node.js / TypeScript)** usando el estándar **Model Context Protocol (MCP)**.

---

## 🏗️ Arquitectura del Sistema

El sistema se compone de tres piezas de software principales que se comunican entre sí en tiempo real de forma local, garantizando privacidad absoluta:

```text
[ Orquestador Python ] <--- (JSON-RPC via stdio) ---> [ Servidor MCP Node.js ] <---> [ CouchDB (Vault Obsidian) ]
         |
         +------------------- (API HTTP Local) -------> [ Ollama (Qwen 2.5) ]

```

1. **El Orquestador (`python_src/`):** Script de Python que inicia el flujo. Levanta el servidor MCP en segundo plano, coordina la lectura de la bandeja de entrada, envía el texto a la IA y ordena la creación de las notas procesadas.
2. **El Servidor MCP (`src/` compilado a `dist/`):** Desarrollado en TypeScript. Actúa como traductor exponiendo herramientas estándar (`list_files_in_dir`, `get_file_contents`, `Notes`) para que Python interactúe con la base de datos sin tocar directamente los archivos.
3. **Base de Datos (CouchDB):** El motor de almacenamiento sincronizado con Obsidian (vía *Self-Hosted LiveSync*).
4. **Motor de IA (Ollama):** Ejecuta el modelo de lenguaje de código abierto (`qwen2.5:14b`) siguiendo las reglas estrictas definidas en un archivo `SCHEMA.md`.

---

## 📂 Estructura del Proyecto

El proyecto está diseñado para separar claramente las responsabilidades del puente de conexión y la lógica de inteligencia artificial:

```text
Nocturnal-Compiler/
├── .env                  # (IGNORADO POR GIT) Credenciales y URLs.
├── SCHEMA.md             # Instrucciones y estructura estricta para la IA.
│
# --- LADO NODE.JS (Servidor MCP) ---
├── src/                  # Código fuente en TypeScript del puente MCP.
├── lib/                  # Utilidades y submódulos del servidor.
├── package.json          # Dependencias de Node.js.
├── tsconfig.json         # Configuración de TypeScript.
├── vite.config.ts        # Planos de construcción para compilar a JavaScript.
├── dist/                 # (AUTOGENERADO) Carpeta con el index.cjs compilado.
│
# --- LADO PYTHON (Orquestador) ---
├── python_src/           # Lógica principal de ejecución.
│   ├── main.py           # Bucle principal e inicializador.
│   ├── config.py         # Variables globales.
│   ├── mcp_client.py     # Gestor del subproceso Node y JSON-RPC.
│   └── llm_client.py     # Conexión directa con la API de Ollama.
└── requirements.txt      # Dependencias de Python (ej. python-dotenv).

```

---

## ⚙️ Flujo Lógico de Ejecución

1. **Handshake MCP:** Python ejecuta el archivo compilado `dist/index.cjs` e inicializa la comunicación por JSON-RPC 2.0.
2. **Lectura de Directrices:** Se extrae el contenido de `SCHEMA.md` que servirá como *System Prompt* para la IA.
3. **Escaneo de Bandeja (Inbox):** El servidor MCP consulta CouchDB y devuelve un listado de notas.
4. **Filtro Anti-Bucles:** Se ignora cualquier nota que ya contenga la cadena `"status/propuesta-ia"`.
5. **Procesamiento de IA:** El contenido de las notas pendientes se envía a Ollama localmente.
6. **Inyección en Obsidian:** Python ordena al servidor MCP guardar la respuesta de Ollama como una nota nueva prefijada con `propuesta-`, dejando la original intacta para validación humana.

---

## 🚀 Guía de Instalación y Despliegue

### Prerrequisitos Globales

* **Node.js** (v18 o superior).
* **Python 3.10** o superior.
* **Ollama** con el modelo descargado: `ollama run qwen2.5:14b`.
* **CouchDB** corriendo y accesible.

### Paso 1: Clonar y Configurar Entorno

```bash
git clone https://github.com/maortegam/obsidian_handler.git
cd obsidian_handler

```

Crea el archivo `.env` en la raíz del proyecto (nunca lo subas al repositorio):

```env
# Ejemplo para un entorno local/servidor unificado:
hostname=https://your.domain.com
dbname=obsidian_vault
db_username=username
db_password=password 
e2ee_passphrase=passphrase 
mcpTransport=stdio
```

Asegúrate de crear tu archivo `SCHEMA.md` en la raíz con la estructura en formato Markdown que deseas que la IA siga.

### Paso 2: Compilar el Servidor Node.js (MCP)

Dado que la carpeta `dist/` no se incluye en el control de versiones, debes compilar el puente en la máquina destino:

```bash
npm install
npm run build

```

*Esto generará el archivo crítico `dist/index.cjs`.*

### Paso 3: Preparar el Entorno de Python

Se recomienda el uso de entornos virtuales para no interferir con las librerías del sistema:

```bash
# Crear y activar entorno virtual (Linux/Mac)
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

```

### Paso 4: Ejecución

Con el entorno virtual activado y la compilación terminada, lanza el orquestador como un módulo de Python para mantener correctamente las rutas relativas:

```bash
python3 -m python_src.main

```

Si todo es correcto, verás el registro en consola indicando la conexión, lectura del `SCHEMA.md`, procesamiento de notas e inyección en CouchDB.

---

## 🛠️ Solución de Problemas Comunes

* **`ModuleNotFoundError: No module named 'python_src'`**: Estás intentando ejecutar el archivo directamente (`python main.py`). Debes ejecutarlo como módulo desde la raíz del proyecto usando `python -m python_src.main`.
* **El código termina inmediatamente sin imprimir nada**: Verifica que no haya un error de sintaxis silenciado o que la compilación de Node haya fallado dejando `dist/index.cjs` vacío.
* **`ModuleLoader.loadEntryModule` / `ENOENT` durante `npm run build**`: Asegúrate de haber clonado correctamente el repositorio incluyendo sus submódulos o carpetas anidadas (`lib/`).
* **Conflictos de Git con `.env` al hacer `git pull**`: Ejecuta `git stash` para guardar temporalmente tu `.env` local, haz el `pull` y luego restáuralo. Para evitar esto, cerciórate de que `.env` está dentro de `.gitignore`.