import os, base64, tempfile, subprocess
from typing import Optional, List
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app.rag import SimpleRAG

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

app = FastAPI(title="PROMPT MAESTRO — (Open-Source) Tutor IA con Voz + RAG + LLM")

# CORS: permite llamadas desde el navegador (file://, localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_rag = None
def get_rag() -> SimpleRAG:
    global _rag
    if _rag is None:
        _rag = SimpleRAG(data_dir="/app/data", embedding_model=EMBEDDING_MODEL)
    return _rag

class AskIn(BaseModel):
    question: str
    voice_mode: Optional[bool] = True
    k: Optional[int] = 3

class AskOut(BaseModel):
    answer_short: str
    explanation: str
    based_on: Optional[str] = None
    audio_base64: Optional[str] = None
    date: Optional[str] = None

@app.get("/health")
def health():
    return {"status": "ok"}

def synthesize_tts(text: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name
    subprocess.run(["espeak-ng", "-v", "es", "-s", "170", "-w", wav_path, text], check=True)
    with open(wav_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def build_prompt(question: str, context_chunks: List[str]) -> str:
    context_block = "\n\n".join([f"[Fragmento {i+1}]\n{c}" for i, c in enumerate(context_chunks)])
    rules = (
        "Eres un tutor en español. Responde breve, claro y natural.\n"
        "Usa primero el contexto; si no alcanza, dilo y complementa con conocimiento general.\n"
        "Evita frases muy largas (TTS).\n"
        "Estructura: Respuesta corta / Explicación / Basado en.\n"
        "No inventes datos ni especules.\n"
    )
    return f"{rules}\n---\nPregunta: {question}\n\nContexto:\n{context_block}"

def call_ollama(prompt: str) -> str:
    import requests
    url = f"{OLLAMA_HOST}/api/chat"
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": "Eres un tutor experto y conciso en español."},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {"temperature": 0.2}
    }
    r = requests.post(url, json=payload, timeout=600)
    r.raise_for_status()
    data = r.json()
    return data.get("message", {}).get("content", "").strip()

@app.post("/ask", response_model=AskOut)
def ask(payload: AskIn):
    rag = get_rag()
    retrieved = rag.retrieve(payload.question, k=payload.k)
    context_chunks = [t for t, _ in retrieved]
    prompt = build_prompt(payload.question, context_chunks)

    answer = call_ollama(prompt)

    based_on = "Documentos locales del RAG" if context_chunks else \
               "No hay contexto local suficiente; se respondió de forma general."

    audio_b64 = synthesize_tts(answer) if payload.voice_mode else None

    first_line = answer.split("\n")[0][:240]
    rest = "\n".join(answer.split("\n")[1:])[:1200]

    return AskOut(
        answer_short=first_line,
        explanation=rest,
        based_on=based_on,
        audio_base64=audio_b64,
        date="UTC"
    )
