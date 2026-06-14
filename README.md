# 🎓 Papoi — Tutor Escolar Acessível por Voz

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

> Projeto final da disciplina de Inteligência Artificial — ADS/IFPB  
> Professor: Rodolfo Bolconte

Papoi é um assistente de tutoria escolar acessível por voz, rodando **100% localmente** via Ollama. O objetivo é permitir que alunos com dificuldade de digitação, leitura, problemas motores ou visuais possam interagir com um tutor através da voz.

**Pipeline:** fala do aluno → STT (Whisper) → LLM (Ollama) → TTS (Piper) → resposta em voz

---

## Autores

| Membro | GitHub |
|--------|--------|
| Luiz Augusto | [@06Augusto-ziuL](https://github.com/06Augusto-ziuL) |
| Arthur Rodrigues | [@Arthxzs](https://github.com/Arthxzs) |
| Maria Eduarda Queiroz | [@dudinha-dev](https://github.com/dudinha-dev) |

---

## Stack

| Camada | Ferramenta |
|--------|-----------|
| LLM | [Ollama](https://ollama.com) + `qwen2.5:3b` |
| STT | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) modelo `base` |
| TTS | [Piper TTS](https://github.com/rhasspy/piper) voz `pt_BR-faber-medium` |
| Interface | [Gradio](https://gradio.app) |

---

## Requisitos

### Hardware mínimo
- CPU: Intel Core i3 de 10ª geração ou equivalente
- RAM: 8GB (12GB recomendado)
- GPU: não necessária — inferência apenas em CPU

### Software
- Python 3.10 ou superior
- [Ollama](https://ollama.com/download)
- [Piper TTS](https://github.com/rhasspy/piper/releases) — executável no PATH do sistema

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/06Augusto-ziuL/voice-tutor-a11y.git
cd voice-tutor-a11y
```

### 2. Ambiente Python

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Linux:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Ollama

**Windows:** baixe o instalador em [ollama.com/download](https://ollama.com/download)

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Após instalar, baixe o modelo:
```bash
ollama pull qwen2.5:3b
```

### 4. Modelo de voz Piper

Baixe os dois arquivos a seguir e coloque em `assets/piper_model/`:

- [`pt_BR-faber-medium.onnx`](https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx)
- [`pt_BR-faber-medium.onnx.json`](https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx.json)

---

## Como rodar

Certifique-se de que o Ollama está em execução, depois:

```bash
python app.py
```

Acesse `http://127.0.0.1:7860` no navegador.

---

## Estrutura do projeto

```
voice-tutor-a11y/
├── app.py                  # entrada principal — interface Gradio
├── requirements.txt
├── assets/
│   └── piper_model/        # modelo de voz (baixar manualmente)
├── core/
│   ├── config.py           # configurações centralizadas
│   ├── llm_client.py       # comunicação com Ollama
│   ├── prompts.py          # system prompt do tutor
│   ├── stt_engine.py       # transcrição de voz (faster-whisper)
│   └── tts_engine.py       # síntese de voz (Piper)
├── ui/
│   ├── styles.py           # CSS e JS da interface
│   └── ui.py               # funções de controle da interface
└── artigo/
    └── artigo_final.pdf
```

---

## Status do projeto

> ⚠️ **Projeto em desenvolvimento ativo** — a interface, os prompts e os módulos estão em modificação constante. A versão atual pode estar instável.

---

## Observações

- O modelo `qwen2.5:3b` requer ~2GB de RAM para inferência
- Os arquivos de áudio gerados (`.wav`) são temporários e não são versionados
- O projeto foi desenvolvido e testado no Windows 11 e Arch Linux (EndeavourOS)