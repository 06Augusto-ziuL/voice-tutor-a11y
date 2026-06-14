# 🎓 Papoi — Tutor Escolar Acessível por Voz

![Status](https://img.shields.io/badge/status-concluído-green)
![License](https://img.shields.io/badge/license-MIT-blue)

> Projeto final da disciplina de Inteligência Artificial — ADS/IFPB
> Professor: Rodolfo Bolconte

Papoi é um assistente de tutoria escolar acessível por voz, desenvolvido para permitir que alunos com dificuldades de digitação, leitura, problemas motores ou visuais possam interagir com um tutor por meio da fala. O sistema opera completamente offline via Ollama, com uma interface web servida por FastAPI.

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
| LLM | [Ollama](https://ollama.com) + `papoi_q4:latest` (gemma3:4b fine-tuned, Q4_K_M) |
| STT | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) modelo `small` |
| TTS | [Piper TTS](https://github.com/rhasspy/piper) voz `pt_BR-faber-medium` |
| Servidor | [FastAPI](https://fastapi.tiangolo.com) + Uvicorn |
| Interface | HTML/CSS/JS estático servido pelo FastAPI |

---

## Requisitos

### Hardware mínimo
- CPU: Intel Core i3 de 10ª geração ou equivalente
- RAM: 8 GB (12 GB recomendado)
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
```powershell
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

Após instalar, importe o modelo fine-tuned a partir do Hugging Face ou localmente via Modelfile (veja a seção [Modelo Fine-tuned](#modelo-fine-tuned)).

### 4. Modelo de voz Piper

Baixe os dois arquivos a seguir e coloque em `assets/piper_model/`:

- [`pt_BR-faber-medium.onnx`](https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx)
- [`pt_BR-faber-medium.onnx.json`](https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx.json)

---

## Modelo Fine-tuned

O modelo utilizado em produção é o `papoi_q4:latest` — uma versão fine-tuned do `google/gemma-3-4b-it` via QLoRA (4-bit), treinada sobre um dataset sintético de 400 exemplos em formato Alpaca, cobrindo seis categorias: Matemática, Ciências, Português, História/Geografia, Programação e redirecionamento fora do escopo.

Os artefatos estão disponíveis publicamente no Hugging Face:

**[Mugit/papoi-gemma3-4b-ft](https://huggingface.co/Mugit/papoi-gemma3-4b-ft)**

| Arquivo | Tamanho | Descrição |
|---------|---------|-----------|
| `model-f16.gguf` | ~7.2 GB | Precisão FP16 — requer GPU para inferência viável |
| `model-q4_k_m.gguf` | ~3.5 GB | Quantização Q4_K_M — recomendado para CPU |

### Importar via Modelfile

Baixe o `model-q4_k_m.gguf` do Hugging Face e crie um `Modelfile` na mesma pasta:

```
FROM ./model-q4_k_m.gguf

PARAMETER temperature 0.7
PARAMETER num_predict 500
```

Em seguida, registre no Ollama:

```bash
ollama create papoi_q4 -f Modelfile
```

> **Atenção (Windows):** O Ollama no Windows cria um ponteiro simbólico para o arquivo `.gguf`. Não mova nem exclua o arquivo após executar `ollama create`, ou o modelo quebrará.

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
├── app.py                  # entrada principal (Uvicorn/FastAPI)
├── requirements.txt
├── assets/
│   ├── output.wav          # áudio gerado pelo TTS (não versionado)
│   └── piper_model/        # modelo de voz (baixar manualmente)
│       ├── pt_BR-faber-medium.onnx
│       └── pt_BR-faber-medium.onnx.json
├── core/
│   ├── config.py           # configurações centralizadas
│   ├── llm_client.py       # comunicação com Ollama
│   ├── prompts.py          # system prompt do tutor
│   ├── stt_engine.py       # transcrição de voz (faster-whisper)
│   └── tts_engine.py       # síntese de voz (Piper)
├── server/
│   └── server.py           # rotas FastAPI (chat, transcrever, audio)
├── tests/
│   ├── .env                # chaves de API (não versionado)
│   ├── requirements-test.txt
│   └── test_runner.py      # runner de avaliação comparativa
├── ui/
│   ├── index.html
│   ├── script.js
│   └── style.css
└── artigo/
```

---

## Metodologia de avaliação

O projeto conduziu cinco fases de avaliação sistemática, aplicando um banco fixo de 10 perguntas (P01–P10) cobrindo Matemática, Ciências, Português, Programação e redirecionamento fora do escopo. As respostas foram avaliadas por rubrica com quatro critérios (clareza, adequação pedagógica, brevidade, acessibilidade linguística), escala 1–5.

### Resultados por fase

**Fase 1 — Exploração local com prompt v1.0** (E01–E09)

Três modelos testados em três temperaturas cada:

| Modelo | Melhor temperatura | Média geral |
|--------|--------------------|-------------|
| qwen2.5:3b | 0.7 | 3.13 |
| gemma3:4b | 0.2 | 2.90 |
| llama3.2:3b | 0.7 | 2.78 |

Principal limitação identificada: MAX_TOKENS = 300 insuficiente para perguntas matemáticas; redirecionamento fora do escopo com conformidade de apenas 5,6%.

**Fase 2 — Prompt v1.1 + novos modelos** (E10–E14)

Prompt refinado com instrução explícita anti-markdown e redirecionamento reforçado. MAX_TOKENS elevado para 500. Dois novos candidatos avaliados (phi3.5, granite3-dense:2b) e eliminados por latência e imprecisão factual.

| Modelo | Média geral |
|--------|-------------|
| gemma3:4b (E11b) | 3.35 |
| qwen2.5:3b | 2.85 |
| granite3-dense:2b | 2.60 |
| llama3.2:3b | 2.53 |
| phi3.5 | 2.20 |

**Modelo local vencedor: gemma3:4b @ temperatura 0.2, MAX_TOKENS = 500.**

**Fase 3 — Local vs APIs gratuitas** (E15–E17)

| Modelo | Provedor | Média geral | Latência média |
|--------|----------|-------------|----------------|
| llama-3.3-70b-versatile | Groq | 4.05 | 1.19s |
| gemini-2.5-flash | Google | 3.55* | 3.56s |
| gemma3:4b | Ollama (local) | 3.10 | 32.33s |

*Média calculada apenas sobre respostas não truncadas (6/8 perguntas foram cortadas por incompatibilidade de brevidade com o pipeline TTS).

**Fase 4 — Modelos comerciais via interfaces web** (E18–E20)

Avaliação manual com prompt v1.1 injetado como primeira mensagem (sem acesso ao campo `system` no tier gratuito).

| Modelo | Plataforma | Média geral (P01–P08) | P09 | P10 |
|--------|------------|----------------------|-----|-----|
| Claude Sonnet 4.6 | claude.ai | 4.53 | ✅ | ✅ |
| ChatGPT GPT-5.5 | chatgpt.com | 4.03 | ✅ | ❌ |
| Gemini Flash 3.5 | gemini.google.com | 3.84 | ✅ | ✅ |

**Fase 5 — Fine-tuned vs baseline** (E21–E24)

O modelo `papoi_f16:latest` (FP16, 7.2 GB) apresentou timeout sistemático em CPU — inviável no hardware alvo. O modelo `papoi_q4:latest` (Q4_K_M, 3.5 GB) foi estável nas duas temperaturas testadas:

| Execução | Modelo | Temperatura | Média geral | Latência média |
|----------|--------|-------------|-------------|----------------|
| E22 | papoi_q4 | 0.2 | 3.18 | 37.8s |
| E24 | papoi_q4 | 0.7 | 3.23 | 31.4s |

Principais ganhos do fine-tuning em relação ao baseline (gemma3:4b E11b, média 3.35):

- Markdown completamente eliminado (0% de violações vs ~80% no baseline) — impacto direto na qualidade do TTS
- Redirecionamento P09 funcional (5.00 em E22; 4.75 em E24)
- P01 (frações) com processo completo e correto nas duas execuções (4.50 vs 3.75 no baseline E15)
- Temperatura 0.7 produziu latência média menor que 0.2 (31.4s vs 37.8s), sugerindo otimização do modelo para estilo mais conversacional

Falha persistente: P10 (futebol) não foi redirecionada em nenhuma execução — limitação estrutural de modelos locais abaixo de ~7B parâmetros, não atribuível ao fine-tuning.

**Configuração final adotada: `papoi_q4:latest` @ temperatura 0.7.**

---

## Observações técnicas

- O modelo `papoi_q4:latest` requer ~3.5 GB de RAM para inferência ativa
- Inferência em CPU satura o processador (~90% de uso médio) — comportamento esperado e documentado
- Os arquivos de áudio gerados (`.wav`) são temporários e não são versionados
- O projeto foi desenvolvido e testado no Windows 11 e Arch Linux (EndeavourOS)
- APIs externas (Groq, Google AI) foram utilizadas apenas na fase de avaliação comparativa e não integram o pipeline de produção

---

## Observações

![Status](https://img.shields.io/badge/status-concluído-green)

> Este projeto foi desenvolvido como trabalho final acadêmico. O pipeline local está funcional e testado. A integração STT permanece como componente externo desenvolvido por membro separado do trio.
