# 🎓 TutorIA — Asistente Educativo con Voz + RAG + Llama 3.1 (Open Source)

![TutorIA Banner](https://user-images.githubusercontent.com/0000000/tutoria-banner.png)

**TutorIA** es un asistente inteligente en español que responde **con voz y texto**, utilizando modelos **open-source** completamente locales.  
No depende de servicios en la nube ni APIs de pago.

> 🧠 *“Aprende, explica y enseña como un tutor humano, pero desde tu computadora.”*

---

## 🚀 Características principales

✅ 100 % **local y privado** — sin conexión a Internet ni servicios externos  
✅ **Responde en español**, con voz natural (TTS)  
✅ **RAG**: Recupera información desde tus propios documentos  
✅ **Modelo Llama 3.1 (8B)** ejecutándose en **Ollama**  
✅ **Frontend web** con entrada y salida por voz  
✅ Compatible con **Windows, Linux y macOS**

---

## 🧰 Tecnologías usadas

| Componente | Descripción | Herramienta |
|-------------|--------------|-------------|
| 🐍 Backend API | Servidor principal | **FastAPI + Uvicorn** |
| 🤖 LLM | Modelo de lenguaje local | **Llama 3.1 (8B)** via **Ollama** |
| 🔎 RAG | Búsqueda semántica contextual | **SentenceTransformers (MiniLM)** |
| 🔊 TTS | Voz en español | **espeak-ng** |
| 🌐 Frontend | Interfaz web voz↔voz | **HTML + JavaScript (Web Speech API)** |
| 🐳 Contenedores | Orquestación y aislamiento | **Docker + Docker Compose** |
| 🪟 OS | Entorno de ejecución | **Windows 11 / Linux / macOS** |

---

## 📦 Requisitos previos

Antes de empezar, asegúrate de tener instalado:

1. **Docker Desktop**  
   👉 [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

2. **Git**  
   👉 [https://git-scm.com/downloads](https://git-scm.com/downloads)

3. (Opcional) **PowerShell 7+** para Windows.

---

## 🪜 Instalación paso a paso

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/<TU_USUARIO>/TutorIA.git
cd TutorIA
```

---

### 2️⃣ Estructura del proyecto

```
TutorIA/
 ├─ app/                → Código principal (FastAPI, RAG, TTS)
 ├─ data/               → Documentos para búsqueda local
 ├─ web/                → Interfaz cliente (HTML + JS)
 ├─ Dockerfile          → Imagen del backend
 ├─ docker-compose.yml  → Orquestación de contenedores
 ├─ requirements.txt    → Dependencias de Python
 ├─ .env                → Variables de entorno
 ├─ .gitignore
 └─ README.md
```

---

### 3️⃣ Configurar variables de entorno

Crea el archivo `.env` en la raíz del proyecto:

```env
# Puerto del servidor API
PORT=8000

# Dirección del contenedor Ollama
OLLAMA_URL=http://ollama:11434

# Modelo LLM (descargado automáticamente)
MODEL_NAME=llama3.1

# Lenguaje del TTS
VOICE_LANG=es
```

---

### 4️⃣ Construir y ejecutar con Docker

```bash
docker compose up --build -d
```

Esto levanta:
- 🧠 **ollama** → modelo Llama 3.1  
- 🎙 **tutor-ia** → API FastAPI (RAG + TTS)

Verifica que ambos contenedores estén activos:
```bash
docker compose ps
```

---

### 5️⃣ Descargar el modelo Llama 3.1

Una sola vez:

```bash
docker exec -it ollama ollama pull llama3.1
```

---

### 6️⃣ Verificar el servicio

Prueba el endpoint de salud:
```bash
Invoke-WebRequest http://localhost:8000/health
```
Debería responder:
```json
{"status":"ok"}
```

---

## 🗣️ Prueba de funcionamiento

### Opción 1 – Desde PowerShell
```powershell
$body = @{ question = "¿Qué es la energía solar?"; voice_mode = $true } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/ask" -Method Post -ContentType "application/json; charset=utf-8" -Body $body
```

### Opción 2 – Desde el navegador
Abre el archivo:
```
web/index.html
```
Y presiona el botón 🎤 **“Hablar”**.  
El tutor escuchará tu voz, pensará y responderá **hablando en español**.

---

## 🧩 Arquitectura del sistema

```
┌────────────────────┐
│  Navegador (web)   │  ← Voz/Texto del usuario
└────────┬───────────┘
         │
         ▼
┌────────────────────────────┐
│   FastAPI (tutor-ia)       │
│ - Procesa preguntas         │
│ - Ejecuta RAG               │
│ - Envía prompt a Ollama     │
│ - Genera voz (espeak-ng)    │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│   Ollama + Llama 3.1 (8B)  │
│   Modelo local de lenguaje  │
└────────────────────────────┘
```

---

## 🧠 Agregar tus propios documentos (RAG)

Coloca tus archivos `.txt`, `.pdf` o `.md` en la carpeta `data/`.

Luego reinicia el contenedor del backend:
```bash
docker compose restart tutor-ia
```

El sistema indexará automáticamente tus documentos para usarlos como contexto.

---

## 🐞 Solución de problemas comunes

| Problema | Causa | Solución |
|-----------|--------|----------|
| ❌ *“There was an error parsing the body”* | JSON mal formateado | Usa `ConvertTo-Json` en PowerShell |
| 💤 *Demora en responder* | CPU sin GPU | Es normal, usa `llama3.1:8b-instruct` o `phi3` para más rapidez |
| ⚠️ *Caracteres raros (Ã³, Ã¡)* | Consola sin UTF-8 | Ejecuta `chcp 65001` en PowerShell |
| 🔇 *No hay voz* | Navegador bloquea audio | Permite micrófono y altavoz en el navegador |

---
# 1️⃣ LEVANTAR OLLAMA CON GPU
docker run -d --gpus all --name ollama -p 11434:11434 ollama/ollama:latest

# Cargar modelo
docker exec -it ollama ollama pull llama3.1

# 2️⃣ LEVANTAR BACKEND TUTORIA
cd TutorIA
docker build -t tutoria .
docker run -d --name tutor-ia -p 8000:8000 --env-file .env --link ollama:tutoria-ollama tutoria
---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas!  
Puedes abrir un **issue** o enviar un **pull request** con mejoras, nuevos modelos o voces.

---

## 🧑‍💻 Autor

**EVER DEV**  
Desarrollador de soluciones educativas con IA  
💬 [LinkedIn](linkedin.com/in/lino-ever-ramos-maiz-950578387) 

---

## 📜 Licencia

Este proyecto está bajo la licencia **MIT**.  
Puedes usarlo, modificarlo y compartirlo libremente.

---

## 🌟 Agradecimientos

- [Ollama](https://ollama.com/) — por hacer accesibles los modelos LLM locales  
- [FastAPI](https://fastapi.tiangolo.com/) — backend rápido y moderno  
- [SentenceTransformers](https://www.sbert.net/) — embeddings potentes y ligeros  
- [espeak-ng](https://github.com/espeak-ng/espeak-ng) — voz libre en español

---

> ✨ *“TutorIA: tu profesor personal, local y libre.”*
