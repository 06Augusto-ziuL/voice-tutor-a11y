import requests
import json
from core.config import OLLAMA_MODEL, OLLAMA_URL, OLLAMA_TEMPERATURE
from core.prompts import TUTOR_SYSTEM_PROMPT

def perguntar(pergunta: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "system": TUTOR_SYSTEM_PROMPT,
        "prompt": pergunta,
        "temperature": OLLAMA_TEMPERATURE,
        "stream": False
    }

    try:
        resposta = requests.post(OLLAMA_URL, json=payload)
        resposta.raise_for_status()
        dados = resposta.json()
        return dados["response"]
    except requests.exceptions.ConnectionError:
        return "Erro: não foi possível conectar ao Ollama. Verifique se o serviço está funcionando corretamente."
    except requests.exceptions.HTTPError as e:
        return f"Erro na requisição: {e}"
    except KeyError:
        return "Erro: resposta inesperada do Ollama."