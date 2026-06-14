"""
server.py — Backend FastAPI do Papoi
"""

import os
import shutil
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel

# Importações do core (permanecem funcionais a partir da raiz do projeto)
from core.llm_client import perguntar
from core.tts_engine import sintetizar_voz
from core.stt_engine import transcrever
from core.config import AUDIO_OUTPUT

app = FastAPI(title="Papoi API")

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para cabeçalhos de segurança (necessário para a Web Audio API no navegador)
class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        return response

app.add_middleware(SecureHeadersMiddleware)

# Mapeamento do diretório da Interface (ui/) subindo um nível a partir de server/
BASE_DIR = Path(__file__).resolve().parent.parent
UI_DIR = BASE_DIR / "ui"

# Monta o diretório 'ui' na rota '/ui' para servir o style.css e script.js
app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")

# ── Modelos de Dados Pydantic ─────────────────────────────────────────────────

class MensagemHistorico(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    pergunta: str
    historico: list[MensagemHistorico] = []

class ChatResponse(BaseModel):
    resposta: str
    audio_path: str

class TranscricaoResponse(BaseModel):
    texto: str

# ── Endpoints da API ──────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.pergunta.strip():
        raise HTTPException(status_code=400, detail="Pergunta vazia.")

    # Converte o histórico recebido para o formato aceito pelo llm_client
    historico = [{"role": m.role, "content": m.content} for m in req.historico]
    
    resposta = perguntar(req.pergunta, historico)
    sintetizar_voz(resposta)

    return ChatResponse(resposta=resposta, audio_path="/audio")

@app.post("/transcrever", response_model=TranscricaoResponse)
async def transcrever_audio(arquivo: UploadFile = File(...)):
    suffix = Path(arquivo.filename).suffix if arquivo.filename else ".webm"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(arquivo.file, tmp)
        tmp_path = tmp.name

    tamanho = Path(tmp_path).stat().st_size

    if tamanho < 500:
        os.unlink(tmp_path)
        raise HTTPException(status_code=400, detail="Áudio muito curto ou vazio.")

    try:
        texto = transcrever(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na transcrição: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return TranscricaoResponse(texto=texto)

@app.get("/audio")
async def servir_audio():
    audio_path = Path(AUDIO_OUTPUT)
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Nenhum áudio disponível.")
    return FileResponse(
        path=str(audio_path),
        media_type="audio/wav",
        headers={"Cache-Control": "no-store"},
    )

@app.get("/", response_class=HTMLResponse)
async def raiz():
    html_path = UI_DIR / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<p>index.html não encontrado na pasta ui/.</p>", status_code=404)