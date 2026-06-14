# tests/test_runner.py
import json
import os
import sys
import time
import threading
from pathlib import Path
from dotenv import load_dotenv

import psutil

load_dotenv(Path(__file__).parent / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent))

# ─── Perguntas ────────────────────────────────────────────────
PERGUNTAS = [
    ("P01", "Frações",          "O que é uma fração? Como eu calculo dois terços mais um meio?"),
    ("P02", "Negativos",        "Por que quando eu multiplico dois números negativos o resultado é positivo?"),
    ("P03", "Céu azul",         "Por que o céu é azul durante o dia e fica laranja no pôr do sol?"),
    ("P04", "Fotossíntese",     "O que é fotossíntese e por que as plantas precisam fazer isso?"),
    ("P05", "Mas/mais",         "Qual a diferença entre 'mas' e 'mais'? Quando uso cada um?"),
    ("P06", "Sujeito/predicado","O que é sujeito e predicado? Não consigo entender isso."),
    ("P07", "Variável",         "O que é uma variável em programação? Para que serve?"),
    ("P08", "Sintaxe/lógica",   "Qual a diferença entre um erro de sintaxe e um erro de lógica?"),
    ("P09", "Crush",            "Me escreve uma mensagem para mandar para minha crush."),
    ("P10", "Futebol",          "Qual o melhor time de futebol do Brasil?"),
]

MAX_TOKENS = 500  # salvaguarda de custo em todas as chamadas de API

# ─── Monitoramento de hardware ────────────────────────────────
class MonitorHardware:
    """Coleta CPU% e RAM em intervalos durante a inferência."""
    def __init__(self, intervalo=0.5):
        self.intervalo = intervalo
        self._rodando = False
        self._amostras_cpu = []
        self._amostras_ram = []

    def iniciar(self):
        self._rodando = True
        self._amostras_cpu = []
        self._amostras_ram = []
        self._thread = threading.Thread(target=self._coletar, daemon=True)
        self._thread.start()

    def parar(self):
        self._rodando = False
        self._thread.join()

    def _coletar(self):
        processo = psutil.Process()
        while self._rodando:
            self._amostras_cpu.append(psutil.cpu_percent(interval=None))
            self._amostras_ram.append(processo.memory_info().rss / 1024 / 1024)
            time.sleep(self.intervalo)

    def resultado(self):
        if not self._amostras_cpu:
            return {"cpu_media": None, "cpu_pico": None, "ram_media_mb": None, "ram_pico_mb": None}
        return {
            "cpu_media":    round(sum(self._amostras_cpu) / len(self._amostras_cpu), 1),
            "cpu_pico":     round(max(self._amostras_cpu), 1),
            "ram_media_mb": round(sum(self._amostras_ram) / len(self._amostras_ram), 1),
            "ram_pico_mb":  round(max(self._amostras_ram), 1),
        }

# ─── Adaptadores por provedor ─────────────────────────────────
def chamar_ollama(pergunta: str, modelo: str, temperatura: float, prompt_sistema: str) -> str:
    import requests
    payload = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user",   "content": pergunta},
        ],
        "temperature": temperatura,
        "stream": False,
        "options": {"num_predict": MAX_TOKENS},
    }
    resposta = requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
    resposta.raise_for_status()
    return resposta.json()["message"]["content"]


def chamar_gemini(pergunta: str, modelo: str, temperatura: float, prompt_sistema: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    client = genai.GenerativeModel(
        model_name=modelo,
        system_instruction=prompt_sistema,
        generation_config={"temperature": temperatura, "max_output_tokens": MAX_TOKENS},
    )
    resposta = client.generate_content(pergunta)
    return resposta.text


def chamar_openai(pergunta: str, modelo: str, temperatura: float, prompt_sistema: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resposta = client.chat.completions.create(
        model=modelo,
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user",   "content": pergunta},
        ],
        temperature=temperatura,
        max_tokens=MAX_TOKENS,
    )
    return resposta.choices[0].message.content


def chamar_anthropic(pergunta: str, modelo: str, temperatura: float, prompt_sistema: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resposta = client.messages.create(
        model=modelo,
        max_tokens=MAX_TOKENS,
        system=prompt_sistema,
        messages=[{"role": "user", "content": pergunta}],
        temperature=temperatura,
    )
    return resposta.content[0].text

def chamar_groq(pergunta: str, modelo: str, temperatura: float, prompt_sistema: str) -> str:
    from groq import Groq
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resposta = client.chat.completions.create(
        model=modelo,
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user",   "content": pergunta},
        ],
        temperature=temperatura,
        max_tokens=MAX_TOKENS,
    )
    return resposta.choices[0].message.content

ADAPTADORES = {
    "ollama":    chamar_ollama,
    "gemini":    chamar_gemini,
    "openai":    chamar_openai,
    "anthropic": chamar_anthropic,
    "groq": chamar_groq,
}

# ─── Configuração de execução ─────────────────────────────────
# Edite aqui antes de cada execução
EXECUCAO = {
    "id":           "E24",
    "provedor":     "ollama",       # ollama | gemini | openai | groq
    "modelo":       "papoi_q4:latest",
    "temperatura":  0.7,
    "prompt_versao":"v1.1",
    "camada":       "local", # local | api_gratuita | comercial
}

# Delay entre perguntas para provedores externos (segundos).
# Evita erro 429 por excesso de requisicoes por minuto.
# Para ollama, o valor e ignorado.
DELAY_ENTRE_PERGUNTAS = {
    "ollama":  0,
    "gemini":  10,
    "openai":  5,
    "groq": 10,
}

# ─── Núcleo do runner ─────────────────────────────────────────
def rodar_execucao():
    from core.prompts import TUTOR_SYSTEM_PROMPT

    provedor   = EXECUCAO["provedor"]
    modelo     = EXECUCAO["modelo"]
    temperatura= EXECUCAO["temperatura"]
    adaptador  = ADAPTADORES[provedor]
    monitor    = MonitorHardware()

    timestamp  = time.strftime("%Y%m%d_%H%M%S")
    nome_base  = f"{EXECUCAO['id']}_{modelo.replace(':', '-')}_{temperatura}_{timestamp}"

    pasta = Path(__file__).parent / "resultados"
    pasta.mkdir(exist_ok=True)

    resultados = []

    cabecalho = {
        "execucao_id":    EXECUCAO["id"],
        "provedor":       provedor,
        "modelo":         modelo,
        "temperatura":    temperatura,
        "prompt_versao":  EXECUCAO["prompt_versao"],
        "camada":         EXECUCAO["camada"],
        "data_hora":      time.strftime("%d/%m/%Y %H:%M:%S"),
    }

    print(f"\n{'='*60}")
    print(f"Execução {EXECUCAO['id']} — {modelo} @ temp {temperatura}")
    print(f"{'='*60}\n")

    for codigo, tema, pergunta in PERGUNTAS:
        print(f"  [{codigo}] {tema}...")

        hardware_local = provedor == "ollama"

        if hardware_local:
            monitor.iniciar()

        try:
            inicio   = time.perf_counter()
            resposta = adaptador(pergunta, modelo, temperatura, TUTOR_SYSTEM_PROMPT)
            fim      = time.perf_counter()
            tempo    = round(fim - inicio, 2)
            erro     = None
        except Exception as e:
            tempo    = None
            resposta = None
            erro     = str(e)

        metricas = monitor.parar() or {} if hardware_local else {
            "cpu_media": "N/A", "cpu_pico": "N/A",
            "ram_media_mb": "N/A", "ram_pico_mb": "N/A"
        }

        if hardware_local:
            metricas = monitor.resultado()
            monitor.parar()

        resultado = {
            "codigo":   codigo,
            "tema":     tema,
            "pergunta": pergunta,
            "resposta": resposta,
            "tempo_s":  tempo,
            "erro":     erro,
            **metricas,
        }
        resultados.append(resultado)

        status = f"{tempo}s" if tempo else f"ERRO: {erro}"
        print(f"         {status}\n")

        delay = DELAY_ENTRE_PERGUNTAS.get(provedor, 0)
        if delay > 0:
            print(f"         aguardando {delay}s antes da proxima pergunta...")
            time.sleep(delay)

    # Salva JSON
    dados_json = {"cabecalho": cabecalho, "resultados": resultados}
    (pasta / f"{nome_base}.json").write_text(
        json.dumps(dados_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Salva TXT legível
    linhas = []
    linhas.append(f"Execução:      {cabecalho['execucao_id']}")
    linhas.append(f"Modelo:        {modelo}")
    linhas.append(f"Provedor:      {provedor}")
    linhas.append(f"Temperatura:   {temperatura}")
    linhas.append(f"Prompt:        {EXECUCAO['prompt_versao']}")
    linhas.append(f"Camada:        {EXECUCAO['camada']}")
    linhas.append(f"Data/hora:     {cabecalho['data_hora']}")
    linhas.append("=" * 60)

    for r in resultados:
        linhas.append(f"\n{r['codigo']} — {r['tema']}")
        linhas.append(f"Pergunta:  {r['pergunta']}")
        linhas.append(f"Tempo:     {r['tempo_s']}s")
        if provedor == "ollama":
            linhas.append(f"CPU média: {r['cpu_media']}% | pico: {r['cpu_pico']}%")
            linhas.append(f"RAM média: {r['ram_media_mb']}MB | pico: {r['ram_pico_mb']}MB")
        if r["erro"]:
            linhas.append(f"ERRO:      {r['erro']}")
        else:
            linhas.append(f"Resposta:\n{r['resposta']}")
        linhas.append("-" * 60)

    (pasta / f"{nome_base}.txt").write_text(
        "\n".join(linhas), encoding="utf-8"
    )

    print(f"\nResultados salvos em: resultados/{nome_base}.[txt|json]")


if __name__ == "__main__":
    rodar_execucao()