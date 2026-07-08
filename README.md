Este sistema implementa un patrón de arquitectura avanzado conocido como **"Compilador Nocturno"** para la gestión del conocimiento personal (segundo cerebro). Su objetivo es automatizar la limpieza, el formateo y la atomización de notas rápidas o desorganizadas que hayas guardado en tu bandeja de entrada de **Obsidian** durante el día, utilizando Inteligencia Artificial local (**Ollama**) mientras no estás usando el ordenador.

A continuación, encontrarás la explicación detallada de su arquitectura, funcionamiento y los pasos exactos para reproducir este entorno en tu máquina.

---

# Arquitectura y Procesos de Alto Nivel

El sistema se compone de tres piezas de software principales que se comunican entre sí en tiempo real:

```
[ Orquestador Python ] <--- (JSON-RPC via Pipes) ---> [ Servidor MCP Node.js ] <---> [ CouchDB (Vault Obsidian) ]
         |
         +------------------- (API HTTP Local) -------> [ Ollama (Qwen 2.5) ]

```

1. **El Orquestador (Script Python):** Es el cerebro lógico del flujo. Se encarga de iniciar el servidor secundario, coordinar la lectura de archivos, enviar los textos a la IA y ordenar la creación de las notas finales procesadas.
2. **El Servidor MCP (Script Node.js):** Utiliza el protocolo **Model Context Protocol (MCP)** desarrollado por Anthropic. Funciona como un puente o traductor. Expone "herramientas" estándar (`list_files_in_dir`, `get_file_contents`, `Notes`) para que el script de Python pueda manipular el contenido de Obsidian sin necesidad de interactuar directamente con archivos locales.
3. **La Base de Datos (CouchDB):** Es el motor de almacenamiento. Obsidian suele sincronizarse con CouchDB mediante plugins como *Self-Hosted LiveSync*. El servidor MCP lee y escribe las notas directamente en CouchDB usando las credenciales guardadas en el archivo `.env`.
4. **El Motor de IA (Ollama):** Ejecuta localmente el modelo de lenguaje de código abierto (`qwen2.5:14b`) para reestructurar las notas siguiendo las reglas estrictas de un archivo de plantilla (`SCHEMA.md`).

---

# Tecnologías y Librerías Utilizadas

### En el script de Python:

* **`subprocess`:** Una librería nativa de Python que permite ejecutar comandos del sistema operativo. Se usa para levantar y controlar el proceso de Node.js en segundo plano.
* **`urllib.request`:** Módulo nativo para realizar peticiones de red HTTP. Se utiliza para enviar los textos al endpoint local de Ollama de forma directa y limpia, sin depender de librerías externas como `requests`.
* **`json`:** Para serializar (convertir a texto) y deserializar (convertir a objetos de Python) los mensajes del protocolo JSON-RPC y las respuestas de la IA.
* **`os` y `time`:** Para gestionar rutas de archivos y pausar la ejecución del código de manera controlada (esperar a que el servidor de Node se inicialice correctamente).

### En el servidor MCP (Node.js):

* **`child_process` (módulo `spawn`):** Utilizado en el script de prueba para instanciar el servidor en un entorno controlado.
* **Protocolo JSON-RPC 2.0:** No es una librería, sino un estándar de comunicación basado en texto plano a través de los canales estándar de comunicación del sistema: la entrada estándar (`stdin`) y la salida estándar (`stdout`).

---

# Funcionamiento Paso a Paso del Código

### 1. El apretón de manos (Handshake MCP)

Cuando ejecutas el script de Python, este lanza el comando `node dist/index.cjs`. Como ambos procesos necesitan entenderse, realizan un proceso de inicialización mediante un formato estructurado llamado **JSON-RPC**.
El cliente (Python) envía un mensaje indicando su versión y protocolo (`initialize`), y el servidor responde confirmando sus capacidades.

### 2. Extracción de directrices (`SCHEMA.md`)

El script de Python le solicita al servidor MCP que busque y lea un archivo llamado `SCHEMA.md`. Este archivo contiene las instrucciones de diseño y estructura que la IA debe adoptar de forma obligatoria (por ejemplo: *"Toda nota debe tener un título en mayúsculas, una sección de etiquetas y un resumen de 3 puntos"*).

### 3. Escaneo de la Bandeja de Entrada (`01 - Inbox`)

El script solicita la lista de todos los elementos dentro de la carpeta configurada como Inbox. El servidor MCP consulta CouchDB y devuelve un listado con las notas pendientes de procesar.

### 4. Filtrado de seguridad y prevención de bucles infinitos

El código recorre la lista de notas una por una y realiza dos comprobaciones críticas:

* Ignora las carpetas (rutas que terminan en `/`).
* Lee el contenido de la nota y busca la cadena `"status/propuesta-ia"`. Si la nota ya contiene este texto, **la ignora**. Esto evita que el script procese una nota que ya fue optimizada en una ejecución anterior, previniendo un bucle sin fin de consumo de recursos.

### 5. Compilación con Inteligencia Artificial (Ollama)

Si la nota es válida, se extrae su contenido en bruto y se envía a la API local de Ollama. Se le concatena el contenido del `SCHEMA.md` bajo el rol de `system_prompt` para forzar a la IA a no generar saludos ni introducciones introductorias, devolviendo estrictamente la nota estructurada.

### 6. Inyección de la propuesta en Obsidian

Una vez que Ollama responde con el texto optimizado, Python le ordena al servidor MCP crear un nuevo archivo con el prefijo `propuesta-` dentro de la bandeja de entrada, resguardando la nota original intacta para que el usuario pueda validar el cambio al día siguiente.

---

# Guía para Reproducir el Entorno desde Cero

Sigue estos pasos detallados para montar este sistema en tu propio ordenador:

### Paso 1: Prerrequisitos de Software

Asegúrate de tener instalado lo siguiente en tu sistema:

1. **Python 3.10 o superior.**
2. **Node.js (versión LTS recomendada).**
3. **Ollama:** Descárgalo de su sitio oficial, ejecútalo en tu terminal y descarga el modelo del script corriendo:
```bash
ollama run qwen2.5:14b

```


4. **Instancia de CouchDB:** Ya sea local o en la nube, donde se sincronice tu vault de Obsidian.

### Paso 2: Estructura del Proyecto

Crea una carpeta para el proyecto con la siguiente estructura de archivos:

```text
mi-segundo-cerebro-mcp/
├── .env                  # Credenciales de CouchDB
├── compiler.py           # Código de Python provisto
├── SCHEMA.md             # Instrucciones de formato para la IA
├── dist/
│   └── index.cjs         # Servidor MCP compilado (Node.js)
└── 01 - Inbox/           # Carpeta simulada o vinculada de entrada

```

### Paso 3: Configurar las Variables de Entorno (`.env`)

El archivo `.env` debe estar en la raíz del proyecto Node.js para que el servidor pueda autenticarse contra CouchDB. Crea el archivo e introduce tus datos de acceso:

```env
COUCHDB_URL=http://admin:tu_contraseña_secreta@127.0.0.1:5984
COUCHDB_DB_NAME=tu_base_de_datos_obsidian

```

### Paso 4: Crear el esquema de diseño (`SCHEMA.md`)

Crea un archivo llamado `SCHEMA.md` en la raíz. Este archivo guiará la transformación del contenido. Ejemplo de contenido:

```markdown
# PLANTILLA DE CONOCIMIENTO ATÓMICO
- **Concepto Principal:** [Definición clara en una frase]
- **Categoría:** #conocimiento/[área]
- **Puntos Clave:**
  - 
- **Acciones / Siguientes Pasos:** [Si aplica]

```

### Paso 5: Ejecución y Pruebas

1. Pon una nota de prueba desorganizada en la carpeta `01 - Inbox/nota_rapida.md`.
2. Primero, puedes asegurarte de que el servidor MCP responde al protocolo básico ejecutando el script de test de Node:
```bash
node test-mcp.js

```


*Deberías ver una respuesta en consola que incluya la confirmación del formato JSON-RPC.*
3. Ejecuta el compilador principal en Python:
```bash
python compiler.py

```


4. Revisa tu carpeta `01 - Inbox/`. Verás aparecer un nuevo archivo llamado `propuesta-nota_rapida.md` perfectamente ordenado por la IA local.

---

Para ayudarte a comprender cómo interactúan de manera exacta estos procesos mediante el protocolo de comunicación en segundo plano, he preparado el siguiente simulador interactivo de la arquitectura MCP. Puedes avanzar por las distintas fases de ejecución para observar los mensajes JSON-RPC nativos que se transfieren entre el script y el servidor de base de datos.